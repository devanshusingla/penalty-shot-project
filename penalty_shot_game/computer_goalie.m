% computer_goalie.m
% 
% This wrapper function takes in a handful of variables and returns
% the next move of the computer goalie. The most important variable is
% goalie, which is the object representing the current goalie. Of the
% other required variables, currentBarY and maxMoveSize are used to
% ensure the goalie does not move too far in one move (defined as
% approximately the distance a human goalie could move). ballY,
% currentBallX, and TimingSequence are used by the different
% goalie.move functions (see goalie_hmm and goalie_guess_react for
% more details).
% 
% To use, simply call computer_goalie with the required
% variables. It's assumed the goalie will be the same on any given
% trial, but it can probably be changed between trials.
% 
% Note that only the react goalie has a move lag. However, all have to
% deal with the maximum allowed move and the way the hmm goalie's
% predictions work often result in it not being perfect.

function [newY,goalie,dest] = computer_goalie(goalie,currentBarY,maxMoveSize,ballY,ballX,TimingSequence)
% This main function, based on the value of goalieType, calls the
% goalie's move functions, gets the goalie's destination back and then
% calls move_towards to check if the move is greater than the maximum
% allowed move. move_towards returns the newY of the goalie, which
% computer_goalie then returns to the calling script. dest is
% necessary just for logging purposes, goalie is potentially
% updated every call.
% 
% goalie: the current goalie object. At this point, it must be already
% initialized and had its trial_start funciton called. computer_goalie
% just calls its move function to get its destination.
% 
% currentBarY: the current y position of the bar. Used to make sure
% the planned move isn't too far away.
% 
% maxMoveSize: the maximum allowed move size (in pixels). Calculated
% each screen refresh by the calling code, based on the current
% acceleration parameter, the "maximum input" (the value that the
% controller returns when its joystick is pressed all the way up),
% and the SpeedFactor.
% 
% ballY: a vector with all the ball's Y history (ie
% BallPositions(2,:)). Used for goalie_react_guess.move, and the last
% value is used for goalie_hmm.move.
% 
% ballX: a vector with all the ball's X history (ie
% BallPositions(1,:)). Used for goalie_react_guess.move, and the last
% value is used for goalie_hmm.move.
% 
% TimingSequence: a vector with all the timing information, used by
% goalie_react_guess.move to determine how many moves ago its lag was.
    
    [goalie, dest] = goalie.move(ballY,ballX,TimingSequence);
    
    newY = move_towards(dest,currentBarY,maxMoveSize);
    
end

function newY = move_towards(dest,currentBarY,maxMoveSize)
% This function simply takes the destination of the goalie, its
% current y position, and the maximum allowed move size and returns
% its new y position. This is either dest or, if abs(dest) >
% maxMoveSize, currentBarY +/- maxMoveSize (in the direction of dest).
% 
% dest: where the goalie wants to move. In the react goalie's case,
% this will be the lagged position of the ball. For the hmm goalie,
% this will be its prediction of the ball's final position.
% 
% currentBarY: the current y position of the bar. Used to make sure
% the planned move isn't too far away.
% 
% maxMoveSize: the maximum allowed move size (in pixels). Calculated
% each screen refresh by the calling code, based on the current
% acceleration parameter, the "maximum input" (the value that the
% controller returns when its joystick is pressed all the way up),
% and the SpeedFactor.
 
    %make sure move is less than the maxMoveSize
    move = dest - currentBarY;
    if abs(move) > maxMoveSize;
        % This moves us in the direction we were going, but only of
        % a magnitude of maxMoveSize
        move = sign(move) * maxMoveSize;
    end
    
    % Update y position and return.
    newY = currentBarY + move;
end
