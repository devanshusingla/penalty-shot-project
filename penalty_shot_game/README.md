# PenaltyKik task

This contains the files necessary to run the Penalty Kik task

Requirements:

 - MATLAB
 - [PsychToolBox](psychtoolbox.org/)
 - if on Linux:
   [joymex2](http://escabe.org/joomla/index.php/7-projects/matlab/1-joymex2)
   (on Windows, we use PsychToolbox's built-in functions)

This task also uses two third-party functions from the File Exchange:
`ismemberf` and `permn`, which are included in this directory along
with their respective licenses.

For best cross-systems compatibility, should only be run with one
screen (the way PsychToolbox's Screen functions interacts with
multiple screens depends on your OS, but it handles one screen the
same on all OS's).

## The task itself

The best way to understand what the task looks like is to just play it
yourself. On each trial, the participant sees a centered fixation
cross for a jittered amount of time and a picture of their opponent
for a set amount of time before they start playing the game. During
the game, the ball moves forward at a constant rate, with the
participant able to use the joystick they have (the left joystick of
the controller if they're using an XBox or Logitech controller) to
move the ball up and down. The bar / goalie is controlled by either a
computer algorithm or another player using a separate joystick. The
goalie can move only up and down and, while it's initially slower than
the ball, it will accelerate if it continues to move in a given
direction. The game ends when the ball either hits the goalie (and
therefore loses) or makes it to the line behind the goalie (and
therefore wins), at which point small text saying "WIN" or "LOSS"
appears on the screen and the game pauses for a set amount of
time. The next trial then begins with another fixation cross.

## Running the task

First, calibrate the MR joystick by going to Start menu > Devices and
Printers > Right click on USB Input Device (should look like a video
game controller) > click Properties on Mag Design fMRI Joystick, then
go to Settings, Calibrate... and follow the steps. You should have the
participant do this before their anatomical scan, so it's calibrated
for them.

All the code is stored on Munin, but we want to move them to the local
machine to avoid potential timing issues. Copy this whole directory
to the Desktop on the local machine. If you make changes to the task on 
the version stored on the local machine, copy it back to the server. Note
that this is a git repository and therefore you'll want to commit any
changes you make. However, the server computers don't have Github, so
you'll have to do this back on your personal computer.

On the scanner computer, you'll need to make sure that PsychToolbox
has been added to the path and setup. To do this, first make sure that
the variable `PsychToolbox_path` in `Setup_script.m` is correct (if
you're on BIAC5, it should be), then run `Setup_script` (no
arguments). You should then see a bunch of text about setting up
PsychToolbox. If you're not on a PC, this won't do anything. You
should only need to run this once per MATLAB instance: if you have to
quit out of the task code for any reason, you do not need to run
this. However, if MATLAB crashes or you close it, you will.

Next, make sure you know which joystick number corresponds to which
controller. On Linux, you can use `jstest-gtk` (install using
`apt-get`), on Windows you can go into Settings and check. If two
controllers are connected, the script will prompt you to specify which
belongs to which player. Before doing so, it will attempt to open two
controllers and, if using `joymex2`, will display information on their
identity. You can also run `Joystick_Finder.m` to find out joystick
identities. This will require you to jiggle the joysticks, so you must
have access to them. It will also require you to know the total number
of joysticks plugged into your machine (since I can't come up with an
easy way to do that automatically), so have that number on hand.

On BIAC5, it is likely that joystick 0 will be the MR joystick and
joystick 2 will be the XBox controller plugged into the computer
(joystick 1 is presumably the button box?), but you should check every
time just in case.

The data will be stored on your Desktop in a directory called
`PenaltyKik.02-Data`. If this directory does not exist, it will be created.

While the task is playing, press `escape` at any time to quit out. The
task might not quit immediately (because it's in the middle of a WaitSecs
command), but don't mash buttons; it will quit soon. 

We want to have the participant practice during the anatomical
scan. During the anatomical scan, run
`Wrapper_PenaltyKik('anat_practice')`. This will have them play for 4
minutes to get a feel for playing inside the scanner. This data won't
be used to calculate their payout. You'll be asked to specify the cue
order ('br' or 'rb'). Here, you can pick either.

After this, call `Wrapper_PenaltyKik('experiment')` from this
directory when you're ready to begin the functional runs. This only
needs to be run once (it goes through all three runs), but waits for
the experimenter to press the spacebar before each run begins. You'll
be asked to specify the cue order ('br' or 'rb'), which determines
whether the computer's cue and goalie bar are red and Matt's are blue,
or vice versa. This will be counter-balanced across participants, so
refer to your participant log to determine which you should use. You
will also be asked to specify which controller is which; running
Joystick_Finder above should give you those numbers, so just fill them
in. Finally, you'll be asked to specify the participant's number;
again, this should come from your participant log.

With `'experiment'`, we will go through three runs, each of which will
have an equal number of trials with the human and computer
opponent. Each run lasts 12 minutes (not counting that 8 second pause
at the beginning during DISDAQs) and this code will keep starting
trials until within 5 seconds of 12 minutes. The number of trials in a
run varies depending on how long the participant takes to center their
joystick. If they're perfect, with no time required to center, they
will have 70 trials. Each run's results are saved in a separate .mat
file (see [Results](#results) for an explanation of the contents).

Afterwards, run `Payout` to determine the participants bonus. You can
enter the `OutputServer` (where the data is stored) by hand or press
enter to use the default (found in `Settings.mat`) as well as the date
(press enter directly to use today's date), and the subject's
number/name. You'll then need to enter the conversion rate and it
should do everything else automatically. If it can't find an "overall"
.mat file, it will throw an exception. If you don't have an "overall"
file, `Payout` will attempt to load in the individual runs and put
together the required data structure by itself. This should work, but
is less tested.

Finally, copy the resulting data back to Munin. There will be four
.mat files in `Desktop/PenaltyKik.02-Data`: one for each run and one 
"overall". Copy all of these into 
`Munin3/Huettel/PenaltyKik.02/Data/Behavioral/{subj}` (on BIAC5, Munin3 is 
drive `N:\Data`)where {subj} is a new directory you create with that subject's 
BIAC subject number. Then, delete the data from the scanner computer (note
that the data must be in `Desktop/PenaltyKik.02-Data` for `Payout`'s
defaults to work, so it's recommended you calculate the bonuses before
moving the data).

For other possible values of `runType` (the argument to
`Wrapper_PenaltyKik`), see the function's docstring.

Note that the call used to be to `Wrapper_PenaltyKik(runType,
goalieType)`, but we ultimately decided to only use
`goalieType='guess'`. The other `goalieType`s are still implemented
(and the docstring explaining them can still be found in the
`Wrapper_PeantlyKik` function), but they are unused. They are left as
an example if someone wishes to extend the goalie using this
framework.

## Scanning

As of 2016-Jun-29, we've decided to scan on BIAC5 using the slightly
modified GE stock EPI sequence that the Adcock lab uses. We have a 4
minute, 12 second anatomical scan (during which, the participant
practices the task) and three functional runs, each with 4 disdaqs and
lasting 12 minutes.

## Joysticks

The script assumes the first two joysticks plugged into the computer
are joysticks 0 and 1 and can be opened by `joymex2('open',0)` and
`joymex2('open',1)` (on Linux) or `WinJoystickMex(0)` and
`WinJoystickMex(1)` (on PC), respectively. If this is false, it will
throw an error.

XBox and Logitech controllers can be used as is; just plug it in and
go. No need to re-center between trials. The MR joystick might require
some more work: there's a "calibration" that can be done through the
Windows control panel for the device (this should be run, but you
don't need to do anything with the numbers returned by Windows) and
the MR joysticks don't auto-center (the way most joysticks, including
the XBox controller). Before each trial, there will be a screen
requiring the participant to center their joystick. It displays the
text "please center your joystick" and a cross showing the y-location
of the joystick (we only care about the y-location, since x doesn't do
anything in our task).

## Documentation

This README will be kept up-to-date with how to run the
task. Documentation provided by Taylor from the initial version of
this task (run summer and fall 2014) can be found within the docs
folder. `PenaltyKikTaskInstructions.html` is the presentation shown to
participants (`PenaltyKikTaskInstructions.org` is the file that
generated the html file and contains the same information), while
`ExperimenterInstructions.md` is the instructions to the experimenter
for how to run everything.

## Randomness

If we are doing the actual experiment, then we have both human and
computer opponents. We want to randomly alternate between these two
conditions, but still ensure that we have half computer and half human
trials. To do this, we take a cell array with human in half of its
entries, cpu in the other half, and permute it. Each subject and each
run will have a different sequence. This is stored in the `Settings`
struct, while the opponent for the specific trial will be stored in
the `Results` struct (see below).

We also include some jitter in the fixation cross shown before each
trial if `runType == 'experiment'`. We take a vector of observations
from an exponential distribution with a mean of
`Settings.TimeToWaitWithFixCross`, add 1 to every value (so that we're
pulling from an exponential distribution with a minimum value of 1),
then round them all to the nearest .5. Then, on trial `i` we take the
`i`th value of this vector for the jitter. This "master vector" is the
same for all subjects, all runs, but we create a new permutation of
that vector for each subject, each run.  This permuted sequence is
stored in `Settings`, and the jitter for a specific trial will be
stored in `Results`. The master sequence is not saved, but can easily
be re-generated by calling:

```
rng(0)
FixCrossJitterOrder = exprnd(Settings.FixCrossJitterMean,1,Settings.RunLength);
FixCrossJitterOrder = FixCrossJitterOrder + 1;
FixCrossJitterOrder = floor(FixCrossJitterOrder/.5) * .5;
```

For other `runType` values, `FixCrossJitterOrder` will simply be a
vector of 1s, because we will not use those `runType`s for scanning.

# Settings

This describes the list of settings that control the parameters of the
game. When values are given, they are the values found in
`Settings.mat`, the default values, and do not change. If there is no
value, just a description, then the value of that field may change.

## Values specified at run-time

 - `CurrentDateTime`; this is the date-time when the Wrapper was
   called in `DD-Mon-YYYY_HH-MM-SS` format.

 - `runType`: 'train', 'experiment', or 'Vs'; specifies whether the
    participant will be playing an actual experiment, training, or
    playing a versus mode against another player. This is one of the
    required variables passed by the experimenter when calling
    `Wrapper_PenaltyKik`, see the documentation there for more
    details.

 - `goalieType`: 'react', 'hmm', 'hmm_pretrain', or 'guess'; specifies
    how the computer goalie plays the game. This is one of the
    required variables passed by the experimenter when calling
    `Wrapper_PenaltyKik`, see the documentation there for more
    details.

 - `HMMGoalieMemory`: This value determines the length of the HMM
    goalie's memory and, therefore, what its states look like. See
    goalie_hmm.m for more details.
	
 - `HMMPretrainGoaliePath`: the path to the output .mats that should
   be used to pretrain the goalie (only uesd if `goalieType` is
   'hmm_pretrain').
	
 - `P1Name` and `P2Name`: the names of players 1 and 2. Only used when
   `runType` is 'Vs'.

 - `RunLength`: how many trials we should play in a single
    run. Depends on whether `runType` is 'train' or 'experiment'.

 - `OutputServer`: what folder to place the outputs in on the local 
    machine (before copying to server). Exact value depends on OS, but will
    be a directory on the Desktop called `PenaltyKik.02-Data`. Grabbed from 
    `Settings.OutputServerPC` or `Settings.OutputServerLinux`, depending
    on OS. Those two values are then removed from the Settings struct that
    is saved along with the data.

 - `BarJoystickConnected`: whether the second player's joystick (which
    will control the bar) is connected. Set by trying to call
    `Joystick_alias('open',1)` in `Wrapper_PenaltyKik.m`
	
 - `BallJoystickNum` and `BarJoystickNum`: the numbers for the bar and
    ball joysticks. If only one joystick is plugged in, it's assumed
    that `BallJoystickNum=0` and `BarJoystickNum` is unset. If two are
    connected, then we prompt the experimenter to specify these values
    (if `runType=='train'`, then we do not prompt for or set
    `BarJoystickNum`, only `BallJoystickNum`).

 - `OpponentOrder`, the order of opponents used in this run (for
    `runType==trial`, this will be a vector of `'cpu'`s with length
    equal to `RunLength`; for `runType==experiment`, this will be a
    random permutation of `'human'`s and `'cpu'`s with length
    `RunLength). See the [Randomness heading](#randomness) of this
    file for more details.

 - `FirstFixCrossJitterOrder`, the order of jitters (in seconds) used
    for the first fixation cross this run. This is always a
    permutation of the same sequence (since we set the rng seed to 0
    first). See the [Randomness heading](#randomness) of this file for
    more details.
	
 - `SecondFixCrossJitterOrder`, the order of jitters (in seconds) used
   for the second fixation cross this run. This is just a different
   permutation of the same sequence as `FirstFixCrossJitterOrder`.

The following settings are generated at runtime because the resolution
of the screen may vary and we want their relative (not absolute)
proportions to be constant.

 - `ScreenRect`: this is returned by the
   `Screen('OpenWindow')` command from PsychToolbox and is a vector
   containing the min x value of the screen, min y, max x, and max y
   (all in pixels). I.e., this is the screen resolution.

 - `BallDiameter`, this is the width of the screen divided by
   64.

 - `BarWidth`, this is half `BallDiameter`, or the
   width of the screen divided by 128.

 - `BarLength`, this is the height of the screen divided by
   6.

 - `BallStartingPosX`: the x position where the ball starts,
   equal to one eighth of the total screen width

 - `BallStartingPosY`: the y position where the ball starts,
   equal to one half of the total screen height

 - `BarStartingPosX`: the x position where the bar starts,
   equal to 7/8 of the total screen width
 
 - `BarStartingPosY`: the y position where the bar starts,
   the same as BallStartingPosY, equal to one half of the total screen
   height
 
 - `FinalLine`: the x position of the final line, equal to the bar's
   starting x position plus three times the bar's width (so it's
   behind the goalie).

 - `BallSpeed`: how fast the ball moves horizontally, in pixels per
   screen refresh, equal to the width of the screen divided by 100. We
   multiply this by the ball joystick's vertical axis (which lies
   between -1 and 1) to get its vertical move; this ensures the max
   vertical speed is the same as the ball's horizontal speed.
   
 - `BarJoystickBaseSpeed`: the base speed of the goalie. When the
   goalie has no acceleration, this is how fast it moves. Should
   always be smaller than the ball's (since the goalie has
   acceleration and the ball doesn't). Tweaking this value, currently
   equal to `BallSpeed / 1.5`.

 - `BarJoystickAccelIncr`: this is how much the maximum move value
   increases if the goalie continues to move in the same
   direction. This allows the goalie to accelerate, but it loses speed
   when it switches direction. This is being tweaked to find the best
   value, but it's currently `BallSpeed / 60`.
   
 - `ScreenRefreshInterval`: the result of
   `Screen('GetFlipInterval',DisplayWindow)`, this is the approximate
   number of seconds between moves / screen refreshes. We use this to
   let the guess goalie translate between seconds and moves without
   seeing `TimingSequence` (for determining lag)
 
## Default values (found in Settings.mat)

 - `Experiment = 'Penalty Kick'`

 - `OutputServerPC = 'U:\Desktop\PenaltyKik.02-Data'`, the value to use
    for OutputServer on a PC.

 - `OutputServerLinux = '~/Desktop/PenaltyKik.02-Data'`, the value to use for
    OutputServer on a non-PC (ie, Linux or Mac).

 - `FixCrossJitterMean = 2`; this is determines the mean number of
   seconds to wait before the trial starts (with the fixation cross on
   the screen). For each subject, each run, we take permutation of a
   "master vector" of observations from an exponential distribution
   with this mean, add 1 to every value (so that we're pulling from an
   exponential distribution with a minimum value of 1), then round
   them all to the nearest .5. The master vector is the same for all
   subjects, all runs, but the specific permutation is
   different. Then, on trial `i` we take the `i`th value of this
   vector for the jitter.

 - `TimeToWaitAfterOutcome = 1.5`; this is number of seconds to wait
   after the game has ended (ball/bar still displayed).
   
 - `TimeToWaitWithOppPic = 2`; this is the number of seconds to wait
   with the picture of the opponent on the screen.

 - `RewardForBlockingBall = 0.5`; this is the reward obtained by P2
   for effectively blocking the ball

 - `RewardForScoring = 0.5`; this is the reward obtained by P1 for
   reaching the final line

 - `BallJoystickDeadZone = 0.1`; this is a deadzone for the the
   joystick controlling the ball to avoid capturing movements that are
   too small

 - `BarJoystickDeadZone = 0.1`; this is a deadzone for the the
   joystick controlling the bar to avoid capturing movements that are
   too small

 - `ActiveScreen = 0`; the screen we use. everyone sees a mirrored
   version of this.

 - `BallPauseStart = 0.3`; the number of seconds to wait after the
   trial is drawn on screen before the ball start moving. This gives
   the participant some time to examine play before they begin.
   
 - `CpuBarLagMinValue = .12`; the minimum number of seconds that bar's
   tracking of the ball can lag behind the ball's actual
   movements. This is to give it a feeling of "response time", so it
   feels more real.
   
 - `CpuBarLagDist = makedist('Beta',2,5)`; the distribution of
   reaction time values. On a given trial, we take an observation from
   this distribution, multiply it by .1 (because we want values on the
   interval [0, .1]) and add it to `CpuBarLagMinValue` to get the
   cpu's "reaction time" for that trial. The value here is a beta
   distribution with alpha=2, beta=5; to visualize this call
   `histogram(Settings.CpuBarLagDist.random(1,10000))`
   
 - `CpuBarLagDistStruct = struct(CpuBarLagDist)`; the struct
   representation of `CpuBarLagDist`. The distribution object is
   opaque to Python, so we save the struct representation so it can be
   manipulated in Python.
 
 - `BallJoystickGeneration = 0`; whether to reverse the axes of ball
   joystick (see `JoystickServer.m` for more details).

 - `BarJoystickGeneration = 0`; same as `BallJoystickGeneration`,
   except for the bar joystick.

# Results

We also save another struct, which contains the Settings struct at run
time, the `CurrentExperimentLog`, which details each trial, and the
`Results` struct, which contains the following. It will be saved in
`Settings.OutputServer` as
`DD-Mon-YYYY_runType_SubjName_currentRun.mat` , and a separate .mat
will be saved for each subject, each run.

To load the Results struct into Python, use the following:
```
import scipy.io as sio
mat = sio.loadmat("path/to/file/struct.mat",struct_as_record=False,squeeze_me=True)
```

Then, to access the Results struct use `mat['Results']` and to access
the Settings struct use `mat['Settings']`. `mat['Results']` will be an
array with a different struct for each trial (so use
`mat['Results'][0]` to access the results of the first trial). For a
given struct, use dot-syntax to access its values (e.g.,
`mat['Settings'].goalieType`)

## Results struct contents

 - `SubjName`: name of the subject, filled in at prompt at the
   beginning.

 - `currentRun`: what run this struct represents. If `runType` is
   'train' or 'anat_practice', there's only one run; if it's
   'experiment', then there are three.
         
 - `runStart`: the time (returned by PsychToolbox's `GetSecs`) when
   the run started

 - `goalie`: the struct of the goalie object. See `goalie_hmm.m` and
   `goalie_react_guess.m` for descriptions of their properties. Each
   goalie has at least three functions: its constructor;
   `trial_start`, which resets some values and sets values that change
   from trial-to-trial; and `move`, which takes `BallPositions` and
   `TimingSequence` and returns the destination (`dest`) of the
   goalie, as well as the goalie itself (since some properties have
   probably been updated). All properties and other functions are to
   facilitate these three functions. We save it as a matlab struct,
   instead of as the object itself, because objects are opaque to
   Python, while structs can be opened.

 - `trial`: the number of the current trial.

 - `trialStart`: how many seconds after `runStart` this trial started

 - `BarY`: 1xN array, where N is the number of time points in the
    trial. Contains the y position of the bar (x position is constant
    and always `Settings.BarStartingPosX`)

 - `BallPositions`: 2xN array, where N is the number of time points in
   the trial. Contains the x and y position of the bar
   (`BallPositions(1,:)` is the x, `BallPositions(2,:)` is the y).
   
 - `BallJoystickHistory`: 2xN array, where N is the number of time
   points in the trial. Contains the positions of the ball player's
   joystick, first position is x, second is y. Close to 0 is close to
   center.
	
 - `BarJoystickHistory`: 2xN array, where N is the number of time
   points in the trial. Contains the positions of the bar player's
   joystick, first position is x, second is y. Close to 0 is close to
   center. If `Results.Opponent` is 'cpu', then this will be [0 0].

 - `TimingSequence`: 1xN array, where N is the number of time points
   in the trial. The value is the number of seconds since the
   beginning of the trial. 
 
 - `dest`: 1x(N-1) array, where N is the number of time points in the
   trial (this has N-1 values because there's no destination on the
   first trial, since neither of the required vectors (`BallPosition`,
   `TimingSequence`) have been created yet). The value is the y
   position that the goalie is trying to reach, as returned by
   `goalie.move()`. The goalie will move as close as it can to this
   value, constrained by `maxMove`.
   
 - `accel`: 1xN array, where N is the number of time points in the
   trial. The value is the acceleration parameter, which is used to
   calculate `maxMove`. It starts out at 1 and increases by
   `BarJoystickAccelIncr` everytime the goalie is moving the same
   direction it had been going at the previous time point and they
   used traveled their `maxMove` on the previous trial (this ensures
   that the goalie's movements appear smooth; otherwise `accel` can
   get very large while the goalie is moving slowly and, if `dest`
   shifts suddenly (e.g., due to shift in strategy), the goalie can
   appear to "teleport"). If the goalie has not traveled their
   `maxMove`, then `accel` stays at its current value; when the goalie
   stops moving or changes direction, `accel` resets to 1.
 
 - `maxMove`: 1xN array, where N is the number of time points in the
   trial. The value is the maximum possible y distance the bar can
   move, which is equal to `accel * BarJoystickBaseSpeed`. Therefore,
   this increases at the same rate as `accel`.
 
 Note: `BarY`, `BallPositions`, `BallJoystickHistory`,
 `BarJoystickHistory`, `TimingSequence`, `dest`, `accel`, and
 `maxMove` are updated every "time point" in the trial. This
 corresponds to an iteration of the while loop in the `playGame`
 function, which should be the same as a screen refresh. Note also
 that they start accumulating data at start of the game, not the start
 of the trial; there's a fixation cross and a brief image of their
 opponent between the start of the trial and the start of the game. In
 particular, this means the first value of `TimingSequence` will never
 be 0, as some amount of seconds will always have passed before the
 game starts.

 - `RewardBall`: how much reward the ball received on this trial (0.5
   if the ball won, 0 else)

 - `RewardBar`: how much reward the bar received on this trial (0.5 if
   the ball lost, 0 else)

 - `Opponent`: 'cpu' or 'human'; whether the goalie was controlled by
   a human on a second joystick or a computer

 - `outcome`: 'win' or 'loss'; the outcome of the game, with respect
   to the participant/ball. So 'win' means that the ball won, 'loss'
   that the bar won.

 - `StartOfGame`: how many seconds have passed since `runStart`.

 - `trialLength`: how many seconds have passed since `StartOfGame`;
   used to check for timeout.

 - `FixCrossJitterThisTrial`: how many seconds the participant
   waited before the game started with the fixation cross on the
   screen. This is a random number from an exponential distribution
   with `Settings.TimeToWaitWithFixCross` as its mean.

 - `CpuBarLagThisTrial`: how many seconds the bar lags this
   trial. Only set if the goalie is type `react` or `guess`, this
   determines how many seconds behind the current time the goalie
   looks for the ball position to respond to. Different value every
   trial, equal to `CpuBarLagMinValue+.1*CpuBarLagDist.random()` (set
   in `goalie.trial_start()`).
