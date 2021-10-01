% Payout.m
% 
% This script loads in the relevant data and calculates the
% payout. The experimenter is required to enter in the
% OutputServer, date (or press enter to use today's date), and
% subject number. We then load the overall experiment results
% (thus, all runs must have finished), ask for the conversion rate
% (cents / win) and print out how many trials the subject won
% against human and computer, how many points this means they won,
% and how much their bonus is. We do the same for Matt.

function Payout()
    % The user can either enter the OutputServer or press enter to
    % use the OS-specific default from Settings.mat
    OutputServer = input('Please enter the OutputServer (the directory your results are saved in\n press enter to use OS-specific default from Settings.mat):  ','s');
    Settings = load('Settings.mat');
    if strcmp(OutputServer,'')
        if ispc
            OutputServer = Settings.OutputServerPC;
        else
            OutputServer = Settings.OutputServerLinux;
        end
    end
    Date = input('Enter date in DD-Mon-YYYY format (press enter to use today''s date):  ','s');
    if strcmp(Date,'')
        Date = date;
    end
    subj = input('Enter subject number/name:  ', 's');
    % This looks for the overall .mat that has the correct date and
    % OutputServer, regardless of its time value.
    name = sprintf('%s/%s_*_experiment_%s_overall.mat', OutputServer, Date, subj);
    matches = dir(name);
    if length(matches) == 1
        output = load(sprintf('%s/%s',OutputServer, matches.name));
        opponents = output.opponents;
        outcomes = output.outcomes;
    else
        % Then there's no overall, so we match all with the correct
        % date and subject number (all the individual runs)
        name = sprintf('%s/%s_*_experiment_%s_*.mat', OutputServer, Date, subj);
        matches = dir(name);
        outcomes = {};
        opponents = {};
        for i=1:length(matches)
            tmp_output = load(sprintf('%s/%s', OutputServer, matches(i).name));
            outcomes = cat(2, outcomes, {tmp_output.Results.outcome});
            opponents = cat(2, opponents, {tmp_output.Results.Opponent});
        end
    end
    display(sprintf('Successfully loaded data at %s/%s_experiment_%s_overall.mat\n', OutputServer, Date, subj));
    conversion_rate = input('Please enter how many cents each point is worth:  ');
    % Convert the conversion rate into dollars per point from
    % centers per point.
    conversion_rate = conversion_rate / 100;
    human_mask = strcmp(opponents, 'human');
    display(sprintf('\nSubject %s won:\n   %d trials against the computer\n   %d trials against Matt', subj, sum(strcmp(outcomes(~human_mask),'win')),sum(strcmp(outcomes(human_mask),'win'))))
    display(sprintf('For a total of %d points and a bonus of $%.2f\n',sum(strcmp(outcomes,'win')),sum(strcmp(outcomes,'win')) * conversion_rate))
    display(sprintf('Matt won: %d trials', sum(strcmp(outcomes(human_mask),'loss'))))
    display(sprintf('For a total of %d points and a bonus of $%.2f\n',sum(strcmp(outcomes(human_mask),'loss')),sum(strcmp(outcomes(human_mask),'loss')) * conversion_rate))    
end