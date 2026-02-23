#!/usr/bin/env python3
"""
Terminal Counter-Strike
=====================
A pseudo-3D FPS game for Linux terminal with raycasting engine.

Features:
- Pseudo-3D raycasting rendering (Wolfenstein-style)
- Multiple game modes (Simple, Medium, Advanced)
- Multiple enemy types
- Powerups
- Random and pre-built maps
- Weapons system
- Score tracking

Controls:
- WASD / Arrow Keys: Move
- Space: Shoot
- 1/2/3: Switch weapon
- R: Reload
- P: Pause
- Q: Quit
"""

import os
import sys
import time
import random
import math
import curses
from collections import deque
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Game constants
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 25
MAP_WIDTH = 24
MAP_HEIGHT = 24
FOV = 60  # Field of view in degrees
HALF_FOV = FOV // 2
NUM_RAYS = SCREEN_WIDTH // 2
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 20  # Max render distance
TICK_RATE = 30


class GameMode(Enum):
    """Game difficulty modes"""
    SIMPLE = "simple"      # Just shooting, static enemies
    MEDIUM = "medium"     # Enemies shoot back
    ADVANCED = "advanced" # Multiple enemy types, powerups


class WeaponType(Enum):
    """Weapon types"""
    PISTOL = 1
    RIFLE = 2
    KNIFE = 3
    SHOTGUN = 4


@dataclass
class Weapon:
    """Weapon configuration"""
    name: str
    damage: int
    max_ammo: int
    reload_time: float
    fire_rate: float
    spread: float
    color: str


@dataclass
class EnemyType:
    """Enemy configuration"""
    name: str
    health: int
    damage: int
    speed: float
    color: int
    points: int


# Define weapons
WEAPONS = {
    WeaponType.PISTOL: Weapon("Pistol", 25, 12, 1.0, 0.5, 0.1, "P"),
    WeaponType.RIFLE: Weapon("Rifle", 35, 30, 2.0, 0.15, 0.05, "R"),
    WeaponType.KNIFE: Weapon("Knife", 50, 999, 0.3, 0.8, 0.3, "K"),
    WeaponType.SHOTGUN: Weapon("Shotgun", 80, 8, 2.5, 1.0, 0.4, "S"),
}

# Define enemy types
ENEMY_TYPES = {
    'grunt': EnemyType("Grunt", 100, 10, 0.03, 5, 100),
    'shotgun': EnemyType("Shotgunner", 150, 25, 0.02, 6, 200),
    'sniper': EnemyType("Sniper", 80, 50, 0.01, 7, 300),
    'boss': EnemyType("Boss", 500, 30, 0.015, 8, 1000),
}

# Define powerups
POWERUPS = {
    'health': {'symbol': '+', 'effect': 'health', 'value': 50},
    'ammo': {'symbol': '*', 'effect': 'ammo', 'value': 30},
    'armor': {'symbol': '#', 'effect': 'armor', 'value': 50},
    'damage': {'symbol': '!', 'effect': 'damage', 'value': 2},
    'speed': {'symbol': '%', 'effect': 'speed', 'value': 2},
}


class GameObject:
    """Base game object"""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class Player(GameObject):
    """Player class"""
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.angle = 0
        self.health = 100
        self.armor = 0
        self.weapon = WeaponType.PISTOL
        self.ammo = {WeaponType.PISTOL: 12, WeaponType.RIFLE: 30, WeaponType.SHOTGUN: 8}
        self.last_shot = 0
        self.last_reload = 0
        self.damage_multiplier = 1
        self.speed_multiplier = 1


class Enemy(GameObject):
    """Enemy class"""
    def __init__(self, x: float, y: float, enemy_type: str):
        super().__init__(x, y)
        self.type_data = ENEMY_TYPES[enemy_type]
        self.health = self.type_data.health
        self.last_shot = 0
        self.alive = True
        self.state = 'patrol'


class Powerup(GameObject):
    """Powerup class"""
    def __init__(self, x: float, y: float, ptype: str):
        super().__init__(x, y)
        self.ptype = ptype
        self.data = POWERUPS[ptype]
        self.active = True


class GameMap:
    """Map generation and management"""
    
    ARENA_MAP = [
        "########################",
        "#......................#",
        "#..####..........####..#",
        "#..#..............#....#",
        "#..#....#######...#....#",
        "#......#.......#......#",
        "#......#.......#......#",
        "#...####.......####...#",
        "#......................#",
        "#...####.......####...#",
        "#......#.......#......#",
        "#......#.......#......#",
        "#..#....#######...#....#",
        "#..#..............#....#",
        "#..####..........####..#",
        "#......................#",
        "########################",
    ]
    
    @staticmethod
    def generate_random(width: int, height: int, complexity: str = "medium") -> List[List[int]]:
        """Generate random map"""
        game_map = [[0 for _ in range(width)] for _ in range(height)]
        
        # Border walls
        for x in range(width):
            game_map[0][x] = 1
            game_map[height-1][x] = 1
        for y in range(height):
            game_map[y][0] = 1
            game_map[y][width-1] = 1
        
        # Random walls
        num_walls = {'simple': 15, 'medium': 25, 'advanced': 35}.get(complexity, 25)
        
        for _ in range(num_walls):
            x = random.randint(2, width - 3)
            y = random.randint(2, height - 3)
            size = random.randint(1, 3)
            
            for dy in range(-size, size + 1):
                for dx in range(-size, size + 1):
                    if 1 < y + dy < height - 2 and 1 < x + dx < width - 2:
                        game_map[y + dy][x + dx] = 1
        
        return game_map
    
    @staticmethod
    def load_arena() -> List[List[int]]:
        """Load pre-built arena"""
        game_map = []
        for row in GameMap.ARENA_MAP:
            game_map.append([1 if c == '#' else 0 for c in row])
        return game_map


class Raycaster:
    """Raycasting engine"""
    
    def __init__(self, game_map: List[List[int]]):
        self.game_map = game_map
        self.height = len(game_map)
        self.width = len(game_map[0])
    
    def cast_ray(self, player: Player, angle: float) -> Tuple[float, int, float]:
        """Cast a ray and return distance, wall type"""
        ray_angle = math.radians(angle)
        ray_dir_x = math.cos(ray_angle)
        ray_dir_y = -math.sin(ray_angle)
        
        map_x = int(player.x)
        map_y = int(player.y)
        
        side_dist_x = side_dist_y = 0
        delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else float('inf')
        delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else float('inf')
        
        step_x = step_y = 1
        if ray_dir_x < 0:
            step_x = -1
            side_dist_x = (player.x - map_x) * delta_dist_x
        else:
            side_dist_x = (map_x + 1.0 - player.x) * delta_dist_x
        
        if ray_dir_y < 0:
            step_y = -1
            side_dist_y = (player.y - map_y) * delta_dist_y
        else:
            side_dist_y = (map_y + 1.0 - player.y) * delta_dist_y
        
        hit = 0
        side = 0
        while hit == 0:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
            
            if map_x < 0 or map_x >= self.width or map_y < 0 or map_y >= self.height:
                hit = 1
                break
            
            if self.game_map[map_y][map_x] > 0:
                hit = 1
        
        if side == 0:
            perp_dist = (map_x - player.x + (1 - step_x) / 2) / ray_dir_x
        else:
            perp_dist = (map_y - player.y + (1 - step_y) / 2) / ray_dir_y
        
        perp_dist *= math.cos(math.radians(angle - player.angle))
        
        return perp_dist, self.game_map[map_y][map_x], 0, side


class Game:
    """Main game class"""
    
    def __init__(self, stdscr, mode: GameMode = GameMode.MEDIUM, map_type: str = "arena"):
        self.stdscr = stdscr
        self.mode = mode
        self.map_type = map_type
        
        self.game_over = False
        self.paused = False
        self.score = 0
        self.wave = 1
        
        if map_type == "arena":
            self.game_map = GameMap.load_arena()
        else:
            self.game_map = GameMap.generate_random(MAP_WIDTH, MAP_HEIGHT, mode.value)
        
        self.player = Player(3.5, 3.5)
        self.raycaster = Raycaster(self.game_map)
        self.enemies: List[Enemy] = []
        self.powerups: List[Powerup] = []
        
        self.spawn_enemies()
        self.last_time = time.time()
        
        self.setup_colors()
    
    def setup_colors(self):
        """Initialize curses colors"""
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
            curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
            curses.init_pair(7, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK)
    
    def spawn_enemies(self):
        """Spawn enemies based on wave and mode"""
        self.enemies.clear()
        
        num_enemies = min(3 + self.wave * 2, 10)
        
        for _ in range(num_enemies):
            while True:
                x = random.randint(2, MAP_WIDTH - 3)
                y = random.randint(2, MAP_HEIGHT - 3)
                dist = math.sqrt((x - self.player.x)**2 + (y - self.player.y)**2)
                if dist > 5 and self.game_map[y][x] == 0:
                    break
            
            if self.mode == GameMode.SIMPLE:
                etype = 'grunt'
            elif self.mode == GameMode.MEDIUM:
                etype = random.choice(['grunt', 'shotgun', 'sniper'])
            else:
                if self.wave % 3 == 0 and _ == 0:
                    etype = 'boss'
                else:
                    etype = random.choice(['grunt', 'shotgun', 'sniper'])
            
            self.enemies.append(Enemy(x, y, etype))
        
        if self.mode == GameMode.ADVANCED:
            for _ in range(random.randint(1, 3)):
                while True:
                    x = random.randint(2, MAP_WIDTH - 3)
                    y = random.randint(2, MAP_HEIGHT - 3)
                    if self.game_map[y][x] == 0:
                        break
                ptype = random.choice(list(POWERUPS.keys()))
                self.powerups.append(Powerup(x, y, ptype))
    
    def get_input(self):
        """Get keyboard input"""
        try:
            key = self.stdscr.getch()
            
            move_speed = 0.1 * self.player.speed_multiplier
            rot_speed = 3
            
            if key in [ord('w'), ord('W'), curses.KEY_UP]:
                new_x = self.player.x + math.cos(math.radians(self.player.angle)) * move_speed
                new_y = self.player.y - math.sin(math.radians(self.player.angle)) * move_speed
                if self.game_map[int(new_y)][int(new_x)] == 0:
                    self.player.x, self.player.y = new_x, new_y
            
            elif key in [ord('s'), ord('S'), curses.KEY_DOWN]:
                new_x = self.player.x - math.cos(math.radians(self.player.angle)) * move_speed
                new_y = self.player.y + math.sin(math.radians(self.player.angle)) * move_speed
                if self.game_map[int(new_y)][int(new_x)] == 0:
                    self.player.x, self.player.y = new_x, new_y
            
            elif key in [ord('a'), ord('A'), curses.KEY_LEFT]:
                self.player.angle = (self.player.angle - rot_speed) % 360
            
            elif key in [ord('d'), ord('D'), curses.KEY_RIGHT]:
                self.player.angle = (self.player.angle + rot_speed) % 360
            
            elif key == ord(' '):
                self.shoot()
            
            elif key == ord('1'):
                self.player.weapon = WeaponType.PISTOL
            elif key == ord('2'):
                self.player.weapon = WeaponType.RIFLE
            elif key == ord('3'):
                self.player.weapon = WeaponType.KNIFE
            
            elif key in [ord('r'), ord('R')]:
                self.reload()
            
            elif key in [ord('p'), ord('P')]:
                self.paused = not self.paused
            
            elif key in [ord('q'), ord('Q')]:
                self.game_over = True
                
        except:
            pass
    
    def shoot(self):
        """Player shoots"""
        weapon = WEAPONS[self.player.weapon]
        current_time = time.time()
        
        if current_time - self.last_shot < weapon.fire_rate:
            return
        
        if self.player.ammo.get(self.player.weapon, 0) <= 0:
            return
        
        self.last_shot = current_time
        self.player.ammo[self.player.weapon] -= 1
        
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            
            dx = enemy.x - self.player.x
            dy = enemy.y - self.player.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > MAX_DEPTH:
                continue
            
            angle_to_enemy = math.degrees(math.atan2(-dy, dx)) % 360
            angle_diff = (angle_to_enemy - self.player.angle + 180) % 360 - 180
            
            if abs(angle_diff) < 10:
                if self.check_line_of_sight(self.player.x, self.player.y, enemy.x, enemy.y):
                    damage = int(weapon.damage * self.player.damage_multiplier)
                    enemy.health -= damage
                    
                    if enemy.health <= 0:
                        enemy.alive = False
                        self.score += enemy.type_data.points
                        self.check_wave_complete()
    
    def check_line_of_sight(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        """Check if line of sight is clear"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        while True:
            if int(x) == int(x2) and int(y) == int(y2):
                return True
            
            if self.game_map[int(y)][int(x)] != 0:
                return False
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
    
    def reload(self):
        """Reload weapon"""
        weapon = WEAPONS[self.player.weapon]
        current_time = time.time()
        
        if current_time - self.last_reload < weapon.reload_time:
            return
        
        self.last_reload = current_time
        self.player.ammo[self.player.weapon] = weapon.max_ammo
    
    def update_enemies(self):
        """Update enemy AI"""
        if self.mode == GameMode.SIMPLE:
            return
        
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            
            dx = self.player.x - enemy.x
            dy = self.player.y - enemy.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 2:
                move_x = enemy.x + (dx / dist) * enemy.type_data.speed
                move_y = enemy.y + (dy / dist) * enemy.type_data.speed
                
                if self.game_map[int(move_y)][int(move_x)] == 0:
                    enemy.x, enemy.y = move_x, move_y
            
            if self.mode in [GameMode.MEDIUM, GameMode.ADVANCED]:
                if dist < MAX_DEPTH and random.random() < 0.02:
                    if self.check_line_of_sight(enemy.x, enemy.y, self.player.x, self.player.y):
                        damage = int(enemy.type_data.damage * random.uniform(0.8, 1.2))
                        
                        if self.player.armor > 0:
                            armor_damage = min(damage, self.player.armor)
                            self.player.armor -= armor_damage
                            damage -= armor_damage
                        
                        self.player.health -= damage
                        
                        if self.player.health <= 0:
                            self.game_over = True
    
    def check_powerups(self):
        """Check and apply powerups"""
        for powerup in self.powerups:
            if not powerup.active:
                continue
            
            dx = self.player.x - powerup.x
            dy = self.player.y - powerup.y
            if math.sqrt(dx*dx + dy*dy) < 0.5:
                if powerup.data['effect'] == 'health':
                    self.player.health = min(100, self.player.health + powerup.data['value'])
                elif powerup.data['effect'] == 'ammo':
                    for w in self.player.ammo:
                        self.player.ammo[w] += powerup.data['value']
                elif powerup.data['effect'] == 'armor':
                    self.player.armor = min(100, self.player.armor + powerup.data['value'])
                elif powerup.data['effect'] == 'damage':
                    self.player.damage_multiplier = powerup.data['value']
                elif powerup.data['effect'] == 'speed':
                    self.player.speed_multiplier = powerup.data['value']
                
                powerup.active = False
    
    def check_wave_complete(self):
        """Check if wave is complete"""
        if all(not e.alive for e in self.enemies):
            self.wave += 1
            self.player.health = min(100, self.player.health + 20)
            self.spawn_enemies()
    
    def render(self):
        """Render the game"""
        self.stdscr.clear()
        
        # Render 3D view
        for x in range(NUM_RAYS):
            angle = self.player.angle - HALF_FOV + x * DELTA_ANGLE
            dist, wall_type, wall_x, side = self.raycaster.cast_ray(self.player, angle)
            
            corrected_dist = dist * math.cos(math.radians(angle - self.player.angle))
            line_height = int(SCREEN_HEIGHT / corrected_dist) if corrected_dist > 0 else SCREEN_HEIGHT
            
            draw_start = max(0, (SCREEN_HEIGHT - line_height) // 2)
            draw_end = min(SCREEN_HEIGHT - 1, (SCREEN_HEIGHT + line_height) // 2)
            
            if dist < 3:
                color = 1
            elif dist < 7:
                color = 2
            else:
                color = 0
            
            # Ceiling
            for y in range(0, draw_start):
                self.stdscr.addch(y, x * 2, ' ')
                self.stdscr.addch(y, x * 2 + 1, ' ')
            
            # Wall
            if color > 0:
                char = '#' if side == 0 else '+'
                for y in range(draw_start, draw_end):
                    self.stdscr.addch(y, x * 2, char, curses.color_pair(color))
                    self.stdscr.addch(y, x * 2 + 1, char, curses.color_pair(color))
            
            # Floor
            for y in range(draw_end, SCREEN_HEIGHT):
                self.stdscr.addch(y, x * 2, '.', curses.color_pair(3))
                self.stdscr.addch(y, x * 2 + 1, '.', curses.color_pair(3))
        
        # Render sprites
        self.render_sprites()
        
        # Render UI
        self.render_ui()
        
        self.stdscr.refresh()
    
    def render_sprites(self):
        """Render enemy and powerup sprites"""
        sprites = []
        
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            dx = enemy.x - self.player.x
            dy = enemy.y - self.player.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < MAX_DEPTH:
                angle = math.degrees(math.atan2(-dy, dx)) - self.player.angle
                sprites.append(('enemy', dist, angle, 5))
        
        for powerup in self.powerups:
            if not powerup.active:
                continue
            dx = powerup.x - self.player.x
            dy = powerup.y - self.player.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < MAX_DEPTH:
                angle = math.degrees(math.atan2(-dy, dx)) - self.player.angle
                sprites.append(('powerup', dist, angle, 7))
        
        sprites.sort(key=lambda x: -x[1])
        
        for stype, dist, angle, color in sprites:
            angle = (angle + 180) % 360 - 180
            
            if abs(angle) < HALF_FOV:
                screen_x = int((angle + HALF_FOV) / FOV * SCREEN_WIDTH)
                
                sprite_height = int(SCREEN_HEIGHT / dist) if dist > 0 else SCREEN_HEIGHT
                sprite_height = min(sprite_height, SCREEN_HEIGHT)
                
                draw_start = max(0, (SCREEN_HEIGHT - sprite_height) // 2)
                draw_end = min(SCREEN_HEIGHT - 1, (SCREEN_HEIGHT + sprite_height) // 2)
                
                char = 'E' if stype == 'enemy' else 'P'
                
                for y in range(draw_start, draw_end):
                    self.stdscr.addch(y, screen_x, char, curses.color_pair(color))
    
    def render_ui(self):
        """Render UI elements"""
        health_str = f"HP: {self.player.health}/100"
        self.stdscr.addstr(0, 1, health_str, curses.color_pair(8))
        
        if self.player.armor > 0:
            armor_str = f"ARMOR: {self.player.armor}/100"
            self.stdscr.addstr(0, 20, armor_str, curses.color_pair(8))
        
        weapon = WEAPONS[self.player.weapon]
        ammo = self.player.ammo.get(self.player.weapon, 0)
        ammo_str = f"AMMO: {ammo}/{weapon.max_ammo}"
        self.stdscr.addstr(0, 45, ammo_str, curses.color_pair(8))
        
        self.stdscr.addstr(0, 65, f"WEAPON: {weapon.name}", curses.color_pair(8))
        
        score_str = f"SCORE: {self.score}  WAVE: {self.wave}"
        self.stdscr.addstr(1, 1, score_str, curses.color_pair(8))
        
        mode_str = f"MODE: {self.mode.value.upper()}"
        self.stdscr.addstr(1, 50, mode_str, curses.color_pair(8))
        
        controls = "WASD:Move SPACE:Shoot 1-3:Weapon R:Reload P:Pause Q:Quit"
        self.stdscr.addstr(SCREEN_HEIGHT - 1, (SCREEN_WIDTH - len(controls)) // 2, controls, curses.color_pair(8))
        
        if self.paused:
            self.stdscr.addstr(SCREEN_HEIGHT // 2, SCREEN_WIDTH // 2 - 5, "PAUSED", curses.color_pair(8))
        
        if self.game_over:
            self.stdscr.addstr(SCREEN_HEIGHT // 2 - 2, SCREEN_WIDTH // 2 - 9, "GAME OVER", curses.color_pair(5))
            self.stdscr.addstr(SCREEN_HEIGHT // 2 - 1, SCREEN_WIDTH // 2 - 11, f"Final Score: {self.score}", curses.color_pair(8))
            self.stdscr.addstr(SCREEN_HEIGHT // 2, SCREEN_WIDTH // 2 - 12, f"Reached Wave: {self.wave}", curses.color_pair(8))
    
    def run(self):
        """Main game loop"""
        curses.curs_set(0)
        self.stdscr.nodelay(True)
        
        while not self.game_over:
            self.get_input()
            
            if not self.paused:
                self.update_enemies()
                self.check_powerups()
            
            self.render()
            time.sleep(1 / TICK_RATE)


def show_menu(stdscr):
    """Show game mode selection menu"""
    curses.curs_set(0)
    
    modes = [
        ("1", "SIMPLE", "Just shooting, static enemies"),
        ("2", "MEDIUM", "Enemies shoot back"),
        ("3", "ADVANCED", "Multiple enemy types + powerups"),
    ]
    
    maps = [
        ("a", "ARENA", "Pre-built arena map"),
        ("r", "RANDOM", "Randomly generated map"),
    ]
    
    selected_mode = 1
    selected_map = 0
    
    while True:
        stdscr.clear()
        
        title = """
 TERMStrike - Console FPS
"""
        stdscr.addstr(1, 30, title, curses.color_pair(1) | curses.A_BOLD)
        
        stdscr.addstr(8, 2, "SELECT MODE:", curses.color_pair(1) | curses.A_BOLD)
        for i, (key, name, desc) in enumerate(modes):
            prefix = ">> " if i == selected_mode else "   "
            stdscr.addstr(10 + i, 5, f"{prefix}[{key}] {name} - {desc}", curses.color_pair(1))
        
        stdscr.addstr(15, 2, "SELECT MAP:", curses.color_pair(1) | curses.A_BOLD)
        for i, (key, name, desc) in enumerate(maps):
            prefix = ">> " if i == selected_map else "   "
            stdscr.addstr(17 + i, 5, f"{prefix}[{key}] {name} - {desc}", curses.color_pair(1))
        
        stdscr.addstr(22, 2, "Press ENTER to start", curses.color_pair(1))
        
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key in [ord('1'), ord('2'), ord('3')]:
            selected_mode = ord(str(key)) - ord('1')
        elif key in [ord('a'), ord('A'), ord('r'), ord('R')]:
            selected_map = 0 if key in [ord('a'), ord('A')] else 1
        elif key in [curses.KEY_ENTER, 10]:
            break
    
    modes_list = [GameMode.SIMPLE, GameMode.MEDIUM, GameMode.ADVANCED]
    maps_list = ["arena", "random"]
    
    return modes_list[selected_mode], maps_list[selected_map]


def main(stdscr):
    """Main entry point"""
    mode, map_type = show_menu(stdscr)
    game = Game(stdscr, mode, map_type)
    game.run()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure you're running in a terminal that supports curses.")
        sys.exit(1)
