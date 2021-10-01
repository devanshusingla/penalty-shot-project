% Setup_script.m
% 
% A small script that should be run before the experiment on the
% scanner computer to get PsychToolbox run. It won't do anything on
% non-PCs, since the commands are different and the scanner
% computers are PCs.
% 
% Before use, make sure that the variable PsychToolbox is correct.

if ispc
    display('Running PC setup');
    current_dir = pwd;
    PsychToolbox_path = '/usr/share/psychtoolbox-3';
    addpath(PsychToolbox_path);
    cd(PsychToolbox_path);
    run('SetupPsychtoolbox');
    cd(current_dir);
else
    display('Adding JoyMEX to path');
    addpath('../JoyMEX-Linux/');
end