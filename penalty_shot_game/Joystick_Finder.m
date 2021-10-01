% Joystick_Finder.m
% 
% This little helper function should be run before running the task
% on a Windows machine in order to determine which id refers to
% which joystick. On Linux, because we use joymex2, the console
% will have a brief printout describing the two joysticks. If the
% joysticks are identical so that this is not enough, you should
% run this script.
% 
% Make sure to run Setup_script before this script, otherwise it
% will throw an error (since it will be unable to find any of the
% joystick-related funtions).

function Joystick_Finder()
    display('Enter the number of joysticks connected to test.')
    display('We will test ids 0 through this number-1')
    joystick_max_num = input('Eg, if you enter 2, we will test ids 0 and 1\njoystick_max_num: ');
    for run_idx=1:joystick_max_num
        joy_id = run_idx - 1;
        joystick = JoystickServer(joy_id, .1, 0);
        display(sprintf('We will display input from the left joystick (the one used for this task)\n from joystick joy_id %d.', joy_id))
        display('Mess around with the joysticks until you''ve determined which this is, then press space.')
        fig = figure;
        % Create plot
        p1=plot([0],[0],'x'); hold on;
        title(sprintf('Device %d\nAxis', joy_id))
        axslims = [-1, 1];
        set(gca,'xlim',axslims,'ylim',axslims); axis square
        % Do this until the spacebar is pressed
        while 1
            [~,~,c] = KbCheck;
            if find(c)==KbName('space'); % experimenter presses spacebar
                break;
            end
            joy_axes = joystick.CalibratedJoystickAxes;
            set(p1,'Xdata',joy_axes(1),'Ydata',joy_axes(2));
            drawnow;
        end        
        close(fig);
        % We need a small WaitSecs command here because otherwise the
        % spacebar above can get carried over, resulting in one spacebar
        % skipping through all joystick ids
        WaitSecs(.5);
    end
end