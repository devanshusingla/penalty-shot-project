% Wrapper_PenaltyKik.m
% 
% This is the wrapper for the task script. It is what the experimenter
% actually runs: it loads the Settings struct, sets some of their
% values, opens the Screen, monitors runs, gets joystick-related
% values set, calls PenaltyKik_run.m, and then displays and saves
% the overall performance.
%
% Most of these are handled automatically, the only options the
% user needs to specify the runType and goalieType. No defaults are
% included, so both of these are required.
% 
% The runType argument should be a string which specifies how you
% want the task to be played. The following options are currently
% implemented:
% 
%  - 'train': participant play against a computer every trial, to get
%    a feel for the controls. Only one run is played, relatively
%    small number of trials. Fixation crosses between trials all
%    last 1 second.
% 
%  - 'experiment': participant plays against a human and a computer
%    opponent, randomly picking which they play on each trial. This is
%    the mode to use for the actual experiment. This will also include
%    a WaitSecs(16) command before the task gets started, which means
%    the task doesn't start until after the scanner has stabilized (it
%    corresponds to 8 TRs with a TR of 2 seconds). Three runs are
%    played, for 12 minutes each (that WaitSecs not included). The
%    durations of the fixation crosses between trials are jittered
%    (see README/Randomness for more details).
% 
%  - 'anat_practice': for use during the anatomical scan, so the
%    participant can get a feel for how the game is played with the
%    fMRI joystick under the sheet. They will play for 5 minutes
%    (against both human and computer opponets) with the fixation
%    cross up for 1 second each time.
% 
%  - 'Vs': used primarily for testing, participant plays against both
%    human and computer opponents, randomly picking which on each
%    trial. Two trials are played and the control of the bar and ball
%    switches between trials (so both players have the opportunity to
%    play as both bar and ball). Fixation crosses between trials
%    all last 1 second.

 
function Wrapper_PenaltyKik(runType)

%    goalieType is a string that specifies the computer goalie's
%    strategy. It used to be an argument, specified by the user, but
%    in the final version of the task, we always use guess. The
%    following options are currently available:
% 
%    - 'react': the goalie simply tracks the ball, with a small lag to
%       simulate reaction time. This reaction time has its parameters
%       set in Settings (CpuBarLagMinValue and CpuBarLagDist), and
%       every trial the cpu's reaction time is `CpuBarLagMinValue +
%       (.1 * CpuBarLagDist.random())`. In effect, we take the minimum
%       value and add one observation from the distribution (we
%       multiply by .1 because the distribution lies on the interval
%       [0,1] and we want values from the interval [0, .1]).
% 
%     - 'hmm': the goalie uses a hidden markov model to try and
%       predict where the ball will end up. The goalie learns across
%       runs, but starts each subject as completely naive. Read the
%       documentation in goalie_hmm.m for more details.
% 
%     - 'hmm_pretrain': similar to hmm, except the goalie doesn't
%       start completely naive: instead it learns transition
%       probabilities from earlier trials. The paths to these results
%       is stored in Settings.HMMPretrainGoaliePath.
% 
%     - 'guess': this goalie tracks the ball (just like react) up to a
%       certain point and then, once the ball is about to reach the
%       "critical point" where the ball could outrace the goalie
%       (determined analytically based on the ball's speed and the
%       goalie's speed, acceleration, and average reaction time), the
%       goalie makes a guess from five possibilities for what it should
%       do next: continue to track, up-up, up-down, down-up, and
%       down-down. This attempts to emulate how goalies perform in an
%       actual penalty kick: at some point, they just have to
%       guess. The goalie can be set to learn, in which case it will
%       update its probabilities of choosing the different guesses
%       based on what choices it has seen the ball make. THIS IS
%       THE OPTION WE ALWAYS USE.
    goalieType = 'guess';
    
    % We turn this warning off because we're casting our goalie
    % object as a struct for storage and we don't want to be
    % reminded of it everytime.
    warning('off','MATLAB:structOnObject');
    
    % We load the settings struct from Settings.mat (see
    % README.md for a description of the fields it contains)
    Settings = load('Settings.mat');
    
    % This is the current datetime, with all spaces removed
    Settings.CurrentDateTime = strrep(datestr(now),' ','_');
    Settings.CurrentDateTime = strrep(Settings.CurrentDateTime,':','-');
    
    % Our OutputServer differs if we're on a PC or not. Both have been
    % saved 
    if ispc
        Settings.OutputServer = Settings.OutputServerPC;
    else
        Settings.OutputServer = Settings.OutputServerLinux;
    end
    % We don't want to leave these lying around confusing things, so we
    % remove them.
    Settings = rmfield(Settings, 'OutputServerPC');
    Settings = rmfield(Settings, 'OutputServerLinux');
    % Make sure the OutputServer exists
    if exist(Settings.OutputServer, 'dir') ~= 7
        mkdir(Settings.OutputServer);
    end
    
    Settings.runType = runType;
    Settings.goalieType = goalieType;
    
    % We want to counter-balance cue colors across
    % participants. The simplest way to do this is to have the
    % experimenter specify whether the cue colors are 'rb' or
    % 'br'. If 'rb', then the human cue is red and the computer is
    % blue. If 'br', then human is blue and computer is red. These
    % are the only two options, so we keep looping if not.
    Settings.CueColors = '';
    while ~strcmp(Settings.CueColors, 'rb') && ~strcmp(Settings.CueColors, 'br')
        Settings.CueColors = input('What order for cue colors? [rb, br]  ','s');
    end
    
    % Make sure runType is implemented and set the relevant variables.
    switch runType
      case 'experiment'
        % For the fMRI experiment, we want to keep running trials until
        % there's basically no time left; we don't want any dead time.
        % Unfortunately, because different subjects will take different
        % lengths of time to center their joystick, we can't exactly
        % calculate how long each run will be for each subject. We can
        % however, calculate the max number of trials we'd get in one row
        % by assuming they spend no time centering their joystick (ie, they
        % always center it without any feedback on our part). We're aiming
        % for three runs, 12 minutes each, which gives us a theoretical max
        % of 71 trials. This 71 is based on the following calculation:
        % there are two jittered fixation crosses (one before cue and one
        % after; set in FixCrossJitterOrder below; because we use rng(0)
        % both use the same values everytime, and they're both different
        % permutations of this vector, a new one each run; the sum for 71
        % trials is 179 seconds), then there's the opponent picure (2
        % seconds per trial), then the game (averages to a little more than
        % 1.5 seconds each trial), then the time after outcome (1.5 seconds
        % per trial). This gives us 179 + 2*72 + 179 + 1.5*72 + 1.5*72 = 725
        % seconds. 12 minutes is 720 seconds, so this is about what we
        % want. It should be noted that this must be an even number (since
        % OpponentOrder calls repmat with MaxNumberOfTrials/2 as an
        % argument). We also set RunLengthSecs because we need to check our
        % run length so far against it every trial. (The 16 seconds we wait
        % for DISDAQS is not included in the 12 minutes). Upped to
        % 74 for 728 seconds because we added an extra 8 seconds.
        Settings.RunLengthSecs = 728; %the run length in seconds
        Settings.MaxNumberOfTrials = 74; %we still need to set this
        OpponentOrder = repmat({'human','cpu'},1,Settings.MaxNumberOfTrials/2);
        allRuns = 1:3;
        rng(0);
        % This returns a vector of jitter values. We then make sure there are
        % none less than 1 and round them to the nearest half
        % second. Since we set the seed of the rng above, exprnd will
        % return the same sequence every time. Thus, every subject, every
        % run will have a different permutation of the same vector.
        FixCrossJitterOrder = exprnd(Settings.FixCrossJitterMean,1,Settings.MaxNumberOfTrials);
        FixCrossJitterOrder = FixCrossJitterOrder + 1;
        FixCrossJitterOrder = floor(FixCrossJitterOrder/.5) * .5;
      case 'train'
        Settings.MaxNumberOfTrials = 10;
        % For this, we don't care about how long a run takes
        Settings.RunLengthSecs = NaN;
        OpponentOrder = repmat({'cpu'},1,Settings.MaxNumberOfTrials);
        allRuns = 1;
        % If this is runType train, we don't need different jitters, we just
        % want a small length of time between trials.
        FixCrossJitterOrder = repmat(1,1,Settings.MaxNumberOfTrials);
      case 'Vs'
        Settings.P1Name = input('Enter player 1''s name: ','s');
        Settings.P2Name = input('Enter player 2''s name: ','s');
        % Settings.MaxNumberOfTrials = 16;
        Settings.MaxNumberOfTrials = 20;
        % For this, we don't care about how long a run takes
        Settings.RunLengthSecs = NaN;
        % OpponentOrder = repmat({'human','cpu'},1,Settings.MaxNumberOfTrials/2);
        OpponentOrder = repmat({'human'},1,Settings.MaxNumberOfTrials);
        allRuns = 1;
        % allRuns = 1:2;
        % If this is runType Vs, we don't need different jitters, we just
        % want a small length of time between trials.
        FixCrossJitterOrder = repmat(1,1,Settings.MaxNumberOfTrials);
      case 'anat_practice'
        % We want to give participants some time to practice in the
        % scanner. Analagous to case 'experiment', this will last four
        % minutes and so we want to find a reasonable number of
        % trials. 240 seconds (for 4 minutes) and 36 does the trick
        % (1*36 + 2*36 + 1*36 + 1.5*36 + 1.5*36 = 252 and we need an
        % even number greater than 240). For this, each jitter is the
        % same, one second, because we're not using this functional
        % data.
        Settings.MaxNumberOfTrials = 36;
        Settings.RunLengthSecs = 240;
        OpponentOrder = repmat({'human', 'cpu'},1,Settings.MaxNumberOfTrials/2);
        allRuns = 1;
        % If this is runType train, we don't need different jitters, we just
        % want a small length of time between trials.
        FixCrossJitterOrder = repmat(1,1,Settings.MaxNumberOfTrials);
      otherwise
        error('Wrapper:runTypeNotFound','Unclear how to set up runType %s!',runType);
    end

    % We now shuffle the rng so that any further random calls will
    % be different.
    rng('shuffle');

    % Make sure one joystick is connected.
    if Joystick_alias('open',0)
        display('Found first joystick!');
    else
        error('No joysticks connected!');
    end
        
    % Find out if a second joystick is connected. If so, figure out
    % which joystick is being used by which player.
    if Joystick_alias('open',1)
        Settings.BarJoystickConnected = 1;
        display('At least two joysticks connected, above may show joystick details');
        Settings.BallJoystickNum = input('Enter ball joystick''s number and press enter: ');
        if ~strcmp(runType,'train')
            Settings.BarJoystickNum = input('Enter bar joystick''s number and press enter: ');
        end
    else
        Settings.BarJoystickConnected = 0;
        display('Only one joystick connected');
        Settings.BallJoystickNum = 0;
    end
    
    % Unload all joysticks
    Joystick_alias('close', 0);
    
    if ~exist(Settings.OutputServer,'dir')
        mkdir(Settings.OutputServer);
    end
    
    SubjName = inputdlg('Enter the subject number');
    SubjName = SubjName{1};

    outcomes = {};
    opponents = {};
    
    Screen('Preference', 'SkipSyncTests', 0);
    
    % Open up a screen in PsychToolBox. Arrange the settings for the ball, bar,
    % and final line positions based on the resolution of that screen.
    [DisplayWindow Settings.ScreenRect] = Screen('OpenWindow',Settings.ActiveScreen,[0 0 0]);%,[10 100 810 700]);
    ScreenWidth = Settings.ScreenRect(3) - Settings.ScreenRect(1);
    ScreenHeight = Settings.ScreenRect(4) - Settings.ScreenRect(2);
    Settings.BallDiameter = ScreenWidth / 64;
    Settings.BarWidth = Settings.BallDiameter / 2;
    Settings.BarLength = ScreenHeight / 6;
    Settings.BallStartingPosX = ScreenWidth / 8;
    Settings.BallStartingPosY = ScreenHeight / 2;
    Settings.BarStartingPosX = 7*ScreenWidth/8;
    Settings.BarStartingPosY = Settings.BallStartingPosY;
    Settings.FinalLine = Settings.BarStartingPosX + 3*Settings.BarWidth;
    
    %This is how fast the ball moves horizontally. When we get the
    %position of the joystick vertical axis (which lies between -1 and
    %1), we multiply that value by BallSpeed, ensuring that the
    %ball's max vertical speed is the same as its horizontal speed
    Settings.BallSpeed = ScreenWidth / 100;
    
    % To allow for bar acceleration, we start them with a slower speed and
    % an acceleration parameter, which determines how much their
    % speed increases each move they continue in the same direction
    Settings.BarJoystickBaseSpeed = Settings.BallSpeed / 1.5;
    Settings.BarJoystickAccelIncr = Settings.BallSpeed / 90;
    
    % Eventually, we'll either move this into Settings.mat or make
    % it an option passed at runtime. This value determines the
    % length of the HMM goalie's memory and, therefore, what its
    % states look like. See goalie_hmm.m for more details.
    Settings.HMMGoalieMemory = 3;
    Settings.HMMPretrainGoaliePath = {sprintf('%s/04-May-2016_train_react_1.mat',Settings.OutputServer)};

    % We want two different text sizes, one for the cues and win/loss, one
    % for the instructions ("press spacebar to start", "please center
    % joystick"). We base these on the screen size. Text size must not
    % be fractional, so we floor it.
    Settings.CueTextSize = floor(ScreenHeight / 20);
    Settings.InstructionsTextSize = floor(ScreenHeight / 35);

    
    % We store the screen refresh interval because this is an
    % approximation of the time between moves. It allows the goalie to
    % use this value without having to actually see the TimingSequence.
    Settings.ScreenRefreshInterval = Screen('GetFlipInterval',DisplayWindow);

    % Initialize the goalie
    switch Settings.goalieType
      case 'hmm'
        goalie = goalie_hmm(Settings.HMMGoalieMemory,Settings.BallStartingPosY,Settings.BallStartingPosX,Settings.ScreenRect(4),Settings.BarStartingPosX);
      case 'hmm_pretrain'
        goalie = goalie_hmm(Settings.HMMGoalieMemory,Settings.BallStartingPosY,Settings.BallStartingPosX,Settings.ScreenRect(4),Settings.BarStartingPosX);
        % pretrain the goalie.
        goalie = goalie.pretrain(Settings.HMMPretrainGoaliePath);
      case 'react'
        goalie = goalie_react_guess('react',false,1,Settings.CpuBarLagMinValue,Settings.CpuBarLagDist,Settings);
      case 'guess'
        goalie = goalie_react_guess('guess',true,1,Settings.CpuBarLagMinValue,Settings.CpuBarLagDist,Settings);
      otherwise
        % Else, we're not sure what kind of goalie we want
        error('Unclear how to use goalieType %s!',goalieType);
    end
    
    HideCursor(DisplayWindow);
    % This is only a function in the Windows version of
    % PsychToolbox. Fortunately, on Linux, it's not necessary, so we
    % don't need a catch block.
    if ispc
        ShowHideWinTaskbarMex(0);
    end

    % We use KbQueue to check for button pressing, so get them started.
    KbQueueCreate();
    KbQueueStart();

    % Iterate through the runs we specified (all differences
    % between train and experiment run have already been set above)
    for currentRun = allRuns,
        % We generate a new order for the opponents and jitters every run.
        
        % This ensures we have a random ordering of our opponents, but we will
        % have exactly half and half human and cpu opponents (unless
        % runType is train, then they're all cpu)
        Settings.OpponentOrder = OpponentOrder(randperm(Settings.MaxNumberOfTrials));
        
        % This is a random permutation of the FixCrossJitterOrder vector.
        Settings.FirstFixCrossJitterOrder = FixCrossJitterOrder(randperm(Settings.MaxNumberOfTrials));
        Settings.SecondFixCrossJitterOrder = FixCrossJitterOrder(randperm(Settings.MaxNumberOfTrials));
        
        [Results,escapeCheck] = PenaltyKik_run(Settings,SubjName,currentRun,DisplayWindow,goalie);

        % Unload all joysticks
        Joystick_alias('close', 0);

        % If the experimenter pressed, escape, we don't want to
        % gather overall results
        if escapeCheck
            break
        end
        
        % We add the outcomes (and opponents) of our trials onto our running
        % list of outcomes (and opponents). If runType is 'Vs', we
        % want to keep each run on a different dimension to make them
        % easy to separate (else, we treat all runs as the same) and
        % we want to switch the joysticks used for bar and ball.
        if strcmp(runType,'Vs')
            outcomes = cat(1,outcomes,{Results.outcome});
            opponents = cat(1,opponents,{Results.Opponent});
            tmp = Settings.BarJoystickNum;
            Settings.BarJoystickNum = Settings.BallJoystickNum;
            Settings.BallJoystickNum = tmp;
        else
            outcomes = cat(2,outcomes,{Results.outcome});
            opponents = cat(2,opponents,{Results.Opponent});
        end
    end
    

    if ispc
        ShowHideWinTaskbarMex(1);
    end
    
    % Stop the KbQueue from getting inputs and flush it
    KbQueueStop();
    KbQueueFlush();
    Screen('CloseAll');

    % If escape was pressed, we don't want to calculate win
    % percentages and we just quit.
    if escapeCheck
        return
    end
    
    % This calculation works regardless of the shape of the
    % outcomes array.
    BallWinPercentage = sum(strcmp(outcomes,'win'),2) / size(outcomes,2);
    if strcmp(runType,'Vs')
        % The ball win percentages for player 1 and player 2 have different
        % indices.
        [P1BallWinPercentage P2BallWinPercentage] = deal(BallWinPercentage(1),BallWinPercentage(2));
        % Because if the runType is Vs, the players will play as both
        % bar and ball, we need to do this bit of nonsense to
        % calculate their win percentages separately. On the plus
        % side, BarWinPercentage will never be Inf
        [P1outcomes P2outcomes] = deal(outcomes(1,:),outcomes(2,:));
        [P1opponents P2opponents] = deal(opponents(1,:),opponents(2,:));
        % We only calculate the bar's win percentage based on the games that
        % they actually played in, ie those with a human opponent. We
        % have to do P1outcomes and P2outcomes because using logical
        % indexing with a muldimensional cell array of dimension 2xN
        % returns an array of Mx1, where M is the number of included
        % values. P1 is the bar when P2 is the ball (hence, during
        % P2opponents and P2outcomes)
        P2BarWinPercentage = sum(strcmp(P1outcomes(strcmp(P1opponents,'human')),'loss')) / sum(strcmp(P1opponents,'human'));
        P1BarWinPercentage = sum(strcmp(P2outcomes(strcmp(P2opponents,'human')),'loss')) / sum(strcmp(P2opponents,'human'));
        
        % display the results
        msgbox({sprintf('%s''s win percentage as ball: %3.1f%%',Settings.P1Name,100*P1BallWinPercentage),sprintf('%s''s win percentage as bar: %3.1f%%',Settings.P1Name,100*P1BarWinPercentage),...
                sprintf('%s''s win percentage as ball: %3.1f%%',Settings.P2Name,100*P2BallWinPercentage),sprintf('%s''s win percentage as bar: %3.1f%%',Settings.P2Name,100*P2BarWinPercentage)},'Results');
        
        % Create the struct containing the vars we want to save
            save(sprintf('%s/%s_%s_%s_overall.mat',Settings.OutputServer,Settings.CurrentDateTime,Settings.runType,SubjName),...
                 'P1BarWinPercentage','P1BallWinPercentage','P1outcomes','P1opponents',...
                 'P2BallWinPercentage','P2BarWinPercentage','P2outcomes','P2opponents');
    elseif strcmp(runType,'experiment')
        % If runType is experiment, then we also want to calculate the Bar's
        % win percentage.  We only calculate the bar's win percentage
        % based on the games that they actually played in, ie those
        % with a human opponent
        BarWinPercentage = sum(strcmp(outcomes(strcmp(opponents,'human')),'loss')) / sum(strcmp(opponents,'human'));
        
        % display the results
        msgbox({sprintf('Ball player''s win percentage: %3.1f%%',100*BallWinPercentage),sprintf('Bar player''s win percentage: %3.1f%%',100*BarWinPercentage)},'Results');
        
        save(sprintf('%s/%s_%s_%s_overall.mat',Settings.OutputServer,Settings.CurrentDateTime,Settings.runType,SubjName),...
             'BarWinPercentage','BallWinPercentage','outcomes','opponents');
    elseif strcmp(runType,'train')
        % if runType is train, we only need to calculate the
        % BallWinPercentage, since there was no bar player.
        msgbox(sprintf('Ball player''s win percentage: %3.1f%%',100*BallWinPercentage),'Results');
        
        save(sprintf('%s/%s_%s_%s_overall.mat',Settings.OutputServer,Settings.CurrentDateTime,Settings.runType,SubjName),...
             'BallWinPercentage','outcomes','opponents');
    end
end