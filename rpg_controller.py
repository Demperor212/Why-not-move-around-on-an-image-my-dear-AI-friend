#!/usr/bin/env python3
"""
2D RPG Character Controller App

A pygame-based application with:
- Visual display showing a red dot character on a switchable background
- Terminal interface to control character movement using move(direction, speed, length)
"""

import pygame
import math
import threading
import queue
import sys
import os
import time

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Character:
    """Represents the player character (red dot)"""
    
    def __init__(self, x, y, radius=10):
        self.x = x
        self.y = y
        self.radius = radius
        self.angle = 0  # Current facing angle in degrees
        self.current_movement = None  # Stores ongoing movement data
    
    def start_move(self, direction_degrees, speed, length_seconds):
        """
        Start an animated movement in a given direction.
        
        Args:
            direction_degrees: Direction in degrees (0 = right, 90 = up, 180 = left, 270 = down)
            speed: Speed in pixels per second
            length_seconds: Duration of movement in seconds
        """
        # Convert degrees to radians (pygame y-axis is inverted, so we negate)
        rad = math.radians(-direction_degrees)
        
        # Calculate velocity components
        vx = speed * math.cos(rad)
        vy = speed * math.sin(rad)
        
        # Store movement data for animation
        self.current_movement = {
            'vx': vx,
            'vy': vy,
            'start_time': time.time(),
            'duration': length_seconds,
            'direction': direction_degrees
        }
        
        # Update facing angle immediately
        self.angle = direction_degrees
    
    def update(self):
        """Update character position based on ongoing movement (call every frame)"""
        if self.current_movement is None:
            return
        
        current_time = time.time()
        elapsed = current_time - self.current_movement['start_time']
        
        if elapsed >= self.current_movement['duration']:
            # Movement complete
            self.current_movement = None
            return
        
        # Calculate delta time since last frame
        dt = 1.0 / FPS  # Approximate frame time
        
        # Update position
        self.x += self.current_movement['vx'] * dt
        self.y += self.current_movement['vy'] * dt
        
        # Keep character within bounds
        self.x = max(self.radius, min(WINDOW_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(WINDOW_HEIGHT - self.radius, self.y))
    
    def draw(self, surface):
        """Draw the character as a red dot"""
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius)
        # Draw a small line indicating direction
        rad = math.radians(-self.angle)
        end_x = self.x + self.radius * 1.5 * math.cos(rad)
        end_y = self.y + self.radius * 1.5 * math.sin(rad)
        pygame.draw.line(surface, WHITE, (self.x, self.y), (end_x, end_y), 2)


class BackgroundManager:
    """Manages background images"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.current_bg_index = 0
        self.backgrounds = []
        
        # Create default solid color backgrounds
        self._create_default_backgrounds()
    
    def _create_default_backgrounds(self):
        """Create some default colored backgrounds"""
        colors = [
            (50, 100, 50),   # Grass green
            (100, 50, 50),   # Dirt brown
            (50, 50, 100),   # Water blue
            (100, 100, 100), # Stone gray
            (100, 100, 50),  # Sand yellow
        ]
        
        for color in colors:
            bg = pygame.Surface((self.width, self.height))
            bg.fill(color)
            self.backgrounds.append(bg)
    
    def load_image(self, filepath):
        """Load a custom background image"""
        try:
            bg = pygame.image.load(filepath)
            bg = pygame.transform.scale(bg, (self.width, self.height))
            self.backgrounds.append(bg)
            print(f"Loaded background: {filepath}")
            return True
        except Exception as e:
            print(f"Error loading background: {e}")
            return False
    
    def switch_background(self, index=None):
        """Switch to next background or specific index"""
        if not self.backgrounds:
            return
        
        if index is not None:
            self.current_bg_index = index % len(self.backgrounds)
        else:
            self.current_bg_index = (self.current_bg_index + 1) % len(self.backgrounds)
    
    def get_current(self):
        """Get current background surface"""
        if self.backgrounds:
            return self.backgrounds[self.current_bg_index]
        else:
            bg = pygame.Surface((self.width, self.height))
            bg.fill(BLACK)
            return bg


class GameApp:
    """Main game application"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("2D RPG Character Controller")
        self.clock = pygame.time.Clock()
        
        self.character = Character(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.bg_manager = BackgroundManager(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        self.running = True
        self.command_queue = queue.Queue()
        
        # Font for displaying info
        self.font = pygame.font.Font(None, 36)
    
    def handle_events(self):
        """Handle pygame events - non-blocking to prevent freezing"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_b:
                    # Switch background with 'b' key
                    self.bg_manager.switch_background()
            # Explicitly handle window events to prevent freezing when moving/resizing
            elif event.type == pygame.WINDOWEVENT:
                # Window moved, resized, etc. - just continue processing
                pass
            elif event.type == pygame.ACTIVEEVENT:
                # Window focus changed - just continue processing
                pass
    
    def process_commands(self):
        """Process commands from the terminal thread"""
        try:
            while True:
                cmd = self.command_queue.get_nowait()
                if cmd[0] == 'move':
                    direction, speed, length = cmd[1:]
                    self.character.start_move(direction, speed, length)
                    print(f"Started movement: direction={direction}°, speed={speed}, length={length}s")
                elif cmd[0] == 'switch_bg':
                    self.bg_manager.switch_background(cmd[1] if len(cmd) > 1 else None)
                    print(f"Switched background")
                elif cmd[0] == 'quit':
                    self.running = False
        except queue.Empty:
            pass
    
    def draw(self):
        """Render the game"""
        # Draw background
        self.screen.blit(self.bg_manager.get_current(), (0, 0))
        
        # Draw character
        self.character.draw(self.screen)
        
        # Draw info
        info_text = f"Pos: ({self.character.x:.0f}, {self.character.y:.0f}) | Angle: {self.character.angle:.0f}° | B=Switch BG | ESC=Quit"
        text_surface = self.font.render(info_text, True, WHITE)
        text_rect = text_surface.get_rect(bottomleft=(10, WINDOW_HEIGHT - 10))
        
        # Draw text with shadow
        shadow_surface = self.font.render(info_text, True, BLACK)
        shadow_rect = shadow_surface.get_rect(bottomleft=(12, WINDOW_HEIGHT - 12))
        self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(text_surface, text_rect)
        
        pygame.display.flip()
    
    def run_visual(self):
        """Run the visual part of the application"""
        while self.running:
            self.handle_events()
            self.process_commands()
            self.character.update()  # Update character position for smooth animation
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
    
    def send_command(self, command):
        """Send a command to the visual thread"""
        self.command_queue.put(command)


def terminal_interface(app):
    """Terminal interface for controlling the character"""
    
    print("=" * 50)
    print("2D RPG Character Controller - Terminal Interface")
    print("=" * 50)
    print("\nCommands:")
    print("  move(direction, speed, length) - Move character")
    print("    - direction: degrees (0=right, 90=up, 180=left, 270=down)")
    print("    - speed: pixels per second")
    print("    - length: duration in seconds")
    print("  switch_bg([index]) - Switch background (optional index)")
    print("  quit - Exit the application")
    print("  help - Show this help message")
    print("=" * 50)
    
    while app.running:
        try:
            user_input = input("\n>>> ").strip()
            
            if not user_input:
                continue
            
            # Parse move command
            if user_input.startswith("move("):
                try:
                    # Extract arguments
                    args_str = user_input[5:-1]  # Remove "move(" and ")"
                    args = [float(x.strip()) for x in args_str.split(",")]
                    
                    if len(args) != 3:
                        print("Error: move() requires exactly 3 arguments (direction, speed, length)")
                        continue
                    
                    direction, speed, length = args
                    app.send_command(('move', direction, speed, length))
                    
                except ValueError as e:
                    print(f"Error parsing arguments: {e}")
                except Exception as e:
                    print(f"Error: {e}")
            
            # Parse switch_bg command
            elif user_input.startswith("switch_bg"):
                try:
                    if "(" in user_input and ")" in user_input:
                        args_str = user_input[user_input.index("(")+1:user_input.index(")")]
                        if args_str.strip():
                            index = int(args_str.strip())
                            app.send_command(('switch_bg', index))
                        else:
                            app.send_command(('switch_bg',))
                    else:
                        app.send_command(('switch_bg',))
                except Exception as e:
                    print(f"Error: {e}")
            
            # Quit command
            elif user_input.lower() == "quit":
                app.send_command(('quit',))
                break
            
            # Help command
            elif user_input.lower() == "help":
                print("\nCommands:")
                print("  move(direction, speed, length) - Move character")
                print("  switch_bg([index]) - Switch background")
                print("  quit - Exit")
                print("  help - Show help")
            
            else:
                print(f"Unknown command: {user_input}")
                print("Type 'help' for available commands")
        
        except KeyboardInterrupt:
            print("\nInterrupted!")
            app.send_command(('quit',))
            break
        except EOFError:
            break


def main():
    """Main entry point"""
    print("Starting 2D RPG Character Controller...")
    
    # Create the game application
    app = GameApp()
    
    # Start visual thread
    visual_thread = threading.Thread(target=app.run_visual)
    visual_thread.daemon = True
    visual_thread.start()
    
    # Run terminal interface in main thread
    try:
        terminal_interface(app)
    finally:
        # Wait for visual thread to finish
        visual_thread.join(timeout=2)
    
    print("Application closed.")


if __name__ == "__main__":
    main()
