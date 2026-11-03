# Gravity Flip: Escape Dimension

A customizable 2D physics-arcade game for Multimedia Systems Lab Test 2. It is built with HTML, CSS, and JavaScript Canvas, so it runs as a static site and can be deployed on Vercel.

## Rules

- Move the laboratory escape suit with `Left/Right Arrow` or `A/D`.
- Collect purple gravity crystals for points.
- Avoid pink electric barriers. Each collision removes one stability heart.
- Press `Space` to reverse gravity. The player and falling objects change direction.
- Gravity automatically reverses every 20 seconds. This is the assigned customization and makes the game increasingly difficult.
- Consecutive crystals create a combo multiplier. A collision resets the combo.
- The experiment ends when all three stability hearts are lost.

## Controls

| Key | Action |
| --- | --- |
| Left / Right or A / D | Move |
| Space | Manually reverse gravity |
| P | Pause/resume |

## Run locally

Open `index.html` in a browser, or serve the folder with any static server:

```bash
npx serve .
```

## Deploy to Vercel

1. Push this folder to a GitHub repository.
2. Import the repository at [vercel.com](https://vercel.com).
3. Select the project as a static site. No build command is required; use `.` as the output directory if prompted.

## Algorithm and collision detection

The game uses a `requestAnimationFrame` loop. Each frame updates keyboard movement, gravity acceleration, object positions, the automatic 20-second gravity timer, particles, score, and lives. Rectangular collision detection checks whether the player rectangle overlaps each crystal or barrier rectangle. A crystal increases the score and combo; a barrier removes stability and grants a short invincibility window. Once stability reaches zero, the game changes to the game-over state and displays the restart screen.
