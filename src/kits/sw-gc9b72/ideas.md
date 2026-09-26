# Ideas for the sw-gc9b72 Kit

A short-term list of watch faces and features to build next. Move an idea
to **Done** when it becomes a lab.

## Watch faces

- **Frame-buffer analog face.** Draw the whole analog face in a 253 KB
  RAM buffer with `framebuf`'s filled `ellipse()` and `poly()`, then send it
  in one `blit_buffer()` (about 131 ms). Compare it side by side with lab
  05: RAM for simplicity, with no hand-erasing tricks, and a smooth
  sweeping second hand at about 7 frames per second. The probe already
  confirms a full 360×360 RGB565 buffer fits in RAM.
- **Binary clock.** Hours, minutes, and seconds as rows of lit dots. It
  teaches binary directly, and each second changes only a few dots.
- **Word clock.** "IT IS TWENTY PAST TEN" on a grid of letters, lighting
  only the words that change every five minutes. Encoding how people say
  the time as a table of rules and words is a knowledge-representation
  exercise.
- **Fibonacci clock.** Port the repo's existing `fibonacci-clock` kit to
  the round screen: colored squares that add up to the time.
- **Sun and moon dial.** A 24-hour dial with the daylight hours as a
  colored arc and a marker for the sun's position. Open-Meteo also sends
  `sunrise` and `sunset`, using the same request as `forecast.py`. The
  moon phase can be computed on the Pico with no web service.
- **World clock.** Three or four small dials for chosen cities, using the
  time-zone math in `wifi_time.py`.

## Sound

- **MAX98357A I2S amplifier** (the ones already on hand, as used in the
  stem-robots `max98357a-amp` kit). Proposed wiring, avoiding the buttons
  on GP13-15: BCLK GP10, LRC GP11 (must be BCLK + 1), DIN GP12, with GAIN
  and SD not connected. Then:
  - add the I2S pins to `config.py`
  - write a `sound.py` module that plays tones and short melodies without
    freezing the display
  - give the countdown timer a real alarm (the pentatonic alarm from the
    old `timer` kit)
  - add a speaker test to `01-probe.py`
- **Piezo buzzer**, as a cheaper option: a *passive* piezo on a free pin
  such as GP16, set with `BUZZER_PIN` in `config.py`. The timer already
  supports it.

## Improvements to existing labs

- **Digital face seconds ring.** At the top of each minute, 59 ticks go
  dark in a 0.3 s sweep. Alternating the ring's color each minute would
  make every second change exactly one tick.
- **Stopwatch past 99:59.99.** Switch to H:MM:SS after an hour instead of
  stopping at the limit.
- **Weather clock.** Add the chance of rain (`precipitation_probability_max`)
  and sunrise/sunset times, from the same Open-Meteo request.

