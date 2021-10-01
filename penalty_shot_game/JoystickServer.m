% JoystickServer
%
% This small class handles getting input from the joysticks, using
% calls to Joystick_alias. On initialization, it opens the joystick
% and sets the properties. It does not provide a function to close the
% joystick, since that is best done by calling
% `Joystick_alias('close')` and that clears all joysticks.
% 
% To use, call JoystickServer (all variables are required). Then, call
% CalibratedJoystickAxes to get the value of from the left joystick to
% use. CalibratedJoystickAxes divides the value by the MaxValue and
% sets anything within the DeadZone to zero before returning; this is
% what is often wanted for use. NOTE that this value will always be
% between -1 and 1 (where -1 is the farthest down/left the joystick
% can be pressed and 1 is the farthest up/right), so it's up to you to
% multiply this value by your "speed"
%
% RawJoystickAxes returns the raw values from the joystick, and is
% only used for testing or determining appropriate MaxValue and
% DeadZone values; it is never called.

classdef JoystickServer
    properties
        % Axes values within the DeadZone (after dividing by the MaxValue),
        % either positive or negative on either axis, are set to
        % 0. This is to make sure the joystick has an appropriate
        % center. 0.1 is a reasonable value.
        JoystickDeadZone
        % The number of the joystick. Joystick numbers seem to be 0-indexed
        % and increase monotonically. If the number doesn't exist,
        % Joystick_alias('open',JoystickNum) will return false
        % (having caught an error)
        JoystickNum
        % Whether to flip the axes. Presumably this depends on the
        % joysticks being used, but this returns the second axes as
        % the x axes and the first as the y, as opposed to the
        % other way round.
        JoystickGeneration
        % Number to divide the joystick axes values by in
        % CalibratedJoystickAxes. Since this value, in any direction,
        % appears to be 32767 (this is intmax('int16') with joymex2,
        % see joytest.m), we divide by this to scale the value
        % returned by the axes between -1 and 1.
        JoystickMaxValue
    end

    methods
        % Initialize the joystick
        function obj = JoystickServer(JoystickNum,JoystickDeadZone,JoystickGeneration)
            Joystick_alias('open', JoystickNum);
            obj.JoystickNum = JoystickNum;
            obj.JoystickDeadZone = JoystickDeadZone;
            obj.JoystickGeneration = JoystickGeneration;
            obj.JoystickMaxValue = double(intmax('int16'));
        end

        % Return the raw axes results. If JoystickGeneration, we will flip
        % them, but otherwise we'll return them untouched.
        function RawJoystickAxes = RawJoystickAxes(obj)
            Temp = Joystick_alias('query',obj.JoystickNum);
            % we need to cast them as doubles for Screen commands (and for
            % multiplication / division to work as we'd expect).
            if obj.JoystickGeneration,
                RawJoystickAxes = double([-Temp.axes(2), Temp.axes(1)]);
            else
                RawJoystickAxes = double([Temp.axes(1), Temp.axes(2)]);
            end
        end

        % Return the processed joystick axes. We divide them by the
        % MaxValue and zero them if they're within the
        % DeadZone. This is the function that's most commonly used.
        function CalibratedJoystickAxesResult = CalibratedJoystickAxes(obj)
            Temp = Joystick_alias('query',obj.JoystickNum);
            if obj.JoystickGeneration,
                x = -Temp.axes(2);
                y = Temp.axes(1);
            else
                x = Temp.axes(1);
                y = Temp.axes(2);
            end
            % x and y are int16s by default; we need to cast them as doubles for
            % Screen commands (and for multiplication / division to work
            % as we'd expect).
            x = double(x);
            y = double(y);
            x = x / obj.JoystickMaxValue;
            y = y / obj.JoystickMaxValue;
            if abs(x) < obj.JoystickDeadZone,
                x = 0;
            end
            if abs(y) < obj.JoystickDeadZone,
                y = 0;
            end

            CalibratedJoystickAxesResult = [x y];
            
        end

    end 
end