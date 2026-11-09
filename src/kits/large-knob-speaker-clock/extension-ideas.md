# Extension Ideas: More Clock-with-Speaker Demos

Ideas for labs to add before the main template, for coding clubs. Each
one uses the speaker in a way that matters, and each teaches one new
programming idea on top of the labs already in this kit.

Adding labs means renumbering `16-main-template.py` to the next free
number and updating every reference to it. Leave the lab numbers in
`sound.py` alone: they refer to the Study Buddy kit's labs.

## Top Five, in Teaching Order

### 1. Reaction-Time Game

After a random delay the screen flashes and the speaker beeps. Press K0
as fast as you can. The screen shows your reaction time in milliseconds
and the best time so far. Pressing too early gets a "wrong" buzz.

- **New idea:** random numbers, plus timing with `time.ticks_ms()` (the
  same way the stopwatch in lab 10 keeps time).
- **Why clubs love it:** it is instantly competitive -- students line up
  to beat each other's score.

### 2. Metronome

Turn the knob to set the beats per minute (40 to 208), and PUSH to change
the beats per bar (2, 3, 4 or 6). The first beat of each bar gets a
higher click, and a pendulum swings on the screen.

- **New idea:** keeping a steady beat by working out when each beat
  SHOULD happen, so it never drifts -- the same idea as the timer in
  lab 09 counting down to its end time.
- **Why it works:** it ties in to music class, and the knob is a natural
  BPM dial.

### 3. Chess Clock

Two players, two buttons: K0 is one player, PUSH is the other. Pressing
your button stops your clock and starts your opponent's. Before the game,
turn the knob to set the time per player. A warning beep sounds when
your time is low, and a buzzer when it runs out.

- **New idea:** two timers in one state machine.
- **Why clubs love it:** clubs play chess and other board games, so it is
  a demo they will actually use.

### 4. Cuckoo Clock

On the hour, a little door opens on the screen, a cartoon bird pops out,
and the speaker plays "cuck-oo" once for each hour. K0 makes it pop out
right now.

- **New idea:** simple animation without a frame buffer -- redraw only
  the parts that move, the same trick as the hands in lab 11.
- **Why it works:** it is charming, and students can design their own
  bird and their own sound.

### 5. Pomodoro Study Timer

25 minutes of work, then a 5-minute break, with a different sound for
each, a tomato that fills up as you go, and a count of the sessions
done. Turn the knob to change the work and break lengths.

- **New idea:** a timer that runs a repeating cycle of states.
- **Why it works:** it is useful for homework, so students keep it on
  their desk.

## More Ideas

- **Morse-code clock:** press K0 and it beeps the time in Morse code
  while showing the dots and dashes.
- **Countdown to a holiday or a birthday:** reuses `lib/holidays.py` and
  plays a fanfare at zero.
- **Interval workout timer:** rounds of work and rest with beeps, for gym
  class.
- **Box-breathing timer:** a calming tone that rises and falls with an
  expanding and shrinking circle.
- **Ship's bells:** strikes 1 to 8 bells every half hour, the way sailors
  kept time on watch.

## Recommendation

If only three get built, start with the **reaction-time game**, the
**metronome** and the **chess clock**. They are the most fun in a group,
and each adds a new idea without repeating the timer lab.

## Design Notes for Any New Lab

- Use the knob to step through values or pages, one step per click, and
  PUSH to go back to the start or to today -- the pattern from
  `14-calendar.py` that worked well on the real board.
- `config.ENCODER_STEPS_PER_CLICK` is 4 on this board.
- Script button presses in the simulator after about 600 ms of fake
  time; scripted knob turns are not reliable there, so feed knob clicks
  in directly when testing.
