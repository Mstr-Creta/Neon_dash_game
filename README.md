# Neon Dash

A fast-paced reflex racing game built with Pygame where you control a glowing neon vehicle racing down an endless track filled with moving obstacles.

## Game Features

- Neon-themed visuals with glowing effects
- Smooth player controls with left/right movement
- Randomly generated obstacles to dodge
- Collectible neon orbs that increase your score
- Boost mechanic with a meter that fills as you collect orbs
- Particle effects for collisions and pickups
- Animated neon grid background
- Progressive difficulty that increases over time
- Game over screen with score display and restart option

## Controls

- **Left/Right Arrow Keys** or **A/D Keys**: Move the vehicle left/right
- **Space**: Activate boost (when meter is charged)
- **R**: Restart after game over
- **Q**: Quit after game over
- **Enter**: Start the game from title screen

## Requirements

- Python 3.x
- Pygame library

## Installation

1. Make sure you have Python installed
2. Install Pygame: `pip install pygame`
3. Run the game: `python neon_dash.py`

## Sound Files

For the full experience, add the following sound files to the same directory:
- `pickup.wav` - Sound when collecting orbs
- `crash.wav` - Sound when crashing
- `dodge.wav` - Sound when narrowly dodging obstacles
- `synthwave.mp3` - Background music

The game will still run without these files, but will display a message about missing sounds.

## Gameplay Tips

- Collect orbs to increase your score and charge your boost meter
- Use boost (Space) strategically to navigate through tight spots
- The game gets progressively faster - stay alert!
- Some orbs are worth more points than others (indicated by lines radiating from them)
- Try to beat your high score with each run!

## Customization

Feel free to modify the game by:
- Adjusting the difficulty scaling in the `update_difficulty()` function
- Adding new obstacle types
- Changing the color scheme
- Adding power-ups or special effects

Enjoy the neon rush!
