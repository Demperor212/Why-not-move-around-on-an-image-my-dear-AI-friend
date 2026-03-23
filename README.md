# 2D RPG Character Controller

A Python/pygame-based application that provides a visual top-down 2D RPG-style interface with terminal-based character control.

## Features

- **Visual Display**: Shows a red dot representing a character on a switchable background
- **Multiple Backgrounds**: Comes with 5 built-in colored backgrounds (grass, dirt, water, stone, sand)
- **Terminal Control**: Control the character using a simple `move(direction, speed, length)` function
- **Keyboard Shortcuts**: 
  - Press `B` to switch backgrounds in the visual window
  - Press `ESC` to quit
- **Real-time Feedback**: See character position and angle displayed on screen

## Requirements

- Python 3.x
- pygame (`pip install pygame`)

## Usage

Run the application:

```bash
python rpg_controller.py
```

This will open two interfaces:
1. A pygame window showing the character (red dot) on a background
2. A terminal prompt for entering commands

### Terminal Commands

#### Move Character
```
move(direction, speed, length)
```
- `direction`: Degrees (0=right, 90=up, 180=left, 270=down)
- `speed`: Pixels per second
- `length`: Duration of movement in seconds

**Examples:**
```
move(0, 100, 2)      # Move right at 100 px/s for 2 seconds
move(90, 50, 1)      # Move up at 50 px/s for 1 second
move(45, 75, 0.5)    # Move diagonally at 75 px/s for 0.5 seconds
```

#### Switch Background
```
switch_bg()          # Switch to next background
switch_bg(2)         # Switch to specific background index
```

#### Other Commands
```
help     # Show available commands
quit     # Exit the application
```

## How It Works

The application runs two threads:
1. **Visual Thread**: Handles the pygame display, rendering the character and background
2. **Terminal Thread**: Accepts user commands and sends them to the visual thread via a queue

Commands entered in the terminal are processed and executed in the visual window, providing immediate feedback.

## Project Structure

- `rpg_controller.py` - Main application file containing:
  - `Character` class - Represents the player character
  - `BackgroundManager` class - Manages background images
  - `GameApp` class - Main game loop and rendering
  - `terminal_interface()` - Command-line interface

## Future Enhancements

- Load custom background images from files
- Add collision detection
- Support for animated sprites
- Multiple characters/NPCs
- Save/load character positions

---
*Under Construction - Prototype Version*
