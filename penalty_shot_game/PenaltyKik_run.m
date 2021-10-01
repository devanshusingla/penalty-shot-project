% PenaltyKik_run.m
% 
% Penalty Kick game by Jean-Francois Gariepy, overhauled by Bill
% Broderick.
% 
% This script corresponds to one run of the Penalty Kick game, for one
% subject. It is called by Wrapper_PenaltyKik.m and passed a Settings
% struct, the SubjName of the current subject, the currentRun, and the
% display window we're showing things on. This script should *not* be
% run directly, as all of the commands to set up the screen are in
% Wrapper_PenaltyKik.m. 
% 
% This script loops through a certain number of runs (specified in
% Settings) and creates a Results stuct which stores all of the
% variables we care about for the results (path of the ball, path of
% the bar, outcome, etc.). This Results struct is multidimensional,
% with one entry for each trial. It is saved every trial, but that
% path it's stored at is specified by the date, SubjName, runType, and
% currentRun, so one call to this script will write to the same file
% several times.
% 
% This script returns the Results struct (so the outcomes and
% opponents can be extracted for overall win percentages) as well as
% escapeCheck, a boolean that specifies whether the experimenter
% pressed escape during play. When escape is pressed, we save
% everything, return from this script immediately (assuming we're not
% in the middle of a WaitSecs command), close the screen, flush the
% KbQueue, clear the joysticks, and exit. Otherwise, Wrapper will
% calculate the overall win percentages and display them to the
% user. 
% 
% Note also that this function does not open or close any screens;
% that's handled by the Wrapper.

function [Results,escapeCheck] = PenaltyKik_run(Settings,SubjName,currentRun,DisplayWindow,goalie)
% Main function call.
%
% Arguments:
% 
%  - Settings: struct, contains the various settings necessary to run
%    the task. These relate to the joysticks, screen, speed, reward
%    and everything. Note that these will all be the same for a given
%    call to Wrapper (most likely, a given subject) and the subset of
%    variables that are constant across all calls are saved in this
%    repo as Settings.mat. The entire Settings struct is saved
%    along with the Results.
% 
%  - SubjName: string, the name of the current subject. Can be
%    anything, used only for determining the save path. Typed in by
%    the experimenter in Wrapper.
% 
%  - currentRun: int, the number of the current run. Used for
%    determining the save path and display purposes.
% 
%  - DisplayWindow: int, the number pointing to the screen we're
%    currently drawing everything on. Returned by PsychToolbox's
%    Screen('OpenWindow') command in Wrapper.
%  
%  - goalie: goalie obj, this object is the goalie, with various
%    properties and methods. It will either have class goalie_hmm or
%    goalie_react_guess. It's initialized in the Wrapper so that it
%    can learn over the course of the subject and to set a couple
%    trial-independent variables.
    
    % Connect the gamepads. We do this here (instead of in
    % Wrapper) because if runType is Vs, we switch which joystick
    % controls the bar and which the ball each run.
    BallJoystick = JoystickServer(Settings.BallJoystickNum, Settings.BallJoystickDeadZone, Settings.BallJoystickGeneration);
    if ~strcmp(Settings.runType,'train')
        % We want to allow input from the BarJoystick if runType is not train
        % (in which case they only play against the computer).
        BarJoystick = JoystickServer(Settings.BarJoystickNum, Settings.BarJoystickDeadZone, Settings.BarJoystickGeneration);
    else
        % There are instances when we want to pass BarJoystick around. Instead
        % of doing an if strcmp(runType,'experiment') check everytime,
        % we make sure that BarJoystick is defined and then have the
        % function make the appropriate check.
        BarJoystick = [];
    end

    % This opens up the main figure of the experiment to display the log.
    CurrentFigure = figure('NumberTitle', 'off','Name', sprintf('PenaltyKick: %s - %s, run %d', Settings.runType,SubjName,currentRun),'Position',[1046 650, 867, 500]);
    CurrentAxes = axes();
    set(CurrentAxes, 'Visible', 'off');
    LogHandle = uicontrol(CurrentFigure, 'Style', 'edit', 'Units', 'normalized','Position', [0, 0, 1, 1],'min', 0, 'max', 2,'String', '','HorizontalAlignment', 'left');
    set(CurrentFigure, 'Visible', 'on');

    % Add current time to the log as 'Run Started' event.
    CurrentExperimentLog{1} = sprintf('%s %s Subj: %s, goalie %s, Run: %d Started',datestr(now,13),Settings.runType,SubjName,Settings.goalieType,currentRun);
    % Update the experiment log.
    set(LogHandle, 'String', fliplr(CurrentExperimentLog));

    % Set the default value of escapeCheck
    escapeCheck = false;
    
    KbName('UnifyKeyNames');
    
    % We attempted to use the scanner trigger to start each run, but ran
    % into issues with the timing (the task kept going for more than a
    % minute after the scan stopped). Unclear why this might be, since
    % the timing values have nothing to do with the trigger, but we
    % are relying on the 'spacebar' trigger instead. If you wish to
    % try and get the run to start when the program receives the
    % trigger from the scanner, make the same call as below but with
    % the argument 'scanner' instead of 'spacebar'. It's recommended
    % that you then wrap it in a try/catch block so that it can be
    % used on machines that are not hooked up to the scanner / allow
    % it to fall back on the spacebar trigger if it fails.
    escapeCheck = runTrigger(DisplayWindow, currentRun, Settings, 'spacebar');
    if escapeCheck
        Results = [];
        return;
    end
    spacebar_pressed = GetSecs;
    
    % Draw a fixation cross
    drawFixationCross(DisplayWindow,Settings);
    
    if strcmp(Settings.runType,'experiment')
        % This command waits 4 TRs so that we can drop the disdaqs afterwards
        % (basically, we're letting the scanner stabilize). We only
        % need to this if we're running the actual experiment.
        WaitSecs(8);
    end

    runStart = GetSecs;
    % Start with 0, because we increment at the beginning of the loop
    trial = 0;
    if isnan(Settings.RunLengthSecs)
        % This way, it's definitely enough time.
        RunLengthSecs = Settings.MaxNumberOfTrials * 100;
    else
        RunLengthSecs = Settings.RunLengthSecs;
    end    
    
    % According to Scott, we should keep running trials as long as we're
    % more than 5 seconds before the end of the run. Because of the
    % delay in the BOLD signal, we won't get relevant brain data for
    % those last 5 seconds anyway.
    while GetSecs - runStart < RunLengthSecs - 5
        % Every trial, we increment the trial and save it.
        trial = trial + 1;
        if trial > Settings.MaxNumberOfTrials
            break
        end
        Results(trial).trial = trial;

        % These will always be the same.
        Results(trial).SubjName = SubjName;
        Results(trial).currentRun = currentRun;
        Results(trial).runStart = runStart;
        Results(trial).spacebar_pressed = spacebar_pressed;
        
        % We update goalie every time because (if it's hmm or hmm_pretrain),
        % it will be learning every trial.
        Results(trial).goalie = goalie;
        
        %Record the start of the trial
        Results(trial).trialStart = GetSecs - runStart;
        
        Screen('Flip',DisplayWindow);
        
        % This resets all the trial-specific variables to their defaults.
        Results(trial).BarY = [];
        Results(trial).BallPositions = [];
        Results(trial).BallJoystickHistory = [];
        Results(trial).BarJoystickHistory = [];
        Results(trial).TimingSequence = [];
        Results(trial).RewardBall = 0;
        Results(trial).RewardBar = 0;
        
        % If the joystick isn't centered, we force them to do so
        % before the trial begins.
        while ~CenterJoystick(BallJoystick)
            joystick_axes = BallJoystick.CalibratedJoystickAxes;
            % We need to call Screen('TextSize') before every call where we
            % draw text, in order to make sure we draw the text at the size
            % we want            
            Screen('TextSize', DisplayWindow, Settings.InstructionsTextSize);
            DrawFormattedText(DisplayWindow,'Please center the y-axis of your joystick','center','center',[255 255 255]);
            Screen('Flip',DisplayWindow,[],1);
            drawFixationCross(DisplayWindow,Settings,joystick_axes(2));
            %Check to see if escape has been pressed. If it has, return, save
            %variables, and close all screens.
            [pressed, firstPress] = KbQueueCheck();
            if pressed && firstPress(KbName('escape'))
                escapeCheck = true;
                saveVarsAndQuit(currentRun,SubjName,struct('Settings',Settings,'CurrentExperimentLog',CurrentExperimentLog,'Results',Results));
                return
            end        
        end

        %Fixation Cross -- since we're just using this as something for them
        %to look at, we just have this show up in the center.
        drawFixationCross(DisplayWindow,Settings);
        
        % Pick the fixation cross duration for this trial and wait that length
        % of time (FirstFixCrossJitterOrder is set in Wrapper).
        Results(trial).FirstFixCrossJitterThisTrial = Settings.FirstFixCrossJitterOrder(trial);
        WaitSecs(Results(trial).FirstFixCrossJitterThisTrial);
        
        %Check to see if escape has been pressed. If it has, return, save
        %variables, and close all screens.
        [pressed, firstPress] = KbQueueCheck();
        if pressed && firstPress(KbName('escape'))
            escapeCheck = true;
            saveVarsAndQuit(currentRun,SubjName,struct('Settings',Settings,'CurrentExperimentLog',CurrentExperimentLog,'Results',Results));
            return
        end        
        
        % Pick the opponent for this trial (OpponentOrder is set in Wrapper).
        Results(trial).Opponent = Settings.OpponentOrder{trial};
        
        % Display an cue specifying which opponent the participant will be
        % playing, with a specific color. These colors come from
        % colorbrewer2.org (the end points of diverging 5-class
        % RdBu, which should be colorblind safe)
        if strcmp(Results(trial).Opponent,'human')
            opp_cue = 'Matt';
            % We just do if/else because we know this is either rb or br
            if strcmp(Settings.CueColors, 'rb')
                cue_color = [202 0 32];
            else
                cue_color = [5 113 176];
            end
        else
            opp_cue = 'Computer';
            if strcmp(Settings.CueColors, 'rb')
                cue_color = [5 113 176];            
            else
                cue_color = [202 0 32];                
            end
        end
        % We need to call Screen('TextSize') before every call where we
        % draw text, in order to make sure we draw the text at the size
        % we want        
        Screen('TextSize', DisplayWindow, Settings.CueTextSize);
        DrawFormattedText(DisplayWindow, opp_cue, 'center', 'center', cue_color);
        Screen('Flip',DisplayWindow);
        
        WaitSecs(Settings.TimeToWaitWithOppPic);

        %Fixation Cross -- since we're just using this as something for them
        %to look at, we just have this show up in the center.
        drawFixationCross(DisplayWindow,Settings);
        
        % Pick the fixation cross duration for this trial and wait that length
        % of time (FirstFixCrossJitterOrder is set in Wrapper).
        Results(trial).SecondFixCrossJitterThisTrial = Settings.SecondFixCrossJitterOrder(trial);
        WaitSecs(Results(trial).SecondFixCrossJitterThisTrial);
        
        % All of these need to be initialized here so we can assign the
        % results of this function to Results(trial) (otherwise it
        % gives a "Subscripted assignment between dissimilar
        % structures." error)
        Results(trial).outcome = 0;
        Results(trial).StartOfGame = 0;
        Results(trial).trialLength = 0;
        Results(trial).CpuBarLagThisTrial = 0;
        Results(trial).maxMove = [];
        Results(trial).dest = [];
        Results(trial).accel = [];
        
        %Check to see if escape has been pressed. If it has, return, save
        %variables, and close all screens.
        [pressed, firstPress] = KbQueueCheck();
        if pressed && firstPress(KbName('escape'))
            escapeCheck = true;
            saveVarsAndQuit(currentRun,SubjName,struct('Settings',Settings,'CurrentExperimentLog',CurrentExperimentLog,'Results',Results));
            return
        end        
        
        Screen('Flip',DisplayWindow);
        
        % We call goalie.trial_start to get some trial-specific things set
        % up. See goalie_hmm.m and goalie_react_guess.m for details, but
        % in brief: for hmm or hmm_pretrain, this just resets the
        % last-seen ball position so the goalie doesn't think the ball
        % teleported; for react or guess, this sets the lag for a given
        % trial and updates any learning we're doing. We call it
        % here because we want access to the last trial.
        if trial > 1
            Results(trial).goalie = Results(trial).goalie.trial_start(Results(trial-1).BallPositions(1,:),Results(trial-1).BallPositions(2,:));
        % Only pass the last trial if there was a last trial.
        else
            Results(trial).goalie = Results(trial).goalie.trial_start();
        end
        
        % Play the game
        [Results(trial),escapeCheck] = playGame(Settings,Results(trial),BallJoystick,BarJoystick,DisplayWindow,cue_color);
        
        % Update goalie every trial
        goalie = Results(trial).goalie;
        % we save this as a struct of the goalie because that's
        % more accessible by Python.
        Results(trial).goalie = struct(goalie);
        if escapeCheck
            saveVarsAndQuit(currentRun,SubjName,struct('Settings',Settings,'CurrentExperimentLog',CurrentExperimentLog,'Results',Results));
            return
        end
        
        % Update the experiment log and the reward, displaying the results.
        CurrentExperimentLog{end + 1} = sprintf('%s %s Subj: %s, Run %d, Trial %d ended; Opponent: %s, Result: %s',datestr(now,13),Settings.runType,SubjName,currentRun,trial,Results(trial).Opponent,Results(trial).outcome);
        set(LogHandle, 'String', fliplr(CurrentExperimentLog));
        % We need to call Screen('TextSize') before every call where we
        % draw text, in order to make sure we draw the text at the size
        % we want        
        Screen('TextSize', DisplayWindow, Settings.CueTextSize);
        if strcmp(Results(trial).outcome,'win')
            Results(trial).RewardBall = Settings.RewardForScoring;
            DrawFormattedText(DisplayWindow,'WIN','center','center', cue_color);
        elseif strcmp(Results(trial).outcome,'loss')
            Results(trial).RewardBar = Settings.RewardForBlockingBall;
            DrawFormattedText(DisplayWindow,'LOSS','center','center', cue_color);
        end
        
        Screen('Flip',DisplayWindow,[]);
        
        % We want to alert the human opponent to look back at the
        % screen after play is done. However, this doesn't appear
        % to do anything on Linux...
        if strcmp(Results(trial).Opponent, 'cpu')
            beep
        end

        WaitSecs(Settings.TimeToWaitAfterOutcome);
        
        save(sprintf('%s/%s_%s_%s_%d.mat',Settings.OutputServer,Settings.CurrentDateTime,Settings.runType,SubjName,currentRun), 'Results', 'Settings', 'CurrentExperimentLog');
        
        Screen('Flip',DisplayWindow);
        
        %Check to see if escape has been pressed. If it has, return, save
        %variables, and close all screens.
        [pressed, firstPress] = KbQueueCheck();
        if pressed && firstPress(KbName('escape'))
            escapeCheck = true;
            saveVarsAndQuit(currentRun,SubjName,struct('Settings',Settings,'CurrentExperimentLog',CurrentExperimentLog,'Results',Results));
            return
        end
        
    end
end

function escapeCheck = runTrigger(DisplayWindow, currentRun, Settings, startInput)
% This function is called at the beginning of the run to display the
% appropriate text on screen and try to receive the appropriate
% input to start the run. If the experimenter presses escape while
% the function is waiting, we return immediately and will quit out.
% 
% DisplayWindow: the window to draw text on
% 
% the Settings struct, because it contains info on the runType and
% player names, if relevant
% 
% startInput: 'spacebar' or 'scanner', which specifies whether
% we're starting when the experimenter presses space or when the
% program receives the scanner trigger.
    if strcmp(Settings.runType,'Vs')
        if currentRun == 1
            curPlayer = Settings.P1Name;
        else
            curPlayer = Settings.P2Name;
        end
        if strcmp(startInput, 'scanner')
            runStartText = sprintf('Run %d will begin with scanner trigger\n%s is controlling the ball',currentRun,curPlayer);
        elseif strcmp(startInput, 'spacebar')
            runStartText = sprintf('Press spacebar to begin run %d\n%s is controlling the ball',currentRun,curPlayer);
        end
    elseif strcmp(Settings.runType,'anat_practice')
        % If we're practicing, we make sure to emphasize that
        if strcmp(startInput, 'scanner')
            runStartText = sprintf('PRACTICE will begin with scanner trigger');
        elseif strcmp(startInput, 'spacebar')
            runStartText = sprintf('Press spacebar to PRACTICE');
        end
    else
        % Otherwise we just say that the run will begin with
        % scanner trigger / spacebar
        if strcmp(startInput, 'scanner')
            runStartText = sprintf('Run %d will begin with scanner trigger',currentRun);
        elseif strcmp(startInput, 'spacebar')
            runStartText = sprintf('Press spacebar to begin run %d',currentRun);
        end
    end
    % We need to call Screen('TextSize') before every call where we
    % draw text, in order to make sure we draw the text at the size
    % we want
    Screen('TextSize', DisplayWindow, Settings.InstructionsTextSize);
    DrawFormattedText(DisplayWindow,runStartText,'center','center',WhiteIndex(DisplayWindow));
    % Screen Flip is necessary to update the displayed screen
    Screen('Flip',DisplayWindow);
    while 1
        [~,~,c] = KbCheck;
        if strcmp(startInput, 'scanner')
            % We wait for scanner trigger to start
            daq = DaqDeviceIndex();
            daqdata=DaqDIn(daq);
            if daqdata(2) == 255
                % original if check: if daqdata(2) ~= 254
                escapeCheck = false;
                return;
            end
        elseif strcmp(startInput, 'spacebar')
            %We wait for spacebar press from experimenter to begin run
            if find(c)==KbName('space'); % experimenter presses spacebar
                escapeCheck = false;
                return;
            end
        end
        if find(c) == KbName('escape'); %experimenter pressed escape
            escapeCheck = true;
            return;
        end    
    end
end

function drawFixationCross(DisplayWindow,Settings,y_percentage)
% This function draws a fixation cross in the center of the given
% screen.
%
% DisplayWindow: which window to draw the fixation cross on
%
% Settings: the Settings struct, used because it contains the origin
% of the display
% 
% y_percentage: the percentage (from -1 to 1) you want to be above or
% below the y-center of the screen. Optional, if not included,
% fixation cross will be drawn in the center of the screen.
    Screen('BlendFunction',DisplayWindow, 'GL_SRC_ALPHA', 'GL_ONE_MINUS_SRC_ALPHA');
    % This captures the center of the screen. For some reason, can't
    % insert this RectCenter call into the Screen('DrawLines')
    % function call.
    if nargin<3
        [x_center, y_center] = RectCenter(Settings.ScreenRect);
    else
        [x_center, y_center] = RectCenter(Settings.ScreenRect);
        % y_center is also half the y screen size.
        y_center = y_center + y_percentage * y_center;
    end
    Screen('DrawLines', DisplayWindow, [-40 40 0 0; 0 0 -40 40], 4, WhiteIndex(DisplayWindow), [x_center y_center], 2);
    Screen('Flip',DisplayWindow);
end

function saveVarsAndQuit(currentRun,SubjName,varsToSave)
% This function is called when escape is pressed to save everything
% contained in the varsToSave struct. Immediately after it's
% called, the user should quit.
%   
% currentRun: int, which run we're currently in (used for save path)
%
% SubjName: string, the name of the subject (used for save path)
%
% varsToSave: struct containing the variables we want to save. Must
% contain Settings, always contains CurrentExperimentLog. Optionally
% contains others.
    if isfield(varsToSave,'CurrentExperimentLog')
        % CurrentExperimentLog is cell array of strings, possibly
        % multi-dimensional, and so if it's multi-dimensional and we
        % pass it to struct, it will make the struct
        % multi-dimensional. We want the struct to be one dimensional,
        % so we turn it instead into one long string, with each cell
        % separated by a newline. Every other field in varsToSave
        % will be identical across the different dimensions, so we
        % just pluck from the beginning.
        currExprLog = strjoin(extractfield(varsToSave,'CurrentExperimentLog'),'\n');
        varsToSave = rmfield(varsToSave,'CurrentExperimentLog');
        for i=2:numel(varsToSave)
            % We use isequaln because there may be nans in
            % varsToSave and (even if they're in the same place)
            % nans always return false through isequal.
            assert(isequaln(varsToSave(1),varsToSave(i)),'The variables to save are messed up! It is multidimensional and entry %s differs from entry 1! 1: %s, %s: %s',i,varsToSave(1),i,varsToSave(i));
        end
        varsToSave = varsToSave(1);
        varsToSave.CurrentExperimentLog = currExprLog;
    end
    Settings = varsToSave.Settings;
    varsToSave.esctime = GetSecs;
    % Save all the variables we passed
    save(sprintf('%s/%s_%s_%s_%d.mat',Settings.OutputServer,Settings.CurrentDateTime,Settings.runType,SubjName,currentRun),'-struct','varsToSave');
end

function [Results,escapeCheck] = playGame(Settings,Results,BallJoystick,BarJoystick,DisplayWindow,cue_color)
% This function is a giant while loop that continues until a result is
% reached: either via the ball crossing the final line or the ball
% hitting the goalie. At that point, the Results struct is
% returned. It takes the Settings, the two Joysticks, the Results
% struct, the current window and the experiment log as inputs. It
% initializes all the relevant variables (BallY/X, BarY/X) in this
% function. It updates TimingSequence, BarY, BallPositions,
% BallJoystickHistory, and BarJoystickHistory each iteration of the
% loop and will add the outcome, trialLength, and trialStart to the
% Results struct.
    % Initialize the trial-related variables.
    [BallX, BallY] = deal(Settings.BallStartingPosX,Settings.BallStartingPosY);
    [BarX, BarY] = deal(Settings.BarStartingPosX,Settings.BarStartingPosY);
    Results.StartOfGame = GetSecs - Results.runStart;
    escapeCheck = false;
    accel = 1;

    if isprop(Results.goalie, 'LagThisTrial')
        % If the goalie has a lag, we record it.
        Results.CpuBarLagThisTrial = Results.goalie.LagThisTrial;
    end
    
    switch Results.Opponent
        % Here, we set the tolerance for the comparison between the goalie's
        % most recent move and their maxMove (if the goalie's most
        % recent move is within tolerance of their maxMove, then
        % acceleration increases, otherwise it stays constant). We
        % need to set the tolerance for the human computer to 1,
        % because the input from the gamepad doesn't always return
        % the max value, even if joystick is jammed as far as it
        % can go. So the move value will not be quite
        % maxMove. Unfortunately, this changes every time and so we
        % cannot consistently calibrate it. For cpu, the tolerance
        % is 1e-12, which is the default (because with cpu, we're
        % just dealing with small precision errors).
      case 'human'
        tol = 1e-1;
      case 'cpu'
        tol = 1e-12;
    end
    
    while Results.outcome == 0,
        % First, check to see if the user wants to quit
        [pressed, firstPress] = KbQueueCheck();
        if pressed && firstPress(KbName('escape'))
            escapeCheck = true;
            return;
        end
        
        % Extract the position of the ball joystick
        BallJoystickPosition = BallJoystick.CalibratedJoystickAxes;
        % Only let the ball move once enough time has passed
        if Results.trialLength > Settings.BallPauseStart
            % Don't let it move outside the screen
            BallX = max([0, min([BallX + Settings.BallSpeed, Settings.ScreenRect(3)])]);
            % BallJoystickPosition will lie between -1 and 1, so we multiply that
            % value by BallSpeed to get the amount it actually moves
            % in a given direction (this ensures that the ball's max
            % vertical speed is the same as its horizontal
            % speed). Also, we don't want to allow any of the ball
            % off the screen.
            BallY = max([0, min([BallY + Settings.BallSpeed*BallJoystickPosition(2), Settings.ScreenRect(4) - Settings.BallDiameter])]);
        end

        % If the trial has been going on for long enough to check, the
        % goalie's moving, and it's moving in the same direction we
        % were during the last refresh, accelerate. We use
        % ismemberf here because precision errors may make them
        % trivially different.
        if (length(Results.BarY) >= 3) && (~ismemberf(Results.BarY(end),Results.BarY(end-1))) && (sign(Results.BarY(end) - Results.BarY(end-1)) == sign(Results.BarY(end-1) - Results.BarY(end-2)))
            switch Results.Opponent
              case 'cpu'
                % We only increase accel if they used their max
                % move, otherwise it stays the same. This is to
                % prevent "teleportations" when the goalie's
                % strategy changes. For computers, we're only
                % dealing with small precision errors.
                if ismemberf(Results.maxMove(end),abs(Results.BarY(end) - Results.BarY(end-1)))
                    accel = accel + Settings.BarJoystickAccelIncr;
                end
              case 'human'
                % When the human is controlling the goalie, we're not only dealing
                % with precision errors, but also issues getting input
                % from the controller. Sometimes, a player will be
                % holding the joystick at the most extreme position
                % and (via JoystickServer) MATLAB does not receive the
                % input as +/-1 (the max value). This problem appears
                % worse on the PC when using WinJoystickMex. To deal
                % with this, instead of looking at the move, which
                % will vary in magnitude much more, we look at the
                % joystick input, since that's where the issue
                % originates. We then increment accel when the
                % joystick input is in [-1, -.8] or [.8, 1] instead of
                % just when its 1 or -1. This should hopefully make
                % acceleration more consistent. I'm less worried about
                % the "teleportation" with the human goalie and more
                % about them being unable to accelerate, so setting
                % larger and larger tolerance values here is fine.
                if ismemberf(abs(Results.BarJoystickHistory(end)),1,'tol',.2)
                    accel = accel + Settings.BarJoystickAccelIncr;
                end
            end
        else
            % Otherwise, reset the acceleration value
            accel = 1;
        end
        Results.accel(end+1) = accel;
        
        % The maxMove value here is the magnitude of the largest possible move
        % the bar could make. Since BarJoystickPosition will lie
        % between -1 and 1, it will be the percentage of the largest
        % possible move. This is also used for the computer, to
        % determine how far it can go in one step.
        maxMove = accel*Settings.BarJoystickBaseSpeed;
        Results.maxMove(end+1) = maxMove;

        % if the goalie is 'human', update the bar position according to the
        % joystick position of Player 2, similar to how we updated
        % the positions of the ball
        if strcmp(Results.Opponent,'human')
            BarJoystickPosition = BarJoystick.CalibratedJoystickAxes;
            % Get the bar position from the joystick.
            BarY = BarY + maxMove*BarJoystickPosition(2);
        else
            % If the goalie is 'cpu', we don't do anything with the
            % BarJoystick. But we still put values here so we can
            % update Results.BarJoystickHistory
            BarJoystickPosition = [0 0];
            % if this is false, then there hasn't been any movement to respond to
            % (and the calls to computer_goalie would throw an error).
            if size(Results.BallPositions,2) > 0
                [BarY, Results.goalie, Results.dest(end+1)] = computer_goalie(Results.goalie,Results.BarY(end),maxMove,Results.BallPositions(2,:),Results.BallPositions(1,:),Results.TimingSequence);
            end
        end
        % We don't want to allow any of the bar off the screen.
        BarY = max([Settings.BarLength/2, min([BarY, Settings.ScreenRect(4) - Settings.BarLength/2])]);
                                             
        % Draw the Ball
        Screen('FillOval',DisplayWindow,[0 255 0], [BallX, BallY, BallX + Settings.BallDiameter, BallY + Settings.BallDiameter]);
        
        % draw bar.
        Screen('FillRect',DisplayWindow, cue_color, [BarX, BarY - Settings.BarLength/2, BarX + Settings.BarWidth, BarY + Settings.BarLength/2]);
        
        % Draw the final line. 
        Screen('DrawLine',DisplayWindow,[255 255 255], Settings.FinalLine, 0, Settings.FinalLine, Settings.ScreenRect(4), 2);
        
        % Check how long the game has gone on for. Need to subtract both
        % Settings.StartOfGame and Results.runStart to get the
        % amount of time (in seconds) passed since Results.StartOfGame
        Results.trialLength = GetSecs - Results.runStart - Results.StartOfGame;
        % Check for result conditions
        if (BallX + Settings.BallDiameter >= BarX) && (BallX <= BarX + Settings.BarWidth) && (BallY + Settings.BallDiameter > BarY - Settings.BarLength/2) && (BallY < BarY + Settings.BarLength/2),
            Results.outcome = 'loss';
            % With the parameter dontclear set to 1, the display will not be
            % overwritten at the next flip, allowing us to add text
            % saying "win" over the final state of the game
            Screen('Flip',DisplayWindow,[],1);
        elseif BallX > Settings.FinalLine - Settings.BallDiameter,
            Results.outcome = 'win';
            % With the parameter dontclear set to 1, the display will not be
            % overwritten at the next flip, allowing us to add text
            % saying "loss" over the final state of the game            
            Screen('Flip',DisplayWindow,[],1);
        else
            % Refresh the PsychToolBox screen.
            Screen('Flip',DisplayWindow);
        end
        
        % Update the timing, position, and joystick variables.
        Results.TimingSequence(end + 1) = GetSecs - Results.runStart - Results.trialStart;
        Results.BarY(end+1) = BarY;
        Results.BallPositions(1:2,end+1) = [BallX, BallY];
        Results.BallJoystickHistory(1:2,end+1) = BallJoystickPosition;
        Results.BarJoystickHistory(1:2,end+1) = BarJoystickPosition;
    end
end

function centered = CenterJoystick(Joystick)
% Check to see if the joystick is y-centered. Since we only use the y
% input, we don't care if x value is centered. Returns true if the
% passed joystick is centered, false if it's not.
% 
% Joystick: the JoystickServer object to check.
    JoystickPositions = Joystick.CalibratedJoystickAxes;
    % CalibratedJoystickAxes has checked if the joystick is within the
    % dead zone and zeroed if it's not, so we can check directly (or,
    % within small tolerance) with zero.
    centered = ismemberf(JoystickPositions(2), 0);
end