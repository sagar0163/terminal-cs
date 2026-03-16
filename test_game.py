"""Unit tests for Terminal CS"""

import pytest
from unittest.mock import Mock, patch
import sys
import io

# Mock required modules
sys.modules['curses'] = Mock()

from src.game import Player, Bullet, GameState


class TestPlayer:
    def test_player_initialization(self):
        player = Player(x=10, y=10)
        assert player.x == 10
        assert player.y == 10
        assert player.health == 100
    
    def test_player_move(self):
        player = Player(x=10, y=10)
        player.move(dx=1, dy=0)
        assert player.x == 11
    
    def test_player_shoot(self):
        player = Player(x=10, y=10)
        bullets = player.shoot()
        assert len(bullets) > 0


class TestBullet:
    def test_bullet_movement(self):
        bullet = Bullet(x=10, y=10, dx=1, dy=0)
        bullet.move()
        assert bullet.x == 11
    
    def test_bullet_out_of_bounds(self):
        bullet = Bullet(x=100, y=100, dx=1, dy=0)
        assert bullet.is_out_of_bounds(80, 24) == True


class TestGameState:
    def test_game_initialization(self):
        state = GameState()
        assert state.score == 0
        assert state.game_over == False
    
    def test_add_score(self):
        state = GameState()
        state.add_score(100)
        assert state.score == 100
    
    def test_game_over(self):
        state = GameState()
        state.end_game()
        assert state.game_over == True
