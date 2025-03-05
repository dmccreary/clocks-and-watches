# Fibonacci Clock

# Fibonacci Clock

What is the minimum number of colored LED necessary to tell the time?
The Fibonacci Clock is a unique timepiece that uses just five colored squares of different sizes to tell time. Here's how it works:

## Clock Layout

-   The clock consists of five squares whose sizes correspond to the first five Fibonacci numbers (1, 1, 2, 3, 5)
-   These squares are arranged in a pattern that forms a rectangle, with the largest square (5) typically on one side.  In our example, it will be on the right side.

## Reading the Time

<iframe src="https://dmccreary.github.io/microsims/sims/fibonacci-clock/main.html" width="600" height="565"  scrolling="no"></iframe>


-   **Colors indicate function**:
    -   **Red squares** represent hours
    -   **Green squares** represent minutes
    -   **Blue squares** represent both hours and minutes
    -   **Black squares** are inactive (not used for the current time)
-   **To read the hours**: Add the values of all red and blue squares
    -  Example: If the 5-square is red and the 3-square is blue, the hour is 8
-   **To read the minutes**: Add the values of all green and blue squares, then multiply by 5
    - Example: If the 2-square is green and the 3-square is blue, the minutes are (2+3) × 5 = 25

## Some Limitations

- Hours are displayed in 12-hour format (1-12)
- Minutes are displayed in 5-minute increments (0, 5, 10, 15, etc.).  We actually round the actual minute to the closest value so the number you calculate is within 2.5 minutes of the actual time.
- The clock can only display certain minute values due to the limited combinations possible with the five Fibonacci squares

This clever design creates a visually interesting timepiece that requires a bit of mental arithmetic to read, making it both decorative and intellectually engaging.

It will take you a bit of time to get used to doing the math.  After a while is will become easier.

[Assembly](assembly.md)

[Programming Code](./code.md)

[Generative AI Prompt](./prompt.md)

