% goalie_hmm
% 
% This class corresponds to the goalie that uses a Hidden Markov Model
% (HMM) to model the behavior of the ball. The ball is viewed as
% moving between the states of a HMM, where each state has one
% emission (which it always does) and the goalie is trying to learn
% the transition probabilities between states. Each state corresponds
% to a sequence of moves, the length of which is determined by the
% goalie's memory attribute, set at initialization. Memory specifies
% how many ball positions the goalie remembers and the number of moves
% in each state is equal to memory-1 (thus, memory must be equal to or
% greater than 2). So if memory=2, the goalie remembers the current
% position and the one beforehand; each state is one move and there
% are therefore three possible states ('^': up, 'v': down, and '-':
% center), corresponding to each possible move. In general, there are
% 3^(memory-1) total states and the states will be all possible
% permutations of the symbols ^, v, and - of length memory-1.
% 
% goalie_hmm can be used in two ways: regular and pretrained. Both
% versions play the game the same way, but regular goalie starts out
% naive, whereas if it's pretrained we give it some background data
% before it sees play to start learning transition probabilities.
% 
% To use goalie_hmm, first construct by calling `goalie =
% goalie_hmm(*)`. All arguments are necessary, though only memory
% needs to be decided upon by the user; ballStartY, ballStartX, maxY,
% and barX are all determined by the size of the screen. If
% pretraining goalie, call `goalie = goalie.pretrain(path)`, where
% path is a cell array of strings pointing to the locations (>=1) of
% the pretraining data. Then (for both regular and pretrained), for
% each trial, call `goalie=goalie.trial_start()` to reset the goalie
% (ballX and ballY are optional arguments and should not be used if
% the goalie is being run on the screen passed at
% construction). During the trial, call
% `goalie=goalie.update_state(ballY,ballX,true)` after each movement
% of the ball to update the moves and steps the goalie has of the
% ball. Finally, at any point `goalie.predict_dest()` can be called to
% get the goalie's prediction of the ball's final y position. This is
% done every refresh within computer_goalie.m (right after
% update_state) in order to get the point the goalie is moving towards.

classdef goalie_hmm
    properties
        % cell array storing all ball moves the goalie is aware
        % of. These are the actual states (and emissions) of the
        % behavioral HMM the goalie is simulating. It's updated
        % every time update_state is called and used by hmmestimate
        % and hmmgenerate to predict where the ball will end up
        ballMoves
        
        % how many ball y positions the goalie should remember. See the
        % docstring of goalie_hmm (the initialization function) for
        % more details
        memory
        
        % most recent ball y position
        ballLastY
        
        % array containing the non-zero vertical displacement of each
        % move. Goalie assumes that on each up or down move, the ball
        % moves up or down by the average of this array. We ignore
        % zeros because we want to use this for determining
        % displacement on up or down, not straight.
        ballStepsY
        
        % most recent ball x position
        ballLastX
        
        % array containing the non-zero horizontal displacement of each
        % move. Used (with ballLastX and barX) to determine how many
        % moves are between now and the bar reaching the goalie.
        ballStepsX
        
        % containers.Map mapping between the integers and symbols
        % for the up, down, and center moves. We use this so we can
        % convert from our calculated values (intMoves) to the
        % symbols we use to represent them: ^ (up), v (down), and -
        % (center).
        moveMap
        
        % cell array showing all possible states, given the memory. This will
        % be all possible permutations of the chars ^, v, and - of
        % length memory-1. So if memory=2, then
        % allStates={'v','^','-'} and if memory=3,
        % allStates={'^^','^v','^-','-^','-v','--','vv','v^','v-'},
        % etc.
        allStates
        
        % The x position of the bar (unchanging, depends on the screen). Used
        % to determine how far the ball is from the goalie.
        barX
        
        % The maximum possible y position (unchanging, depends on the
        % screen). Used to make sure the goalie doesn't predict
        % impossible positions.
        maxY
        
        % The initial x and y position of the ball; we want to hold on to them
        % so we can reset ballLastX and Y for each trial
        ballStartX
        ballStartY
    end
    
    methods

        function obj = goalie_hmm(memory,ballStartY,ballStartX,maxY,barX)
        % This function initializes the goalie, setting the initial
        % values.
        % 
        % memory: integer greater than 1 that specifies how many ball
        % y positions the goalie should remember. The goalie deals
        % with move sequences of length memory-1. A memory value of 2
        % will have the goalie remember the last two states and thus
        % the most recent move (up, down, or straight). If the memory
        % value is 3, the goalie deals with the last two moves
        % (up-up, up-down, down-up, etc). And so on.
        % 
        % ballStartY: double, the initial y position of the ball
        % 
        % ballStartX: double, the initial x position of the ball
        % 
        % maxY: the maximum possible y position, equal to the
        % vertical resolution of the PsychToolbox Screen. This is
        % so the goalie doesn't predict the ball will have an
        % impossible y
        % 
        % barX: the x position of the bar/goalie. Used to determine
        % how far away the ball is from the goalie.
            assert(memory>1,'Unable to create goalie with memory 1! (they wouldn''t remember enough positions to check for moves)')
            assert(floor(memory)==memory,'Memory must be an integer!')
            obj.ballMoves = {};
            obj.ballStepsY = [];
            obj.ballStepsX = [];
            obj.memory = memory;
            obj.ballLastY = ballStartY;
            obj.ballLastX = ballStartX;
            obj.moveMap = containers.Map({1 0 -1}, {'^','-','v'});
            % permn is a function written by someone else (not a standard matlab
            % function) and can be found in this repo as permn.m, with
            % its associated license permn_license.txt
            obj.allStates = transpose(cellstr(permn(['^-v'],memory-1)));
            % We want to know our own x position so we know how far
            % away the ball is
            obj.barX = barX;
            % goalie should know where the top of the screen is
            obj.maxY = maxY;
            % we want to hold on to ballStartX and ballStartY so we
            % can reset ballLastX and Y for each trial
            obj.ballStartY = ballStartY;
            obj.ballStartX = ballStartX;            
        end

        function obj = trial_start(obj,ballX,ballY)
        % At the beginning of each trial, we want to reset ballLastY and
        % ballLastX so that they're equal to ballStartY and X,
        % respectively. This way the goalie doesn't think the ball
        % teleports between trials (which would give us a really
        % large ballSteps value).
        % 
        % ballX and ballY are the x and y positions of the ball we
        % should reset goalie too. They are both optional; if they're
        % not passed, then we'll use obj.ballStartX and
        % obj.ballStartY. They should only be passed during
        % pretraining, when the data you're about to call update_state
        % with has different starting positions than those set at the
        % construction of the goalie.
            % If we only pass one argument (that is, called
            % obj.trial_start() without passing ballX or ballY; the
            % one arg is obj), then we set ballX and ballY to their
            % default values. We may call trial_start with a ballX
            % that has greater than length 1; if we do this, that
            % ballX is not meant for this trial_start, it's for
            % goalie_react_guess.trial_start, so we ignore it.
            if nargin < 2 || length(ballX) > 1
                ballX = obj.ballStartX;
            % We may call trial_start with a ballY that has greater than length
            % 1. If we do this, that ballY is not meant for this
            % trial_start, it's meant for
            % goalie_react_guess.trial_start, so we ignore this ballY
            elseif nargin < 3 || length(ballY) > 1
                ballY = obj.ballStartY;
            end
            obj.ballLastY = ballY;
            obj.ballLastX = ballX;
        end
        
        function [obj, ballDest]  = move(obj,ballY,ballX,TimingSequence)
        % This small function updates the state of the goalie to the most
        % recent ball positions and then returns the updated goalie and its
        % most recent prediction. It takes all the ball's
        % Y positions, its current X position, and the
        % TimingSequence as inputs (Timing not used by this
        % goalie class, but by goalie_react_guess)
            % We want the ball's current Y position, but because
            % goalie.move needs to take in ballY (the history of
            % all Y positions), we just grab the last value
            obj = obj.update_state(ballY(end),ballX(end),true);
            ballDest = obj.predict_dest();
        end
        
        function obj = pretrain(obj,path)
        % This function loads in the output .mats given at path and uses the
        % Results.BallPositions field to update the goalie's
        % state. This way the goalie is pretrained on data and
        % doesn't start naive.
        %
        % path: a cell array of strings, containing the paths to
        % output .mats we should use
            % Doing a bunch of nested for loops like this is inefficient, but it's
            % fast and infrequent enough that it doesn't really
            % matter.
            for i=1:length(path)
                output = load(path{i});
                for j=1:length(output.Results)
                    results = output.Results(j);
                    % We need to set the ballLastY and ballLastX to
                    % the ball's position at the beginning of the
                    % trial here, otherwise
                    obj = obj.trial_start(output.Settings.BallStartingPosY,output.Settings.BallStartingPosX);
                    for k=1:size(results.BallPositions,2)
                        % For each movement within each Results within each output .mat, we
                        % update the states to include the observed
                        % ball movements. The false here (variable
                        % updateSteps) means that goalie does not
                        % learn the size of the steps from this
                        % prtraining, since it's likely that they will
                        % be different.
                        obj = obj.update_state(results.BallPositions(2,k),results.BallPositions(1,k),false);
                    end
                end
            end
            % Make sure to reset the ballLastY and ballLastX values
            obj = obj.trial_start();
        end
        
        function obj = update_state(obj,ballY,ballX,updateSteps)
        % This function updates the observed states, taking the most recent
        % ballY and using that to determine what state the ball is in
        % (ie what the last move or last series of moves [depending on
        % obj.memory] was/were). We also keep track of the vertical
        % and horizontal displacement of each move (ballStepsX and
        % ballStepsY) and the most recent x position. These are all
        % used when predicting where the ball will end up.
        % 
        % ballY: double, most recent y position of the ball
        % 
        % ballX: double, most recent x position of the ball
        % 
        % updateSteps: true/false, whether we should update the
        % ballStepsY and ballStepsX properties. Almost always true;
        % only false when we're pretraining the goalie and don't want
        % to learn the step size (which will vary based on the speed
        % of the ball and size of the screen).
            % We only remember a small number of past positions
            if length(obj.ballLastY) == obj.memory
                obj.ballLastY = [obj.ballLastY(2:end), ballY];
            else
                obj.ballLastY(end+1) = ballY;
            end
            if length(obj.ballLastY) > obj.memory - 1
                % If we're pretraining, we don't want to get this steps information
                % (since the system set up on the pre-training data
                % may be different from the current one).
                if updateSteps
                    % We want to keep track of how large each movement
                    % is, so we can use it for the prediction. if the y
                    % difference is 0 though, we don't care.                    
                    if obj.ballLastY(end) ~= obj.ballLastY(end-1)
                        obj.ballStepsY(end+1) = abs(obj.ballLastY(end) - obj.ballLastY(end-1));
                    end
                    % We also want to keep track of x steps, to determine how much farther
                    % the ball has to go
                    if obj.ballLastX ~= ballX
                        % We have that if statement because there
                        % will be several time points at the
                        % beginning of the trial where the ball's
                        % not moving. We don't want to count those.
                        obj.ballStepsX(end+1) = abs(ballX - obj.ballLastX);
                    end
                end
                % We use those positions to determine whether they've
                % been moving up or down. intMoves will contain them as
                % integers (0, -1, or 1) in an array
                intMoves = sign(diff(obj.ballLastY));
                % Here we convert intMoves to a cell array ...
                intMoves = num2cell(intMoves);
                % ... so we can use cellfun to get a string of length
                % obj.memory-1 of characters that detail what
                % directions they've moved. These will be the states of
                % our Hidden Markov Model.
                obj.ballMoves{end+1} = cellfun(@(x) obj.moveMap(x),intMoves);
                % We now update our allStates so that the most
                % recent move is state 1, since hmmgenerate assumes
                % we are currently in state 1
                idx = 1:length(obj.allStates);
                % We find the index, in the current allStates, of the last
                % Move. We use regular parentheses for the call to
                % ballMoves because this works by comparing two cell
                % arrays.
                lastMoveIdx = find(strcmp(obj.allStates, obj.ballMoves(end)));
                % We rearrange the index vector so that the index
                % of the last move is first, and then all the rest
                idx(lastMoveIdx) = [];
                idx = [lastMoveIdx idx];
                % We update allStates 
                obj.allStates = obj.allStates(idx);
            end
            % For x positions, we only care about the most recent
            % one (we do this after the if statement so we can
            % calculate ballStepsX first).
            obj.ballLastX = ballX;
        end
        
        function [ballDestination] = predict_dest(obj)
            % Start with most recent ball position and predict where it will end
            % up. This needs to be first in case we hit that return
            % statement.
            ballDestination = obj.ballLastY(end);
            % To determine how many moves left before the end of the trial,
            % we determine how far the ball is from the bar (along the x
            % axis) and then divide by the average of ballStepsX. It also
            % needs to be an integer, so we round it.
            movesRemaining = round(abs(obj.ballLastX - obj.barX) / mean(obj.ballStepsX));
            if isinf(movesRemaining) || isnan(movesRemaining)
                % The first time we try to generate a prediction,
                % movesRemaining will be Inf. If we haven't stored any
                % ballMoves, then we also haven't stored any ballStepsX and
                % so movesRemaining will be NaN. Instead of trying to
                % generate a prediction here (which would be meaningless),
                % we return, giving the most recent Y position.
                return
            end            
            % Estimate the transition and emission matrices from
            % the moves we've seen so far (emis will always be an
            % identity matrix, since we've made the states and
            % emissions identical; each state only has one emission
            % associated with it and they have the same identity).
            [trans, emis] = hmmestimate(obj.ballMoves, obj.ballMoves,'Symbols',obj.allStates,'Statenames',obj.allStates);
            % We generate the moves left between now and the end of
            % the trial. 
            seq = hmmgenerate(movesRemaining,trans,emis,'Symbols',obj.allStates,'Statenames',obj.allStates);
            % We predict that on each movement, the ball will move
            % the average of its steps so far
            ballStepY = mean(obj.ballStepsY);
            if isnan(ballStepY)
                % In this case, the ball never moved and so we can
                % think of ballStep being 0. 
                ballStepY = 0;
            end
            % We go through each predicted state
            for i=1:length(seq)
                % And for each state, the last char is the "new move". So if each
                % state is a sequence of three moves, the first two
                % chars of state i are the last two chars of state i-1
                % and thus only the last char is new. This is the
                % move we use to update our prediction.
                switch seq{i}(end)
                  case '^'
                    ballDestination = ballDestination + ballStepY;
                  case 'v'
                    ballDestination = ballDestination - ballStepY;
                    % and that's it, on the case '-', we're
                    % predicting that its y value won't change at all.
                end
                % Make sure that the ball is in a possible position.
                if ballDestination < 0
                    ballDestination = 0;
                elseif ballDestination > obj.maxY
                    ballDestination = obj.maxY;
                end
            end
            % once we've gone through each predicted state, we
            % return the predicted ballDestination.
        end
    end
end