---
title: Guide to Multicore Processing on the Study Buddy
description: How the Study Buddy's two processor cores, its PIO and DMA hardware, and the I2S bus work together so the display, WiFi, and sound run smoothly side by side. Includes every measurement taken so far, what MicroPython's source says, and what is still unproven.
---

# Guide to Multicore Processing on the Study Buddy

The Study Buddy has to do three demanding things at once: **draw on the
screen**, **talk over WiFi**, and **play sound without a single click**. This
guide explains how the Pico 2 W's two processor cores, its PIO state
machines, and its DMA controller can share that work, what we have measured
so far, and what is still unproven.

!!! note "How to read the labels in this guide"
    Every claim carries one of four labels, because they are not equally
    trustworthy:

    - **Measured**: run on the real kit (Pico 2 W, MicroPython 1.29.0,
      2026-10-04 to 2026-10-06), with the numbers shown.
    - **Source**: read in the MicroPython v1.29.0 source files named in
      [Sources](#sources). I read them through a tool that fetches a file and
      answers questions about it, so these are summaries, not line-by-line
      reads. The function and macro names are worth confirming in the files
      before any design decision rests on a single detail.
    - **Datasheet**: from my memory of the RP2350 and flash datasheets.
      Check before relying on a number.
    - **Hypothesis**: reasoning, not yet tested. Each one has an experiment
      in [Experiments to run](#experiments-to-run).

    This guide is for teachers and developers. It is not student-facing.

## The Short Version

1. **Both cores run in parallel.** The same loop took 1014 ms on core 0
   alone and 1024 ms on core 1 alone; with both running at once each took
   1121 ms. The RP2 port builds MicroPython with the global interpreter lock
   turned off. (Measured, Source)
2. **Sound fed from core 1 survives anything that freezes core 0 in
   ordinary or long C code**: a 1.2 s freeze, 20 garbage collections, a
   9.5 s WiFi connect, and 17 to 21 full-screen repaints all left at least
   248 of 256 ms in reserve. The same freeze made the core-0 version run dry.
   (Measured)
3. **There is one exception, and it is the important one: flash writes.**
   While MicroPython erases or programs flash it disables interrupts and
   pauses core 1. The I2S driver depends on a CPU interrupt that fires about
   every 2 ms to keep a tiny hardware buffer full, so a flash write cuts the
   sound *no matter which core feeds it*. **Confirmed by ear**: a listener
   heard a click or gap in all three phases that wrote flash (5 small
   writes, one 200 KB write, and a mixed load), and in none of the other six.
   In those phases the ring buffer never ran dry (its low point was 27 to
   168 ms), so the glitch happened *after* the ring, at the interrupt-fed DMA
   buffer, exactly where the source said the weak link was.
   (Measured, Source)
4. **PIO and DMA already do most of the work of moving sound to the
   speaker, but not all of it.** The PIO makes the I2S clocks and shifts out
   the bits, and DMA moves words into the PIO. A CPU interrupt still refills
   the DMA buffer, and that last step is the weak link. (Source)
5. **The display, WiFi, and sound work smoothly together, with the flash
   exception.** In `multicore-stress-test.py` a steady tone stayed clean, by
   ear and by counter, through 23 full-screen repaints, three WiFi scans, a
   5.8 s WiFi connect with time sync, a web request, and 20 garbage
   collections. (Measured)
6. **The sound is not free for core 0.** With the audio loop running, a
   150,000-step loop on core 0 took **6.4% longer** with silence playing,
   **7.1%** with a 16 kHz tone, and **9.8%** with a 44.1 kHz tone. Most of it
   is core 1 busy-waiting on shared memory. (Measured)

!!! warning "Two corrections to things I said earlier"
    - I wrote that the core-1 audio loop "sleeps inside `write()`". It does
      not: in blocking mode `write()` **busy-waits** in a C loop until there
      is room. It is harmless, but the loop keeps core 1 100% busy. The code
      comment and the audio page have been fixed. (Source)
    - I told you the reserve protects the sound through a flash write. It
      does not: see [Flash: the exception](#flash-the-exception).

## The Three Workloads

| Workload | What it does to the processor | What it needs from the processor |
|---|---|---|
| **Display** | A full-screen fill sends 259,200 bytes over SPI. It takes about **130 ms**, and core 0 spends it waiting. | Core 0, in blocks of up to 130 ms. (Measured) |
| **WiFi** | A connect plus time sync took **9.45 s** on core 0. The wireless chip is run by interrupts and a PIO-driven link. | Core 0, in blocks of seconds. (Measured, Datasheet) |
| **Sound** | Needs a fresh sample every 62.5 µs at 16 kHz, or 22.7 µs at 44.1 kHz, forever. | A refill every **~2 ms** (hardware level) and a new chunk every 64 ms (software level). (Source, Measured) |

The sound is the strictest tenant. It has the hardest deadline, and it
shares a chip with two others that freeze the main core for tens to
thousands of milliseconds. That is why it does not run on core 0.

### The deadline ladder for sound

There are three buffers between your program and the speaker, and each has
its own deadline. This ladder is the key to everything that follows.

| Stage | Where it lives | How long it can run dry | Who feeds it |
|---|---|---|---|
| **Our chunk** | `sound.py`'s 1024-sample buffer | 64 ms at 16 kHz | Core 1 (our loop) |
| **The ring buffer** (`ibuf`) | RAM, 8192 bytes by default | **256 ms** at 16 kHz | Core 1, by `write()` |
| **The DMA buffer** | RAM, 256 bytes in two halves of 128 | **2.0 ms** at 16 kHz, 0.73 ms at 44.1 kHz | **A CPU interrupt, on core 0** |
| **The PIO FIFO** | Inside the PIO | a few samples | DMA, in hardware |

Everything we measured so far tested the top two rungs. The third rung, the
2 ms one, is where a flash write bites.

## The Hardware You Have

| Resource | What the Pico 2 W has | Used by the Study Buddy |
|---|---|---|
| **Cores** | 2 Arm Cortex-M33 at 150 MHz (Measured: `machine.freq()`) | Core 0: program, display, WiFi, files. Core 1: the audio loop. |
| **SRAM** | 520 KB; MicroPython's heap is about 436 KB (Measured) | One shared heap for both cores |
| **PIO** | 3 blocks of 4 state machines (Datasheet) | The WiFi chip link, and I2S |
| **DMA** | 16 channels (Datasheet) | The display's SPI writes, I2S (2 channels), and WiFi |
| **SPI0** | Hardware SPI on GP2 and GP3 | The display |
| **Flash** | 4 MB (Measured); the code and files live here and are read through a cache called XIP | Everything, including the filesystem |

Three facts about this hardware explain most of what you will see:

- **The two cores share the same memory and the same heap.** There is no
  fence between them. (Source: `mpthreadport.c` guards shared state with a
  recursive mutex while core 1 is active.)
- **The PIO, DMA, and cores all run at the same time.** A PIO state machine
  keeps running while both cores are busy, and DMA keeps copying while the
  CPU is stuck. This is the whole basis of the "offload" idea.
- **Code runs out of flash.** While flash is being written, nothing can run
  from it, so the chip must stop both cores and turn off interrupts. This is
  the cause of the flash problem.

## How the I2S Bus Works

I2S (say "I-squared-S") is a three-wire way to send digital audio from one
chip to another. It was designed for exactly this job: a processor handing
sound to a DAC or an amplifier. Our MAX98357A amplifier has the DAC and the
speaker driver in one chip, so the only wires are:

| Wire | Pico pin | Name on the amp | What it carries |
|---|---|---|---|
| **BCLK** | GP20 | BCLK | **Bit clock.** One tick for every bit of audio. |
| **WS** | GP21 | LRC | **Word select.** Says which channel the bits are for: low is left, high is right. |
| **SD** | GP19 | DIN | **Serial data.** The sample bits themselves, most significant bit first. |

A **sample** is one number that says how far the speaker cone should be
pushed at one instant. At 16,000 samples a second the Pico sends 16,000 of
them every second, one for each tick of the sample clock.

### One frame

I2S always sends two channels, left then right, even for mono sound. One
**frame** is one left sample plus one right sample, 16 bits each:

```text
           |<-------------- one frame: 32 BCLK ticks -------------->|

 BCLK    _|‾|_|‾|_|‾|_|‾|_|‾|_|‾|_ ... one tick for every bit ... |‾|_|‾|_

 WS      ____________________________                 ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
         |<------ LEFT (low) ------>|<----- RIGHT (high) ------->|<- next LEFT

 SD      --< b15 b14 b13 ... b1 b0 >--< b15 b14 b13 ... b1 b0 >--<
              16 bits, MSB first          16 bits, MSB first
```

The details that matter:

- **WS changes one tick *before* the first bit** of its channel. The data line
  changes on the falling edge of BCLK and the amplifier reads it on the
  rising edge. This is the "Philips" I2S format.
- **The bit clock is not a free-running number. It is 32 times the sample
  rate**, because each frame has 32 bits:

  | Sample rate | BCLK | Frames per second | One frame lasts |
  |---|---|---|---|
  | 16,000 Hz | 512 kHz | 16,000 | 62.5 µs |
  | 22,050 Hz | 705.6 kHz | 22,050 | 45.4 µs |
  | 44,100 Hz | 1.4112 MHz | 44,100 | 22.7 µs |

- **The amplifier needs no master clock.** The MAX98357A works out its
  timing from BCLK and WS, which is why only three signal wires are needed.
- **Mono is sent twice.** MicroPython's mono format copies each sample into
  both slots. The amplifier averages left and right (the SD pin is left
  unconnected), so the result is the same sound at full level. (Source)

### Why LRC must be the pin after BCLK

MicroPython drives BCLK and WS from a **single instruction** using the PIO's
"side-set" feature, which sets a group of **adjacent** pins at once. So the
two pins must be neighbors, with WS one higher than BCLK. The MicroPython
code checks this directly and raises an error if `ws != sck + 1`.
(Source: `machine_i2s.c`, and the MicroPython docs: "The `ws` pin number
must be one greater than the `sck` pin number".) Your wiring (BCLK on GP20,
LRC on GP21) follows the rule, and lab 02 checks it.

## How MicroPython Moves Sound on the Pico

This is the real path a sound takes. Read it from the top:

```text
  core 1                          core 0                       hardware
 ┌─────────────────────┐
 │ sound.py loop       │
 │  _fill(): synthesize│
 │   1024 samples with │
 │   viper machine code│
 │  _audio.write(buf)  │──┐
 └─────────────────────┘  │
                          ▼
              ┌───────────────────────┐
              │ RING BUFFER (ibuf)    │  8192 bytes in RAM
              │ 256 ms at 16 kHz      │  one writer, one reader
              └───────────────────────┘
                          │  every ~2 ms
                          ▼
              ┌───────────────────────┐
              │ DMA IRQ HANDLER       │  runs on CORE 0 (the core
              │ feed_dma(): copy 32   │  that created the I2S object)
              │ frames, duplicate     │
              │ mono into both slots  │
              └───────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ DMA BUFFER 2 x 128 B  │  two DMA channels, chained:
              │ ping-pong             │  when one finishes the other starts
              └───────────────────────┘
                          │ DMA, no CPU
                          ▼
              ┌───────────────────────┐
              │ PIO TX FIFO           │
              └───────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ PIO state machine     │  8 instructions; makes BCLK and WS
              │ (the I2S program)     │  and shifts the bits out on SD
              └───────────────────────┘
                          │  three wires
                          ▼
                   MAX98357A  →  speaker
```

(Source: `ports/rp2/machine_i2s.c` and `extmod/machine_i2s.c`, v1.29.0.)

### The numbers behind the picture

| Sample rate | PIO clock needed | Divider from 150 MHz | DMA refills per second | Time between refills |
|---|---|---|---|---|
| 16,000 Hz | 1.024 MHz | 146.5 | 500 | **2.0 ms** |
| 22,050 Hz | 1.411 MHz | 106.3 | 689 | 1.45 ms |
| 44,100 Hz | 2.822 MHz | 53.1 | 1378 | **0.73 ms** |

The PIO clock is `rate × 2 channels × 16 bits × 2 PIO instructions per bit`,
because the program takes two instructions per bit (one with the clock low,
one with it high). Each DMA half-buffer holds 32 frames, so a refill is due
every `32 / rate` seconds. (Source for the formula; the table is arithmetic.)

!!! tip "Why this matters for the display and WiFi"
    A 44.1 kHz sound asks core 0 to service an interrupt **1378 times a
    second**, each one copying 32 frames. That is a steady, small tax on
    core 0 that we have *not* measured (see experiment E4). It is paid on
    core 0 even when core 1 is the one making the sound.

### What happens when the ring buffer runs dry

If the DMA interrupt finds the ring buffer empty, MicroPython fills the DMA
buffer with **zeros**, so the speaker gets silence, not a repeat of the old
sound. (Source: `memset` in the TX path.) That is the "underrun" the stats
counters watch for at the *ring* level. If the DMA interrupt does not run
at all, the DMA buffer empties and the PIO **stalls** waiting for data:
BCLK and WS stop. The amplifier hears the clocks vanish, which is a harder
failure than a few zeros. (Source for the stall behavior: a `pull` blocks on
an empty FIFO; Hypothesis for what the amplifier does about it.)

### Blocking `write()` is a busy-wait

In blocking mode (no `irq` handler set, which is how core 1 uses it),
`write()` copies bytes into the ring buffer one at a time, and when the ring
is full it simply loops: `while ringbuf_push(...) == false {;}`. There is no
timeout, no sleep, and no call into the scheduler. (Source:
`extmod/machine_i2s.c`.) Two consequences:

- **Core 1 is always at 100%.** It does a little synthesis, then spins until
  the DMA interrupt on core 0 drains enough of the ring. It cannot be
  interrupted by Ctrl-C and cannot run scheduled callbacks. (Source)
- **It reads shared memory constantly.** Spinning on the ring buffer's
  indices competes with core 0 for the memory bus. We have not measured the
  cost (experiment E3).

The ring buffer is safe between the two cores because it is built as
**single producer, single consumer**: core 1 only writes, the interrupt only
reads, and neither touches the other's index. (Source: the header comment in
the ring buffer code.)

## The PIO: What It Is and What It Does Here

The **PIO** (Programmable I/O) is a set of tiny processors, called state
machines, built for one job: wiggling pins with exact timing. Each has:

- a handful of instructions (`pull`, `out`, `set`, `jmp`, `wait`, `nop`) and
  a shared 32-instruction memory,
- **FIFOs** (small queues) to exchange words with the CPU or DMA,
- a **clock divider**, so it runs at whatever speed the protocol needs,
- **side-set**: extra pins that change *during* any instruction at no cost,
  which is how BCLK and WS are made at the same moment the data bit is
  shifted.

A state machine runs **by itself**. It does not need either core, does not
read flash, and does not care about interrupts being disabled. That is why
PIO is the right tool for I2S, SPI, and WS2812 LEDs.

### The I2S program, in words

MicroPython's 16-bit I2S program is 8 instructions long. Reading it as a
loop, for each bit of the frame it does the following, with BCLK low for one
instruction and high for the next:

1. take the next bit from the shift register and put it on SD,
2. drive BCLK low and WS (set for the right channel) in the same
   instruction, using side-set,
3. drive BCLK high,
4. when 16 bits have gone out, `pull` the next 32-bit word from the FIFO
   (which holds a left and right sample together).

(Source for the length and side-set; the instruction-by-instruction story is
my reading of how such a program works, not a transcription.)

### Who does what

| Task | Who does it | CPU cost |
|---|---|---|
| Make BCLK at 32 × the sample rate | **PIO** | none |
| Make WS in step with the data | **PIO** (side-set) | none |
| Shift each sample out, bit by bit | **PIO** | none |
| Copy words from RAM into the PIO FIFO | **DMA** | none |
| Swap between the two DMA halves | **DMA** (chained channels) | none |
| **Refill the DMA half-buffer from the ring** | **CPU interrupt, core 0** | ~500 to 1400 a second |
| Put new samples in the ring | CPU, core 1 (`write()`) | busy-waits |
| **Calculate the samples** | CPU, core 1 (viper) | small (E4) |
| Keep the amplifier configured (GAIN) | none (a GPIO level) | none |

So the hope is **mostly** realized: the bit-level work and the transfer into
the FIFO are fully offloaded. The weak link is the sixth row: a CPU
interrupt, with a 2 ms deadline, that stands between the large ring buffer
and the tiny DMA buffer.

## Flash: the Exception

Code runs from flash. To erase or write flash the chip must stop reading it,
so the MicroPython flash driver does this for every erase and write:

1. pause core 1 (`multicore_lockout_start_blocking()`),
2. disable interrupts on the calling core (`save_and_disable_interrupts()`),
3. call the ROM erase or program routine,
4. restore both.

(Source: `begin_critical_flash_section()` in `ports/rp2/rp2_flash.c`.) Core 1
is registered as a lockout "victim" so this works. (Source: `mpthreadport.c`.)

Put that next to the deadline ladder:

| Event | Lasts | The DMA interrupt can run? | Result |
|---|---|---|---|
| One flash **page program** (256 bytes) | roughly 0.5 ms (Datasheet) | no | tight, but inside 2 ms at 16 kHz and not inside 0.73 ms at 44.1 kHz |
| One flash **sector erase** (4096 bytes) | tens of ms (Datasheet; each of ours was less than 139 ms, the whole 40 KB write) | **no** | the DMA buffer empties in 2 ms, so **silence, and the PIO stalls** |

The reserve in the ring buffer does not help here, because the ring is not
the problem: the sound sits in it, safe, but the interrupt that carries it
across to the DMA buffer is the thing that cannot run. And core 1 is paused
as well, so it would not even keep the ring topped up.

**What we measured, in two steps.**

*Step 1, on 2026-10-05 (counters only).* A 40 KB write and delete took 139 ms
while a tone played on core 1, with 0 underruns and a reserve that never fell
below 250 ms. Nobody was listening. I called that "consistent with a glitch we
did not detect", which turned out to be right.

*Step 2, on 2026-10-06 (counters and ears).* `multicore-stress-test.py`
played a steady tone and asked the listener, after each phase, whether they
heard a click or gap:

| Phase | Took | Reserve at its lowest | Longest wait for core 1 | Heard a problem? |
|---|---|---|---|---|
| 5 small writes (4 KB each) | 2745 ms | 168 ms | 121 ms | **yes** |
| one 200 KB write | 695 ms | 56 ms | 148 ms | **yes** |
| everything in turn | 5830 ms | 27 ms | 92 ms | **yes** |

Two things in that table matter.

- **The counters did notice something this time.** Core 1 was paused by the
  lockout, so its supply fell behind: the reserve dropped to 56 ms and 27 ms,
  and the longest wait stretched to 148 ms. In the earlier step the write was
  smaller and nothing showed. How long a write blocks depends on whether the
  filesystem has to erase a block first, so it varies from write to write.
- **The ring buffer never ran dry, and the listener heard it anyway.**
  Underruns stayed at 0 and the reserve never reached 0. A glitch with sound
  still in the ring can only have happened *after* the ring: in the DMA
  buffer that the stalled interrupt could not refill. That is the mechanism
  the source pointed to, and it is why a bigger ring would not fix it.

**Conclusion.** Every flash write while a sound plays is audible, on either
core. Progress saves, a Library download, and a log file would each do it.

**One thing still unknown: does a flash write during silence pop?** The audio
loop feeds zeros when nothing is playing, so the DMA buffer and the PIO are
still running. If the interrupt is blocked, the PIO stalls and the clocks
stop, which might make the amplifier pop even though the sound is silent.
The rule "do not write while a sound plays" only works if that is clean.
Experiment E10 tests it.

### What to do about it now

- **Do not write flash while a sound is playing.** (Confirmed necessary.) Wait for `sound.busy()`
  to be false, then write. Save the quiz progress at the end of a round,
  which is already the plan, and keep downloads away from sounds.
- **Play the "done" chime after a download, not during.**
- If E1 confirms a glitch, `sound.py` should offer a call that quiets the
  speaker (ramps to silence, writes, ramps back) so a short glitch is a
  smooth dip instead of a click. (Proposal)

## What We Measured

### Method, and a mistake worth recording

Every test that touches the board runs under a hard timeout, and each one
does a *bounded* amount of work. That rule came from a mistake. My first
two-core test used `sum(range(12_000_000))` as a way to keep core 0 busy. On
MicroPython the running total outgrows small integers after about 46,000
terms, and every addition then allocates on the heap, so it took **66
seconds** (measured at 9 million terms). The board looked dead, I killed the
tool talking to it, and I wrongly suspected that a busy second core had
starved the first. The board was just busy. The fix was a freeze that does
not allocate: `max(range(1_000_000))` takes about 1.2 s and does nothing but
loop in C.

### Result 1: the cores run in parallel (Measured)

150,000 iterations of `x += i` on each core:

| | Time |
|---|---|
| Core 0 alone | 1014 ms |
| Core 1 alone | 1024 ms |
| Both at once | core 0: **1121 ms**, core 1: **1121 ms** |

If the cores took turns, each would take about 2000 ms. About **10% slower**
when both run is the cost of sharing the memory bus and the heap. The RP2
build sets `MICROPY_PY_THREAD_GIL` to 0, so there is no interpreter lock.
(Source)

### Result 2: a freeze on core 0 (Measured, reproduced by lab 03)

A steady tone plays while core 0 sits inside `max(range(1_000_000))`. Core 0
cannot run Python, scheduled callbacks, or anything else for about 1.2 s.

| Audio fed by | Core 0 frozen | Underruns | Reserve at its lowest | Longest wait between chunks |
|---|---|---|---|---|
| core 0 (interrupt callback) | 1163 ms | **1** | **-878 ms** | 1192 ms |
| core 1 (thread) | 1284 ms | **0** | **254 of 256 ms** | 64 ms |
| core 0, in lab 03 on Dan's board | 1164 ms | 1 | -867 ms | 1182 ms |
| core 1, in lab 03 on Dan's board | 1284 ms | 0 | 254 ms | 64 ms |

**Why core 0 ran dry.** The old design used I2S's non-blocking mode, where a
*callback* refills the ring. The callback is scheduled with
`mp_sched_schedule()`, and the scheduler only runs between MicroPython
operations. A long C call has none, so the callback waited 1.2 s, the ring
(256 ms) emptied, and the DMA interrupt, which kept running, played silence.
(Source for the scheduling; Measured for the result.)

**Why core 1 did not.** The producer is on a different core, so core 0
being frozen does not touch it. The DMA interrupt still runs on core 0,
because a hardware interrupt can fire in the middle of a long C call. That
is the reason the ring got to the DMA buffer even while core 0 was frozen.

### Result 3: real jobs, with sound on core 1 (Measured)

A 9-second tone, with these jobs run on core 0:

| Job | Took | Underruns | Reserve at its lowest | What it exercises |
|---|---|---|---|---|
| 40 KB flash write and delete | 139 ms | 0 | 250 ms | flash lockout. **See the caveat above.** |
| 20 × (allocate 8 KB, `gc.collect()`) | 133 ms | 0 | 248 ms | the shared heap and garbage collection |
| WiFi connect and NTP time sync | **9451 ms** | 0 | 252 ms | the wireless chip's interrupts and PIO link |

### Result 4: drawing (Measured)

| Audio fed by | Repaints | Underruns | Reserve at its lowest |
|---|---|---|---|
| core 0 (interrupt callback) | 21 full-screen fills | 0 | 252 ms |
| core 1 | 17 full-screen fills (lab 03) | 0 | 252 ms |

Drawing alone never needed core 1. The display driver makes many short SPI
writes, and the scheduler runs between them. For writes of 32 bytes or more
the SPI driver hands the bytes to **DMA** and waits for it to finish, with no
scheduler call during the wait; for shorter writes it calls the SDK's
blocking write. (Source: `machine_spi.c`.) So a repaint costs core 0 a lot
of *waiting*, but it is waiting that interrupts and the DMA both ignore.

### Result 5: the stress test, by ear (Measured)

`multicore-stress-test.py`, run on Dan's board on 2026-10-06. A steady
440 Hz tone on core 1 at 16 kHz with a 256 ms reserve; core 0 did one kind
of load per phase; the listener pressed UP for "heard a click or gap" or DOWN
for "clean".

| # | Phase | Took | Underruns | Reserve at its lowest | Longest wait | Heard a problem? |
|---|---|---|---|---|---|---|
| 0 | baseline (nothing) | 3000 ms | 0 | 254 ms | 64 ms | no |
| 1 | 23 full-screen repaints | 3017 ms | 0 | 254 ms | 64 ms | no |
| 2 | three WiFi scans | 3200 ms | 0 | 254 ms | 64 ms | no |
| 3 | WiFi connect and time sync | 5783 ms | 0 | 254 ms | 64 ms | no |
| 4 | web request (296 bytes) | 5658 ms | 0 | 254 ms | 64 ms | no |
| 5 | 20 garbage collections | 188 ms | 0 | 245 ms | 70 ms | no |
| 6 | 5 small flash writes | 2745 ms | 0 | 168 ms | 121 ms | **YES** |
| 7 | one 200 KB flash write | 695 ms | 0 | 56 ms | 148 ms | **YES** |
| 8 | everything in turn | 5830 ms | 0 | 27 ms | 92 ms | **YES** |

What it shows:

- **Phases 0 to 5 are the good news.** The display, WiFi (scanning,
  connecting, and fetching), and the garbage collector never disturbed the
  sound, by ear or by counter. The reserve sat at 254 of 256 ms, and the
  longest wait was the normal 64 ms chunk cadence. This is the main answer to
  "do display, WiFi, and sound work smoothly together": **yes, except for
  flash.**
- **Phases 6 to 8 are the one problem.** See [Flash: the
  Exception](#flash-the-exception).
- **Phase 8 is close to the edge.** With a flash lockout, scans, a repaint,
  and a collection all in turn, the reserve fell to 27 ms. That is still above
  zero, but it shows that a heavy mix of loads can bring even the ring
  buffer close to running dry. A bigger ring (`ibuf=16384` doubles it to
  512 ms) is cheap insurance for that, though it would not fix the flash
  glitch.
- **WiFi time varies.** The same connect and sync took 5.8 s here and 9.45 s
  the day before, so plan on up to ten seconds.

### Result 6: what the sound costs core 0 (Measured)

The same 150,000-step loop on core 0:

| Audio state | Time | Slower by |
|---|---|---|
| no audio at all | 1040 ms | |
| audio loop running, playing silence | 1107 ms | **6.4%** |
| 16 kHz tone | 1114 ms | **7.1%** |
| 44.1 kHz tone | 1142 ms | **9.8%** |

This is a single run, so treat differences of a percent or so as noise.
Reading it:

- **Most of the cost is simply having the audio loop on.** Silence alone
  costs 6.4%. That is core 1 busy-waiting in `write()` and polling the ring
  buffer, and the DMA interrupts running on core 0, both reading and writing
  shared memory.
- **Going from 16 kHz to 44.1 kHz adds about 2.7 percentage points.** That
  is 878 more DMA interrupts a second. If all of it were the interrupts, each
  would cost about 28 µs, which would put the interrupts at roughly 1.5% of
  core 0 at 16 kHz and 4% at 44.1 kHz. That split is my arithmetic, not a
  measurement.
- **It matches the 10% found earlier** for two Python loops running at once
  (1014 ms alone, 1121 ms together), so the bus is the common cause.
- **It is small but real.** Over a 130 ms repaint it is under 10 ms. It would
  matter if core 0 ever needed to be as fast as it can go. Idea C (pace the
  producer instead of busy-waiting) is the obvious way to claw back most of
  the 6.4%.

### What the numbers cannot see

- **They count supply, not sound.** The counters know when core 1 was late
  with the ring. They cannot see the DMA interrupt being late, a PIO stall,
  or a click from the amplifier. The stress test proved the point: the
  listener heard a problem in three phases where the ring never ran dry.
  Listening, or the PIO meter of idea E, is how to see the part the counters
  cannot.
- **Only one listener, one speaker, and one run** so far. A repeat with a
  second listener would show how many of the flash glitches are audible to
  other ears, and the "everything" phase's 27 ms low point shows the ring
  itself is not far from running dry under a heavy mix.

## Making the Display, WiFi, and Sound Work Together

### How each one affects the sound

| Neighbor | Effect on sound on core 1 | Evidence |
|---|---|---|
| **Display repaint** | None, by counter or ear | Measured, 17 to 23 fills |
| **WiFi connect and sync** | None, by counter or ear | Measured, 5.8 s and 9.45 s |
| **WiFi scans and a web request** | None, by counter or ear | Measured |
| **WiFi traffic while the screen animates** | Unknown | Not tested |
| **Garbage collection** | None seen | Measured, 20 collections |
| **Flash write** | **Click or gap, every time tested** | Measured by ear (3 phases) |
| **Buttons** (pin interrupts) | Expected none | Not tested; their handlers are short |
| **DMA interrupt latency from other interrupts** | Possible: the WiFi chip's interrupt could hold the DMA one off | Hypothesis (E5) |

### Rules for a program that does all three

1. **One extra thread exists: the sound loop.** The RP2 port has only core 1
   to give. Do not start another thread.
2. **Run everything but the sound on core 0:** buttons, display, WiFi, and
   files. The WiFi driver and `network` module were written for the main
   core; running them on core 1 has not been tried and I would not.
3. **Never write a file while a sound plays.** Wait for `sound.busy()` to be
   false.
4. **Never run a long download while a sound plays.** The writes are the
   problem, not the radio.
5. **Show a "connecting" screen before any WiFi call, and expect core 0 to be
   blocked for up to ten seconds.** Draw the screen first. Buttons still
   register short taps because `watchparts.Button` uses a pin interrupt, but
   nothing responds until the call returns.
6. **Keep the screen updates small.** A full-screen fill (130 ms) is fine, but
   drawing only what changed is faster and is the habit the whole kit uses.
7. **Keep the core-1 loop light.** Its stack is the default 4096 bytes, and
   anything that allocates on core 1 can trigger a garbage collection. Do not
   add work to `_fill()` without measuring.
8. **Use `sound.latency_ms()`** when the screen should match what is heard.
9. **Watch `sound.stats()` during development.** If `min_headroom_ms` ever
   falls under about 100 ms, something is competing with core 1: find it.
10. **Reminders must sound even when WiFi is busy.** Sound on core 1 does
    that, except during a flash write (rule 3).

### Display and WiFi without sound (untested)

These two compete for core 0. A WiFi call blocks the main program, so an
animation freezes until it returns. The wireless chip's interrupts also run
on core 0 and could delay the display's short writes. We do not know how
much. Experiment E5 draws an animation during a fetch and counts the frames
that stall.

## Ideas That Would Offload More

None of these has been tried. They are listed in order of how much they
would help, and each has an experiment.

| Idea | What it would change | Why it might work | Risk |
|---|---|---|---|
| **A. A big DMA ring with no refill interrupt** | The refill step moves from a 2 ms interrupt to a 256 ms deadline | Build our own I2S from `rp2.StateMachine` and `rp2.DMA`: DMA reads a large RAM buffer in a loop (the RP2350 DMA can wrap a read address or retrigger itself), and the CPU just writes ahead of it. DMA keeps streaming from RAM while flash is erased, since RAM does not depend on flash. | We would own the I2S code: the PIO program, the pins, and the buffer alignment. Substantial. |
| **B. Create the I2S object on core 1** | The DMA interrupt moves to core 1, away from core 0's WiFi and display work | An interrupt is enabled on the core that registers it, which is the core that created the I2S object. Core 1 has nothing else to do. | Flash still pauses core 1 and blocks its interrupts. The code that creates I2S would need to run on core 1 first. |
| **C. Pace the producer instead of busy-waiting** | Core 1 sleeps instead of spinning, which frees the memory bus | `_feed()` already knows the reserve (`headroom`), so it can sleep until the ring has room, and sleep with a normal `sleep_ms()` | The pacing is only as accurate as the clock estimate. |
| **D. Offload the display's SPI wait** | Core 0 would do other work during a 130 ms repaint | The SPI driver already uses DMA for the bytes. A non-blocking DMA call plus a second frame buffer would let core 0 prepare the next frame while the screen is being filled. | Needs a `rp2.DMA`-based driver, and the display is currently all blocking. |
| **E. PIO as a built-in logic analyzer** | A way to *measure* underruns at the pins, not at the ring | A second state machine watches the WS pin and records the time between WS edges. A gap longer than one frame means I2S stalled. This is a software tool, and it uses a PIO the way PIO is meant to be used. | Needs a short PIO program in MicroPython assembly. |

!!! tip "Why E comes first"
    Every idea above, and the flash question itself, can only be judged by
    watching what the I2S pins actually do. Right now our only instrument is
    an ear. A PIO that times WS edges would give a number for every
    experiment, with no listening and no extra wires.

## Experiments to Run

| ID | Question | How | Result so far |
|---|---|---|---|
| **E1** | Does a flash write make a dropout? | `multicore-stress-test.py`, phases 6 to 8; the listener votes | **Done: yes.** Heard in all three flash phases. |
| **E2** | Does a WiFi connect make a dropout you can hear? | Same script, phases 2 to 4 | **Done: no.** Clean by ear and counter. |
| **E3** | How much slower does core 0 run when core 1 is playing sound? | Same script, speed test | **Done: +6.4% (silence), +7.1% (16 kHz), +9.8% (44.1 kHz).** |
| **E4** | How much CPU does the DMA interrupt and the synthesis use? | Time `_fill()`; vary the sample rate | **Partly done:** the 16 to 44.1 kHz step costs about 2.7 points, which would be about 28 µs per interrupt if all of it is the interrupt. Synthesis time itself is not measured. |
| **E5** | Does WiFi traffic make the display stall, or the sound click? | Draw an animation while fetching a web page | **Not done.** Phase 8 interleaves them but does not animate during a fetch. |
| **E6** | Does the DMA interrupt ever run late? | Idea E: a PIO state machine timing WS edges | **Not started.** The most useful next instrument. |
| **E7** | Does creating I2S on core 1 move the interrupt? | Idea B, repeating the WiFi phase | **Not started.** |
| **E8** | Does a paced producer lower core 0's slowdown? | Idea C, repeating E3 | **Not started.** |
| **E9** | Can our own DMA-ring I2S survive a flash write? | Idea A, repeating E1 | **Not started.** The real fix for flash. |
| **E10** | Does a flash write during *silence* pop? | New phase: a large write with no tone playing | **Not done. Decides whether "don't write while a sound plays" is enough.** Added to the script as phase 9. |

### The stress-test script

`src/kits/study-buddy/multicore-stress-test.py` plays a steady 440 Hz tone
on core 1 for several seconds per phase, runs one kind of load on core 0
during each phase, and then asks the listener to press **UP** if they heard
a click or gap, or **DOWN** if the tone stayed clean. It prints the
supply-level counters and the vote for each phase, plus the "speed" phase
for E3. Run it in Thonny and paste the output back. It has been run once
(see [Result 5](#result-5-the-stress-test-by-ear-measured)).

The phases are: baseline, screen repaints, WiFi scans, WiFi connect and time
sync, a web request, garbage collection, small flash writes, a large flash
write, everything in turn, and (new) a large flash write during silence. If the board is on its own, Thonny can run
it. If a computer is attached to the board, **quit Thonny first** when
asking me to run it, because only one program can hold the serial port.

## Reference

### What `sound.py` does for you

| You call | What runs |
|---|---|
| `sound.init()` | Starts the I2S hardware (PIO, DMA, ring buffer) on core 0, then the audio loop on core 1 |
| `sound.tone(...)` | Adds a note to the queue, under a lock |
| the core-1 loop | `_fill()` makes 1024 samples with viper machine code, `write()` puts them in the ring |
| `sound.stats()` | The supply counters: underruns, smallest reserve, longest gap |
| `sound.deinit()` | Tells the loop to leave, waits, then frees the I2S hardware |

### Glossary

| Word | Meaning |
|---|---|
| **Core** | A processor that runs instructions. The Pico 2 W has two. |
| **GIL** | Global Interpreter Lock: a rule that lets only one thread run Python at a time. This build turns it off. |
| **PIO** | Programmable I/O: small state machines that make pin signals with exact timing, on their own. |
| **DMA** | Direct Memory Access: hardware that copies data between memory and devices without the CPU. |
| **Interrupt (IRQ)** | A signal that makes a core drop what it is doing and run a short handler. |
| **Ring buffer** | A fixed block of memory used as a queue, with a write position and a read position that wrap around. |
| **Underrun** | The reader needs data and the buffer is empty. For sound, this is silence or a click. |
| **Reserve** | How much sound is stored in the ring ahead of the speaker, in milliseconds. |
| **Lockout** | The flash driver pausing the other core while it erases or writes flash. |
| **XIP** | Execute In Place: code runs straight from flash through a cache. It is unavailable while flash is erased or written. |
| **Viper** | A MicroPython code emitter that compiles a function to fast machine code. |
| **Side-set** | A PIO feature that sets pins during an instruction, at no extra cost. |

### Sources

- MicroPython v1.29.0 (the firmware on the board), `ports/rp2/machine_i2s.c`:
  PIO programs, side-set and the `ws == sck + 1` check, the clock formula, the
  two chained DMA channels and 256-byte buffer, the DMA interrupt handler
  and `feed_dma()`, silence on underrun, and mono duplication.
- `extmod/machine_i2s.c`: blocking `write()` as a busy-wait, the
  non-blocking callback scheduled by `mp_sched_schedule()`, and the
  single-producer single-consumer ring buffer.
- `ports/rp2/mpthreadport.c`: core 1 start-up, the 4096-byte default stack,
  the recursive mutex used while core 1 is active, the lockout victim
  registration, and `mp_thread_gc_others()`.
- `ports/rp2/mpconfigport.h`: `MICROPY_PY_THREAD_GIL (0)`.
- `ports/rp2/rp2_flash.c`: `begin_critical_flash_section()` with lockout and
  interrupts disabled around every erase and program.
- `ports/rp2/machine_spi.c`: DMA for writes of 32 bytes or more, blocking
  writes below that, no scheduler call during the wait.
- Adafruit's MAX98357A breakout page, for the GAIN pin and SD pin behavior.
- Kit measurements: `src/kits/study-buddy/03-sound-test.py` and the test
  scripts described under [What We Measured](#what-we-measured).

**Next:** [Roadmap and Risks](05-roadmap.md)
