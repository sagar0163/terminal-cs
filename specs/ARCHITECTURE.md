# Architecture Document: Terminal Counter-Strike

## 1. System Overview

Terminal Counter-Strike is a Python-based terminal FPS game using raycasting for pseudo-3D rendering. The architecture follows a game loop pattern with distinct modules for rendering, game logic, and user input.

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Main Game Loop                          │
│                     (game.py)                                │
└─────────────────────┬───────────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    ▼                 ▼                 ▼
┌─────────┐     ┌───────────┐     ┌──────────┐
│ Input   │     │  Game     │     │ Renderer │
│ Handler │     │  Logic    │     │ (Curses) │
└─────────┘     └───────────┘     └──────────┘
    │                 │                 │
    │                 ▼                 │
    │          ┌───────────┐            │
    │          │ Entities  │            │
    │          │ - Player  │            │
    │          │ - Enemies │            │
    │          │ - Powerups│            │
    │          └───────────┘            │
    │                 │                 │
    │                 ▼                 │
    │          ┌───────────┐            │
    │          │  Physics  │            │
    │          │ - Raycast │            │
    │          │ - Collision│           │
    │          └───────────┘            │
    │                                   │
    └───────────┬───────────────────────┘
                │
                ▼
         ┌─────────────┐
         │   Level    │
         │   System   │
         │ - Maps     │
         │ - Editor   │
         └─────────────┘
```

## 3. Core Components

### 3.1 Rendering Engine (Raycasting)
- **DDA Algorithm:** Digital Differential Analyzer for wall distance calculation
- **Field of View:** 60-degree view cone
- **Ray Count:** One ray per screen column
- **Wall Height:** Proportional to inverse distance
- **Texture Simulation:** Shading based on distance and wall orientation

```
    Raycasting Visualization
    
    Player → ╲═══════════════════→ Wall
              ╲══════════════════
               ╲═════════════════
                ╲════════════════
```

### 3.2 Game Entities

#### Player
- Position (x, y)
- Direction (angle)
- Health, Ammo, Armor
- Current weapon
- Powerup states

#### Enemies
| Type | HP | Damage | Behavior |
|------|-----|--------|----------|
| Grunt | 100 | 10 | Basic AI, move and shoot |
| Shotgunner | 150 | 25 | Close-range, spread damage |
| Sniper | 80 | 50 | Long-range, one-shot potential |
| Boss | 500 | 30 | Every 3 waves, high HP |

#### Powerups
- Health (+50 HP)
- Ammo (+30 rounds)
- Armor (+50 points)
- Damage (2x multiplier)
- Speed (2x movement)

### 3.3 Weapons System
| Weapon | Damage | Fire Rate | Special |
|--------|--------|-----------|---------|
| Pistol | 25 | Medium | Starter weapon |
| Rifle | 35 | Fast | Auto-fire |
| Knife | 50 | Slow | Melee attack |
| Shotgun | 80 | Very Slow | Spread damage |
| Machine Gun | 20 | Rapid | High DPS |
| Sniper | 150 | Slow | One-shot kill |
| Grenade | 100 | Slow | Area of Effect |
| Rocket Launcher | 200 | Slow | Boss killer |
| Flame Thrower | 15 | Rapid | Spray damage |

### 3.4 Level System
- **5 Built-in Maps:** Pre-designed levels
- **Procedural Generation:** Random map creation
- **Level Editor:** Custom map creation tool

#### Map Format
```
# = Wall
. = Floor
P = Player start
E = Enemy spawn
```

### 3.5 Multiplayer System
- **Local Co-op:** 2-4 players on same screen
- **Split Controls:** Keys 1-4 to switch players
- **Shared Resources:** Option for shared or individual ammo/health

## 4. Game Loop

```
┌─────────────────────────────────────────┐
│              Game Loop                  │
├─────────────────────────────────────────┤
│ 1. Process Input                        │
│    - Read keypresses                    │
│    - Update player state                │
│                                         │
│ 2. Update Game State                   │
│    - Move enemies                       │
│    - Process AI                         │
│    - Handle collisions                  │
│    - Update projectiles                 │
│                                         │
│ 3. Render Frame                         │
│    - Cast rays                          │
│    - Draw walls                         │
│    - Draw sprites (enemies/items)      │
│    - Draw UI (health, ammo, score)     │
│                                         │
│ 4. Check Game Conditions               │
│    - Wave complete?                     │
│    - Player dead?                       │
│    - Game over?                         │
└─────────────────────────────────────────┘
```

## 5. Input Handling

| Input | Action |
|-------|--------|
| W/↑ | Move forward |
| S/↓ | Move backward |
| A/← | Turn left |
| D/→ | Turn right |
| Space | Shoot |
| 1-9 | Select weapon |
| R | Reload |
| P | Pause |
| Q | Quit |

## 6. File Structure

```
terminal-cs/
├── src/
│   └── game.py       # Main game (all-in-one)
├── specs/            # Documentation
├── README.md
├── LICENSE
└── test_game.py      # Test scripts
```

## 7. Dependencies

| Package | Purpose |
|---------|---------|
| curses / ncurses | Terminal rendering |
| windows-curses | Windows compatibility |
| Python 3.6+ | Runtime |

---

*Document Version: 1.0*  
*Created: 2026-03-17*
