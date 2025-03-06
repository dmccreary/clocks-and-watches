# Code

The Fibonacci clock shares a common code base with most of
the other clocks in our site.  It needs to read the
actual time from the real-time clock (RTC) or WiFi and in needs
to have the RTC set if you don't use WiFi to synchronize your time.

The key difference is how the hour and minute digits are converted
into turning on the right LEDs.

## The ```fib_time``` Function

At the core of this process is the ```fib_time``` function.  This function has two inputs (hours and minutes) and returns a sequence of five binary numbers, one for each cell in our clock. Here is that code:

```python
# Fibonacci time function
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
```

You will see that `fib_time()` has two loops, one for the hours and one for the minutes.  For each loop it starts with the initial value and then subtracts
the value for each cell.  It breaks out of the loop if there are no more
values left or the index (idx) is less than zero.

Here is a step by step explanation of the code that calculate the hours:

```python
# Calculate Fibonacci representation for hours
remaining_hours = hours
idx = len(vals) - 1
for v in vals[::-1]:
    if remaining_hours == 0 or idx < 0: break
    if remaining_hours >= v:
        state[idx] += 1
        remaining_hours -= v
    idx -= 1
```

This code is taking a number of hours and representing it using Fibonacci numbers. 

1.  `remaining_hours = hours` - This creates a variable that starts with the total number of hours we're trying to represent.  It gets hours as an input parameter. We'll subtract from this as we go.

2.  `idx = len(vals) - 1` - This sets an index to point to the last element of the `vals` list, which contains the first five Fibonacci values ( 1, 1, 2, 3, 5).

3.  `for v in vals[::-1]:` - This loop goes through the `vals` list in reverse order. The `[::-1]` is a Python trick that means "start at the end and move backward." We start with the largest Fibonacci numbers first.

4.  `if remaining_hours == 0 or idx < 0: break` - This says "if we've used up all the hours or run out of Fibonacci numbers, stop the loop."

5.  `if remaining_hours >= v:` - This checks if the current Fibonacci number can fit into our remaining hours.

6.  `state[idx] += 1` - If the Fibonacci number fits, we increment a value in the `state` list at position `idx`. This is tracking which Fibonacci numbers we're using.

7.  `remaining_hours -= v` - We subtract the Fibonacci value from our remaining hours.

8.  `idx -= 1` - We move to the next position in our tracking list, regardless of whether we used the current Fibonacci number.

In simple terms, this algorithm is like making change with coins, but using Fibonacci numbers instead of coins. It starts with the largest Fibonacci value and works down to the smallest, trying to represent the hours using as few Fibonacci numbers as possible.

Looking at the other files you've provided, this appears to be part of a Fibonacci clock, where time is represented using Fibonacci squares on a display of LED lights.

## Full Main Program

```python
```
