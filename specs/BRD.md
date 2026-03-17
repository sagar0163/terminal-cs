# Business Requirements Document (BRD): Terminal Counter-Strike

## 1. Project Overview

**Project Name:** Terminal Counter-Strike  
**Type:** Terminal-based First-Person Shooter Game  
**Core Functionality:** A pseudo-3D First-Person Shooter game for Linux terminal using raycasting engine (Wolfenstein-style), featuring multiple game modes, enemy types, weapons, levels, and multiplayer support.

**Target Users:** Gamers who enjoy retro-style FPS games and want to play in their terminal. Linux users primarily, with cross-platform support via windows-curses.

---

## 2. Features

### Core Features
- **Pseudo-3D Rendering:** Wolfenstein-style raycasting engine
- **4 Game Modes:** Simple, Medium, Advanced, Multiplayer
- **Multiple Enemy Types:** Grunt, Shotgunner, Sniper, Boss
- **Powerups:** Health, Ammo, Armor, Damage, Speed
- **5 Built-in Levels:** The Warehouse, The Corridor, The Arena, The Fortress, The Lab
- **9 Weapons:** Pistol, Rifle, Knife, Shotgun, Machine Gun, Sniper, Grenade, Rocket Launcher, Flame Thrower
- **Score & Wave System:** Endless waves with increasing difficulty
- **Sound Effects:** Visual feedback for all actions
- **Multiplayer:** Local co-op (2-4 players on same screen)
- **Level Editor:** Create custom maps

### Technical Features
- Python-based with curses library
- DDA raycasting algorithm
- Sprite rendering for enemies/powerups
- Procedural map generation
- Split-screen multiplayer

---

## 3. Tech Stack

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.6+ |
| **Rendering** | Curses (ncurses) |
| **Audio** | Terminal bell/visual feedback |
| **Platform** | Linux (primary), Windows/macOS (via windows-curses) |

---

## 4. User Stories

| ID | User Story | Acceptance Criteria |
|----|------------|---------------------|
| US1 | As a gamer, I want to play an FPS in my terminal | Game runs and renders pseudo-3D view |
| US2 | As a player, I want different difficulty modes | Four modes available with varying AI |
| US3 | As a player, I want multiple weapons to choose | Nine weapons with different stats |
| US4 | As a player, I want to play with friends | Multiplayer mode supports 2-4 players |
| US5 | As a player, I want endless waves | Wave system with increasing difficulty |
| US6 | As a creator, I want to design my own levels | Level editor allows custom map creation |

---

## 5. Requirements

### Functional Requirements
- FR1: Raycasting engine renders walls correctly
- FR2: Player can move and look around
- FR3: Enemies spawn and can be shot
- FR4: Weapons fire and cause damage
- FR5: Health/ammo system works
- FR6: Wave progression increases difficulty
- FR7: Multiplayer splits screen for 2-4 players
- FR8: Level editor creates valid maps

### Performance Requirements
- PR1: Maintain 30+ FPS on standard hardware
- PR2: Input response < 100ms
- PR3: Support terminal sizes from 80x24 to fullscreen

---

## 6. Future Enhancements

| Enhancement | Description | Priority |
|-------------|-------------|----------|
| FE1 | Add actual sound effects using pygame | Medium |
| FE2 | Online multiplayer via network | Medium |
| FE3 | More enemy types and boss battles | High |
| FE4 | Save/load game progress | Low |
| FE5 | Achievements and leaderboards | Low |
| FE6 | Additional weapon types | Medium |
| FE7 | More procedurally generated levels | Medium |

---

*Document Version: 1.0*  
*Created: 2026-03-17*
