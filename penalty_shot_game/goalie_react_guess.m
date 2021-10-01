% goalie_react_guess.m
% 
% This class contains the functions related to the goalie's "guess"
% and "react" strategies, since many of their methods overlap.
%
% React: the goalie attempts to track the ball the entire time. In
% this case, learnToggle must be false and guessProbVector only
% contains the element 'react'.
% 
% Guess: the goalie tracks the ball for as long as feasible
% (similar to the "react" strategy) and then makes a guess right
% before the ball reaches the critical points, in an attempt to
% predict which direction the ball will go before it's too late for
% the goalie to catch up to them. It is specified at initialization
% whether this is an "educated guess", with the goalie learning over
% time against the subject, or a "naive guess", with each possibility
% given an equal probability and no learning.

classdef goalie_react_guess
    properties
        % This variable is a true/false toggle, set at initialization that
        % determines whether the goalie will learn or not. If true,
        % the goalie will update its guessProbVector on each trial,
        % depending on what choice the ball made. If false, it will
        % stay constant (and so the probability of each guess will
        % never change). If this is the react goalie, learnToggle
        % is always false.
        learnToggle
        
        % The vector of possible guesses. To make this simple, we change the
        % probability of each guess by adding that guess multiple
        % times to this vector. Then, at guess-time, we simply pick
        % one element from the vector at random; a guess that has been
        % added more times will have a higher probability of being
        % chosen. If learnToggle is set to false, this vector will
        % contain one of each guess possibility and will never
        % change. If this is the "guess" goalie, the elements of
        % guessProbVector are: react (continue tracking), ^^ (up-up),
        % ^v (up-down), v^ (down-up), and vv (down-down). If it's the
        % "react" goalie, it only has one element: react.
        guessProbVector
        
        % These are the critical points, those points where the goalie could
        % not catch up to the ball if they simply pressed their
        % joystick in one direction and continued to the end of the
        % screen. These are calculated once, at initialization, based
        % on the screen settings, and are assumed to be constant for a
        % given goalie. The calculations are also made under the
        % assumptions that the goalie and ball are both in the center
        % of the screen and have no vertical motion when this is made
        % (equivalently: switch directions at the critical
        % point). This is obviously not true during play-time, but are
        % not terrible simplifications to make.
        critPts
        
        % The x positions when the goalie needs to actually enact its
        % guess. The first value corresponds to the first guess and
        % the second value corresponds to the point when the goalie
        % should change directions if its guess had two components.
        InflectionPts
        
        % These are the other variables associated with calculating the
        % critical points. We hold onto them in case they are needed
        % for future reference.
        barMoveRange
        ballMoveRange
        ballX
        
        % the minimum value of the goalie's "reaction time". On a
        % given trial, we add this to .1 times an observation from
        % LagDist to determine the lag on this particular trial
        LagMinValue
        
        % the distribution we use to vary the goalie's lag from trial-to-trial
        LagDist
        
        % The lag on a given trial. Set by calling trial_start.
        LagThisTrial
        
        % the guess chosen on this trial. Unset (ie, equal to 0) before the
        % ball reaches the first of the inflection points.
        GuessThisTrial
        
        % Store the screen max Y, because if the ball is too close to it we
        % don't want to guess it's going towards it.
        ScreenMaxY
    end
    
    methods
        function obj = goalie_react_guess(strategy,learnToggle,priorStrength,LagMinValue,LagDist,Settings)
        % Initialize the goalie, setting its strategy and learnToggle, and
        % initializing its guessProbVector. 
        % 
        % If strategy is 'react', then learnToggle must be false,
        % priorStrength is disregarded, and guessProbVector only
        % contains one element: react.
        % 
        % If strategy is 'guess', then learnToggle can be true or
        % false, and priorStrength is the approximate strength of the
        % goalie's prior that all possibilities have equal
        % probability: its the number of times we repeat each
        % possibility in the initial guessProbVector (so larger number
        % means more resistant to observations). This only makes sense
        % if learnToggle is true, so if it's false, we set it to 1 and
        % print a Warning if priorStrength>1.
            switch strategy
              case 'react'
                if learnToggle
                    warning('With strategy react, no learning is possible')
                end
                learnToggle = false;
                guessElements = {'react'};
              case 'guess'
                % It doesn't start with the "stutter-steps" (v^, ^v) as possible
                % moves, but it can learn them.
                guessElements = {'react','^^','vv'}; 
                % guessElements = {'^^'};
              otherwise
                error('Don''t know how to do strategy %s!',strategy)
            end
            obj.learnToggle = learnToggle;
            assert(floor(priorStrength)==priorStrength,'priorStrength must be an integer!');
            assert(priorStrength>=1,'Cannot have a prior of negative or zero strength!');
            if ~learnToggle
                if priorStrength>1
                    warning('With learnToggle false, priorStrength is unused (equivalent to priorStrength=1)');
                end
                priorStrength = 1;
            end
            obj.guessProbVector = repmat(guessElements,1,priorStrength);
            obj.LagMinValue = LagMinValue;
            obj.LagDist = LagDist;
            [obj.critPts,obj.barMoveRange,obj.ballMoveRange,obj.ballX,obj.InflectionPts] = obj.calculate_crit_pts(Settings);
            obj.GuessThisTrial = 0;
            obj.ScreenMaxY = Settings.ScreenRect(4);
        end
        
        function obj = trial_start(obj, prevBallX, prevBallY)
        % This function is called at the beginning of every trial and sets the
        % pre-trial settings: the lag on this particular trial and the
        % update of the last trial. We only learn from the last trial
        % if prevBallY is passed and obj.learnToggle = true.
        % 
        % prevBallX, optional. is the history of ball Y positions from
        % the previous trial (Results(trial-1).BallPositions(1,:)),
        % which we use to update the probabilities if we're learning.
        % 
        % prevBallY, optional. is the history of ball Y positions from
        % the previous trial (Results(trial-1).BallPositions(2,:)),
        % which we use to update the probabilities if we're learning.

           % This generates a random number and adds it to the lag, so that we in
           % effect jitter the computer's reaction time on every trial. The
           % distribution it is pulled from is stored in Settings, as is
           % the minimum value.            
            obj.LagThisTrial = obj.LagMinValue + .1 * obj.LagDist.random();
            
            % At the beginning of each trial, we reset the guess value.
            obj.GuessThisTrial = 0;
            
            % prevBallY and prevBallX are optional; if they're not passed, then we
            % don't learn.
            if obj.learnToggle && nargin > 1
                % We only consider those y values within the
                % critical points, since our guess is attempting to
                % predict the behavior during those points, not
                % over the whole trial. We use ismemberf because
                % sometimes, due to rounding errors, they'll be off
                % by a smalla mount.
                prevBallY = prevBallY(ismemberf(prevBallX, obj.critPts));
                % directions then contains -1, 0, and 1, specifying the direction the
                % ball was moving.
                directions = sign(diff(prevBallY,1));
                % We remove all 0s because we only care about when the ball is
                % changing its y position, not moving directly
                % forward.
                directions = directions(directions~=0);
                
                % For this, note that we only check the beginning and the end. We
                % don't care how many times they shifted directions,
                % only what the end result was.
                if isempty(directions)
                    % If they never shifted directions in the critical zone, call it
                    % react.
                    obj.guessProbVector{end+1} = 'react';
                elseif directions(1) == directions(end)
                    % Then they left the critical zone the same direction they entered it
                    % (or continued in the same direction once they
                    % started) and so we consider this either vv or
                    % ^^. Since directions(1) and directions(end) are
                    % equal, we only need to check one to determine
                    % which direction they went
                    if directions(1) == 1
                        obj.guessProbVector{end+1} = '^^';
                    elseif directions(1) == -1
                        obj.guessProbVector{end+1} = 'vv';
                    end
                elseif directions(1) ~= directions(end)
                    % Then they switched directions and so we check
                    % to see whether they went up-down or
                    % down-up. Note that, we know the value of
                    % directions(end) by checking directions(1)
                    % (since there are only two possible values and
                    % they must be different), so we only check the
                    % first
                    if directions(1) == 1
                        obj.guessProbVector{end+1} = '^v';
                    elseif directions(1) == -1
                        obj.guessProbVector{end+1} = 'v^';                        
                    end
                else
                    % I'm not sure how to characterize this and so we call it react
                    obj.guessProbVector{end+1} = 'react';
                end
            end
        end
        
        function [obj, ballDest] = move(obj,ballY,ballX,TimingSequence)
        % This small function calls the appropriate functions to determine the
        % ball's destination. It takes all the ball's Y positions, all
        % its X positions, and the TimingSequence as inputs
            reactToBallY = obj.react(ballY, TimingSequence);
            reactToBallX = obj.react(ballX, TimingSequence);
            if reactToBallX < obj.InflectionPts(1)
                % If the ball hasn't reached the first inflection point, we just react
                % to it
                strategy = 'react';
            elseif ~obj.GuessThisTrial
                % If the ball is too close to the bottom or top of
                % the screen, we guess that it won't move towards
                % them (at least on its first move; it could feint
                % away and then come back, but it won't feint
                % towards or move towards)
                if reactToBallY < obj.ScreenMaxY/6
                    guessProbThisTrial = obj.guessProbVector(~ismember(obj.guessProbVector,{'vv','v^'}));
                elseif reactToBallY > 5*obj.ScreenMaxY/6
                    guessProbThisTrial = obj.guessProbVector(~ismember(obj.guessProbVector,{'^^','^v'}));
                else                  
                    guessProbThisTrial = obj.guessProbVector;
                end
                % Here, we set the guess for the trial. Remember, if this is the react
                % goalie instead of the guess goalie, guessProbThisTrial
                % only includes 'react', and so this will choose react
                % every time. This function picks one random element
                % from guessProbThisTrial
                obj.GuessThisTrial = datasample(guessProbThisTrial, 1);
                % From above, GuessThisTrial will be a 1x1 cell, and we want it to be
                % the string within that cell.
                obj.GuessThisTrial = obj.GuessThisTrial{1};
                strategy = obj.GuessThisTrial;
            else
                strategy = obj.GuessThisTrial;
            end
            % For all of the non-react strategies, we set the destination as the
            % farthest point the goalie thinks the ball could reach at
            % the moment it's reacting too. We use ismemberf because
            % sometimes, due to rounding errors, they'll be off by a
            % small amount.
            ballMaxMove = obj.ballMoveRange(ismemberf(obj.ballX,reactToBallX));
            switch strategy
              case 'react'
                ballDest = reactToBallY;
              case 'vv'
                ballDest = reactToBallY - ballMaxMove;
              case '^^'
                ballDest = reactToBallY + ballMaxMove;
              case 'v^'
                if reactToBallX < obj.InflectionPts(2)
                    ballDest = reactToBallY - ballMaxMove;
                else
                    ballDest = reactToBallY + ballMaxMove;
                end
              case '^v'
                if reactToBallX < obj.InflectionPts(2)
                    ballDest = reactToBallY + ballMaxMove;
                else
                    ballDest = reactToBallY - ballMaxMove;
                end                
              otherwise
                error('Unclear how this happened, but we have a strategy we can''t deal with! %s',strategy)
            end
        end
        
        function reactToBallPos = react(obj, ballPositions, TimingSequence)
        % This function takes in the history of ball y positions and the
        % Timing Sequence in order to determine where the computer
        % goalie will move. It does this by finding what ball movement
        % it should be reacting to (using obj.LagThisTrial) and
        % returning the value of the ball it's reacting to. This is
        % its destination. Other functions take this destination and
        % make sure it is no larger than the maximum allowed move.
        % 
        % ballPositions: the history of all ball positions in one axis
        % this trial up to this point. This can be the y or x
        % positions, ie Results.BallPositions(2,:) or
        % Results.BallPositions(1,:)
        % 
        % TimingSequence: the history of time on this trial, ie
        % Results.TimingSequence. Need this since a screen refresh doesn't
        % necessarily take the same amount of time each time, used to
        % figure out which ball position we're responding to.
            
        % This calculates the index in TimingSequence that corresponds to
        % obj.LagThisTrial seconds ago. Since TimingSequence and ballY
        % are indexed in the same way, it's also the index for
        % ballY. TimingSequence(end) is the most recent time, so
        % TimingSequence(end) - obj.LagThisTrial is the number of
        % seconds we're responding to. And min(abs(TimingSeuqence -
        % that)) gives us the index of closest number to that value.
            [~,reactIdx] = min(abs(TimingSequence - (TimingSequence(end) - obj.LagThisTrial)));
            
            %the position of the ball at the time the goalie is responding to
            reactToBallPos = ballPositions(reactIdx);
            
        end
        
        function [critPts,barMoveRange,ballMoveRange,ballX,InflectionPts] = calculate_crit_pts(obj,Settings)
        % To calculate this, we find the points where the ball's possible
        % vertical movement is greater than the bar's. We do this because
        % we're assuming the bar is tracking the ball as closely as possible
        % and so is at the same Y, roughly speaking. We want to calculate this
        % without any movement data, so it has to all be based on stuff in
        % Settings.

        % With this, we predict what the ball's x positions will be once it
        % starts moving. It will start from its starting position and
        % every move advance by Settings.BallSpeed until it reaches that
        % bar's x position.
            ballX = [Settings.BallStartingPosX: Settings.BallSpeed: Settings.BarStartingPosX];
            % This is how far the ball could move vertically by the end of the
            % trial, at every point. Because we assume that the ball's
            % horizontal speed and it's max vertical speed are the same, we
            % don't need to multiply/divide by anything here (technically,
            % we'd divide the difference between the barX and ballX by the
            % horizontal speed to get how many moves we have left, and then
            % multiply that by its max vertical speed to get the maximum
            % distance it could travel). 
            ballMoveRange = Settings.BarStartingPosX - ballX;
            % Moves are bounded by the screen. We check against half the
            % max y because the bar and ball start in the center of screen
            % not the bottom.
            ballMoveRange(ballMoveRange > Settings.ScreenRect(4)/2) = Settings.ScreenRect(4) / 2;
            ballMoveRange(ballMoveRange < 0) = 0;

            for i=1:length(ballX)
                % This calculates, for each ballX position i, how far the bar could go
                % if it started moving in one direction and just kept
                % going. It's 1+... because 1 is the base acceleration rate
                % (the value of the accel parameter if the bar is starting
                % from still). The big between square brackets generates an
                % array that goes from 0, 0 to the number of moves left-1 (we
                % have 0 twice and go to moves left-1 because acceleration
                % only kicks in on the third move in the same direction),
                % which we then multiply by the acceleration increment and add
                % to the base acceleration rate (1) to find out what the
                % acceleration value would be at each point. Finally, we
                % multiply by 32000 and divide by the SpeedFactor since this
                % is how we calculate the maxMove (see PenaltyKik_run.m for a
                % brief explanation). Therefore, for a given i, this gives us
                % the max move at each time point between time point i and the
                % end of the trial. We sum all those up to find the maximum
                % possible distance the bar could go if it just went in one
                % direction. Then the vector barMoveRange (with all i) gives
                % us the maximum move range of the bar at each time point.
                
                barMoveRange(i) = sum((1 + [0, 0:((Settings.BarStartingPosX - ballX(i)) / Settings.BallSpeed)-1] * Settings.BarJoystickAccelIncr ) * Settings.BarJoystickBaseSpeed);
            end
            % Moves are bounded by the screen. We check against half the max y
            % because the bar and ball start in the center of screen not the
            % bottom.
            barMoveRange(barMoveRange > Settings.ScreenRect(4)/2) = Settings.ScreenRect(4)/2;

            % The IntLag here is the approximate number of moves the bar lags
            % behind the ball because of its "reaction time". Since the
            % actual reaction time varies from trial to trial, we take the
            % 75% percentile.
            IntLag = round((Settings.CpuBarLagMinValue+.1*Settings.CpuBarLagDist.icdf(.75)) / Settings.ScreenRefreshInterval);
            % If there is no lag, we set IntLag to 2 so that the following command
            % shifts barMoveRange by one.
            if ~IntLag
                IntLag=2;
            end
            % We use it to shift the barMoveRange
            barMoveRange = [barMoveRange(IntLag:end), zeros(1,IntLag-1)];

            % Then we find those time points where the ball's maximum possible
            % move is larger than the bar's and the ball's maximum
            % possible move is less than half the vertical screen
            % (since that means they would be moving to the boundary
            % and things get weird there). These are the critical
            % points. Logical indexing gives us the index of these
            % values within ballX, which then gives us the x position
            % corresponding to them.
            critPts = ballX((ballMoveRange > barMoveRange + Settings.BarLength/2) & (ballMoveRange < Settings.ScreenRect(4)/2));
            
            % The first inflection point is the move right before the first
            % critical point, the second is that position plus 3 moves
            % (ie, first crit point plus 2 moves)
            InflectionPts = [critPts(1) - Settings.BallSpeed, critPts(1) + 2*Settings.BallSpeed];
        end
        
    end
end