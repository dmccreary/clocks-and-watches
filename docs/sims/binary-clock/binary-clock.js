// Use the microsim-2d-geometry.js template
// CANVAS_HEIGHT: 280
let canvasWidth = 350;
let drawHeight = 240;
let controlHeight = 40;
let canvasHeight = drawHeight + controlHeight;
let defaultTextSize = 24;
let timeTextSize = 36;
let margin = 50;
let showTextTime = false; // Toggle state for displaying textual time
let button; // Button for toggling text time

function setup() {
  const canvas = createCanvas(canvasWidth, canvasHeight);
  var mainElement = document.querySelector('main');
  canvas.parent(mainElement);
  

  // Create button for toggling textual time display
  button = createButton("Show Text Time");
  button.position(10, drawHeight + 10);
  button.mousePressed(toggleTextTime);
}

function draw() {
  // Drawing region background
  fill('aliceblue');
  stroke('silver');
  rect(0, 0, canvasWidth, drawHeight);

  // Controls region background
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  // Get current time
  let now = new Date();
  let hours = now.getHours();
  let minutes = now.getMinutes();
  let seconds = now.getSeconds();

  // Display binary circles for hours (top row, horizontally)
  for (let i = 0; i < 5; i++) {
    // Determine the bit (on/off) and the power-of-two value
    let bit = (hours >> (4 - i)) & 1; // 1 if this bit is set
    let value = 1 << (4 - i);         // e.g. 16, 8, 4, 2, 1

    fill(bit ? 'green' : 'lightgray');
    let x = margin + i * 50;
    let y = margin + 10;
    circle(x, y, 40);

    // Draw the numeric label inside the circle
    fill('gray');
    textSize(defaultTextSize);
    textAlign(CENTER, CENTER);
    text(value, x, y);
  }

  // Display binary circles for minutes (second row, horizontally)
  for (let i = 0; i < 6; i++) {
    let bit = (minutes >> (5 - i)) & 1; // 1 if this bit is set
    let value = 1 << (5 - i);          // e.g. 32, 16, 8, 4, 2, 1

    fill(bit ? 'blue' : 'lightgray');
    let x = margin + i * 50;
    let y = margin + 80;
    circle(x, y, 40);

    // Draw the numeric label inside the circle
    fill('gray');
    textAlign(CENTER, CENTER);
    text(value, x, y);
  }

  // Display flashing circle for seconds (center)
  fill(seconds % 2 === 0 ? 'red' : 'lightgray');
  circle(margin * 6, margin+10, 40);

  // Display textual time if toggled
  if (showTextTime) {
    fill('black');
    textAlign(CENTER, CENTER);
    textSize(timeTextSize);
    text(
      `${hours.toString().padStart(2, '0')}:${minutes
        .toString()
        .padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`,
      canvasWidth / 2,
      drawHeight - 40
    );
  }
}

// Toggle the textual time display
function toggleTextTime() {
  showTextTime = !showTextTime;
  button.html(showTextTime ? "Hide Text Time" : "Show Text Time");
}
