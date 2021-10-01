# Experimenter instructions

Note, this is for the original version of the task, data collected
summer and fall 2014. Copied from a Google Drive file that Taylor had
written up for Dianna. Will not be kept up-to-date, see README
instead.

## Before Scan

### At least 48 hours before

email `BIAC-fund@dm.duke.edu` to request subject payment
- \$65 total: \$45 for participant, \$20 for human opponent.
- include total amount and break into bills (i.e., how many \$20s,
  \$10s, etc).
- it is usually easier to request amount you will need for each week
  at the start of that week.
- also need to request parking passes. You will need more than you
  think. I usually get one per participant -- up to you. It's easier
  to return them than to need them.

### 1 hour before visit

Print out consent forms. They're saved in `PenaltyKik.01/Notes`. You
need fMRI consent form (plus an extra copy in case participant wants
one), behavioral consent form, BIAC screening form, and **2 copies**
of the payment form.

### 20 minutes before visit

Leave to meet participant at the fish tank in the Children's
Hospital. Check to make sure you know their names; there are sometimes
two participants for the two scanners.

## During Scan

- Walk over to testing room across from BIAC6. You will have the room
  reserved.
    - Fill out consent forms.
    - Go over task instructions in power point. **Emphasize the
      importance of centering**.
    - If participant is female, you need to pick up a pregnancy test
      about 5 to 10 minutes before scheduled scan from BIAC6. Knock
      before entering, grab baggy with a cup inside and put it in the
      lunchbox. Walk with participant to the bathroom and wait
      outside. Take lunchbox back from them and put it back on the
      tray in BIAC6.
    - Human opponent should come around 5 to 10 minutes before the
      scan. Have them fill out their consent form
- Walk across hall to BIAC6.
    - Restart testing and eyetracking computers.
    - Plug extension cord into Mach and connect controller.
    - While tech is first setting up, turn on eyetracking camera and
      switch over to Nvideo so eyetracker is shown in the scanner
      (follow chart on the wall). Then when the tech is finished,
      switch back to task.
    - Run `JoyTest` so the participant can practice centering the
      joystick (2016-Apr-04 Note: this file does not seem to exist
      anymore).
    - During the anatomical, run the Training (change Training to `if
      1`, change experiment to `if 0`). Play against the participant
      during the training.
    - Set up the eyetracker:
        - Reset video: Video -> Reset
        - Pause data collection
        - New File: Participant Number (see Screening Form or ask
          Tech); save as `Data Delimited` in `Documents` folder
    - Before the trial, calibrate the eyetracker. Tell Tech and Run
      AutoCalibration
- Run Experiment (Change Training to `if 0`, Experimental to `if 1`).
- Give keyboard to Tech, tell them to press spacebar to start. You
  have to click un-pause data collection to start eyetracker.
- After each run you have to pause data collection. Reenter
  participant number. Then un-pause data collection when tech re-hits
  space bar.
- At the end of the experiment (after 4 runs), the win percentages
  will appear. The first is the participant's win percentage, the
  second is the human goalie's. Both have to be above 33% to receive
  the bonus.
- Close the Matlab window on the testing computer so the participant
  can do their resting state scan.
    - During the resting state, you can fill out human opponent's
      payment form. He will get \$15 + \$5 bonus (if over 33%).
    - Put away the controller and extension cord.
- Copy over output files (from `D:/Data`) and eyetracking file (from
  `Documents`) onto Munin (`/Data`)
- Make sure you pick up all forms for the tech: screening form and
  pregnancy form (if female)
- Walk participant back over to testing room. There they have to fill
  out a qualtrics questionnaire.
- After, fill out the payment form. They will receive \$35 + \$10
  bonus (if over 33%).
- Offer to walk them back to the children's hospital.

## After the Scan
- Subject data is not saved in a folder. Move output data and physio
  into a created folder in Data folder on Munin.
