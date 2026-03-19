# Prompt

!!! prompt
    I need to add sound to my clock.  To do this I purchased the following:

    Interface I2S PCM5102A DAC Decoder GY-PCM5102 I2S Player Module For Raspberry

    It has the following edge connections:

    GND - Connected to GND 
    V  IN - Connected to 3.3 V
    LCK - Connected to GPIO 15
    D IN - Connected to GPIO 14
    BCK - Connected to GPIO 13
    SCK - Connected to GPIO 12
    LINE OUT - Connected to an 8-ohm speaker

    Please help me write a MicroPython program for the Raspberry Pi Pico that can help me test this device.

## Response

I'll help you write a MicroPython program to test the I2S DAC module with your Pico. We'll create a simple test that generates a sine wave tone to verify the setup is working correctly.

[I2S DAC Test Program](test-connections.py)


This program provides a basic test of your I2S DAC setup. Here's how it works:

1.  It configures the I2S interface with the pins you've connected:
    -   GPIO 12 (SCK) for the serial clock
    -   GPIO 15 (WS/LCK) for the word select
    -   GPIO 14 (SD/DIN) for the serial data
2.  It creates functions to:
    -   Generate sine waves at specific frequencies
    -   Play individual tones
    -   Run a test sequence of notes (C4, E4, G4, C5)
3.  The test sequence plays each note for 500ms.

To use this program:

1.  Save it to your Pico as `main.py`
2.  When you run it, you should hear a sequence of ascending notes through your speaker
3.  If you don't hear anything:
    -   Check all your connections
    -   Verify your speaker is properly connected to LINE OUT
    -   Make sure your power connections (GND and VIN) are secure

You can modify the `test_sequence()` function to play different frequencies or durations. For reference, here are some common note frequencies:

```
python
Copy

`NOTE_FREQUENCIES ={'C4':262,'D4':294,'E4':330,'F4':349,'G4':392,'A4':440,'B4':494,'C5':523}`

```

Would you like me to modify the program to include different test patterns or features?

 CopyRetry