# Sample  Generative AI Prompts

## Layout Diagram

!!! prompt
    I would like to build a Fibonacci clock with five squares.  I have a piece of plexiglass that is 6 inches wide.  What are the exact dimensions of each of the cells in a landscape configuration.

[Sample Anthropic Claude Dialog](https://claude.ai/share/31f6c2d4-3602-4e3d-9677-89aeb3a90c71)

Note that the dialog also includes the generation of both
the layout diagrams and the MicroSim.

![Square Layout](./square-layout-diagram.png)

## Code Explanation

!!! prompt
    Please create a p5.js sketch using the responsive-desigh.js template that illustrates how the fib_time() function works that converts hours and minutes into the state of the five cells in the clock.

    Detailed Instructions:

    The p5.js sketch should have two sliders at the bottom of the control area.  
    The first slider adjusts the hour from 0 to 11.
    The second slider adjusts the minutes from 0 to 59.
    Place a title "Fibonacci Clock Algorithm" in the top center of the drawing region.
    Place the clock diagram under the title.
    Please the state variables under the clock.
    Show the components of the hours and minutes in an equation where the digit is on the left and the sum of the cells is on the right.  Make the text color match the cell color.

Here is the algorithm in Python, but you will need to use the JavaScript version.

def fib_time(hours, minutes):
    vals = [1, 1, 2, 3, 5]
    state = [0, 0, 0, 0, 0]

    # Calculate Fibonacci representation for hours
    remaining_hours = hours
    idx = len(vals) - 1
    # step through values in reverse order
    for v in vals[::-1]:
        if remaining_hours == 0 or idx < 0: break
        if remaining_hours >= v:
            state[idx] += 1
            remaining_hours -= v
        idx -= 1

    # Calculate Fibonacci representation for minutes (in increments of 5)
    remaining_minutes = math.floor(minutes / 5)
    idx = len(vals) - 1
    for v in vals[::-1]:
        if remaining_minutes == 0 or idx < 0: break
        if remaining_minutes >= v:
            state[idx] += 2
            remaining_minutes -= v
        idx -= 1

    return state