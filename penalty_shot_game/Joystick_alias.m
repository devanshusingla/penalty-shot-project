% Joystick_alias.m
%
% Because the command is different on Linux and Windows, we need to create
% an alias to handle opening and retrieving input from the joysticks. On
% Linux, we use joymex2 and on Windows (the scanner machine), we use
% PsychToolbox's WinJoystickMex.
% 
% 
% This function has three possible commands:
% 
% - open: open the joystick with number JoystickNum. Return true if
%   this succeded, false if it failed (ie that joystick isn't plugged
%   in)
% 
% - query: return the axes of the joystick with number JoystickNum.
% 
% - close: attempt to close all joysticks (JoystickNum is
%   irrelevant). This only works on Linux (with joymex2), it does
%   nothing on PC. Returns true on Linux (since joysticks were closed)
%   and false on PC (since they weren't).

function return_value = Joystick_alias(command, JoystickNum)
    if ispc
        % If we're using a PC, we use PsychToolbox's
        % WinJoystickMex, which is a simple command
        switch command
          case 'open'
            try
                WinJoystickMex(JoystickNum);
                return_value = true;
            catch
                return_value = false;
            end
          case 'query'
            [x y z buttons] = WinJoystickMex(JoystickNum);
            % Using joymex2, the max possible value is
            % intmax('int16'), the min is -1*intmax('int16') and
            % neutral is 0. Using WinJoystickMex, the min is 0, the
            % max is 2*intmax('int16') and neutral is
            % intmax('int16'). To get this to line up with joymex2,
            % we subtract intmax('int16') from the axes values.
            return_value = struct('axes',[x - double(intmax('int16'));y - double(intmax('int16'))]);
          % on pc, we don't cloes the joysticks, so we simply
          % return false (to signal they're not closed)
          otherwise
            return_value = false;
        end
    else
        % If we're using a Linux machine, use joymex2
        switch command
          case 'open'
            try
                joymex2('open', JoystickNum);
                return_value = true;
            catch
                return_value = false;
            end
          case 'query'
            return_value = joymex2('query', JoystickNum);
          case 'close'
            % Using joymex2, we can close the joysticks.
            clear joymex2
            return_value = true;
        end
    end
end