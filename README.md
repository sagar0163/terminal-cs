# Terminal Counter-Strike 🎮

A pseudo-3D First-Person Shooter game for Linux terminal with raycasting engine!

## Features

- 🎯 **Pseudo-3D Rendering** - Wolfenstein-style raycasting
- 🎮 **3 Game Modes** - Simple, Medium, Advanced
- 👾 **Multiple Enemy Types** - Grunt, Shotgunner, Sniper, Boss
- ⚡ **Powerups** - Health, Ammo, Armor, Damage, Speed
- 🗺️ **Two Map Types** - Pre-built Arena or Random Generation
- 🔫 **Weapons System** - Pistol, Rifle, Knife, Shotgun
- 📊 **Score & Wave System** - Endless waves with increasing difficulty

## Screenshots

```
 TERMStrike - Console FPS

SELECT MODE:
   [1] SIMPLE - Just shooting, static enemies
  >> [2] MEDIUM - Enemies shoot back
   [3] ADVANCED - Multiple enemy types + powerups

SELECT MAP:
  >> [a] ARENA - Pre-built arena map
   [r] RANDOM - Randomly generated map
```

## Installation

```bash
# Clone the repository
git clone https://github.com/sagar0163/terminal-cs.git
cd terminal-cs/src
```

## How to Play

```bash
# Run the game
python3 game.py
```

### Controls

| Key | Action |
|-----|--------|
| `W` / `↑` | Move forward |
| `S` / `↓` | Move backward |
| `A` / `←` | Turn left |
| `D` / `→` | Turn right |
| `Space` | Shoot |
| `1` | Pistol |
| `2` | Rifle |
| `3` | Knife |
| `R` | Reload |
| `P` | Pause |
| `Q` | Quit |

## Game Modes

### Simple
- Static enemies (they don't shoot back)
- Basic grunt enemies
- No powerups
- Good for practice

### Medium
- Enemies shoot back!
- Multiple enemy types:
  - **Grunt** - Basic enemy, 100 HP
  - **Shotgunner** - Close-range damage, 150 HP
  - **Sniper** - High damage, low health

### Advanced
- Everything in Medium
- **Boss enemy** every 3 waves (500 HP)
- **Powerups** spawn randomly:
  - ❤️ Health (+50 HP)
  - 📦 Ammo (+30)
  - 🛡️ Armor (+50)
  - ⚡ Damage (2x multiplier)
  - 💨 Speed (2x multiplier)

## Maps

### Arena
Pre-built combat arena with corridors and open spaces.

### Random
Procedurally generated maps with varying complexity.

## Enemies

| Enemy | HP | Damage | Points |
|-------|-----|--------|--------|
| Grunt | 100 | 10 | 100 |
| Shotgunner | 150 | 25 | 200 |
| Sniper | 80 | 50 | 300 |
| Boss | 500 | 30 | 1000 |

## Weapons

| Weapon | Damage | Ammo | Fire Rate |
|--------|--------|------|-----------|
| Pistol | 25 | 12 | Medium |
| Rifle | 35 | 30 | Fast |
| Knife | 50 | ∞ | Slow |
| Shotgun | 80 | 8 | Very Slow |

## How It Works

The game uses **raycasting** - the same technique used in Wolfenstein 3D:

1. Cast rays from player position across field of view
2. Calculate distance to walls using DDA algorithm
3. Render walls at heights proportional to inverse distance
4. Add sprites for enemies and powerups

```
    Player
      │
      │ ray ray ray ray ray
      │╲╲╲╲╲╲╲╲╲╲╲╲╲╲
      │  ╲╲╲╲╲╲╲╲╲╲╲╲
      ▼   Walls rendered
```

## Files

```
terminal-cs/
├── src/
│   └── game.py       # Main game (all in one file!)
├── README.md
└── LICENSE
```

## Requirements

- Python 3.6+
- Linux terminal with curses support
- Or Windows/macOS with `windows-curses`

```bash
# For Windows
pip install windows-curses
```

## License

MIT License - Feel free to modify and share!

## Author

Created by Sagar Jadhav

Enjoy the game! 🔫🎮
