""" Breakout
    This is a simple breakout
    game. started long ago..
    """

import pygame
import pygame.freetype
import os
import sys

# Constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def load_image(name):
    """ Load image and return image object"""
    fullname = os.path.join(os.path.dirname(__file__), "assets", name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error as message:
        print(f"Cannot load image: {name}")
        raise SystemExit(message)
    return image

class Bat(pygame.sprite.Sprite):
    """ The player's bat
    """

    def __init__(self, xypos):
        super().__init__()
        self.image = load_image("bat.gif")
        self.rect = self.image.get_rect()
        self.x, self.y = xypos
        self.rect.center = (self.x, self.y)
        self.speed = 10

    def check_events(self, screen_width):
        keys = pygame.key.get_pressed()
        move_speed = self.speed
        if keys[pygame.K_SPACE]:
            move_speed *= 2

        if keys[pygame.K_LEFT]:
            if self.rect.left > 0:
                self.x -= move_speed
        if keys[pygame.K_RIGHT]:
            if self.rect.right < screen_width:
                self.x += move_speed

    def update(self, control, screen_width):
        if control:
            self.check_events(screen_width)
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)


class Ball(pygame.sprite.Sprite):
    """ The bouncing ball
    """

    def __init__(self, xypos):
        super().__init__()
        self.image = load_image("ball.gif")
        self.rect = self.image.get_rect()
        self.dx = 5
        self.dy = -5
        self.x, self.y = xypos
        self.rect.center = (int(self.x), int(self.y))
        self.hit_count = 0

    def check_bounds(self, screen_width, screen_height):
        if self.rect.right > screen_width:
            self.rect.right = screen_width
            self.dx *= -1
        elif self.rect.left < 0:
            self.rect.left = 0
            self.dx *= -1
        
        if self.rect.top < 0:
            self.rect.top = 0
            self.dy *= -1
            
        if self.rect.bottom > screen_height:
            return True # Ball lost
        return False

    def speed_up(self):
        """ Gradually increase ball speed based on hit count """
        if self.hit_count in [2, 10, 20]:
            self.dx *= 1.2
            self.dy *= 1.2
            self.hit_count += 1

    def update(self, screen_width, screen_height):
        self.x += self.dx
        self.y += self.dy
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        return self.check_bounds(screen_width, screen_height)

class Block(pygame.sprite.Sprite):
    """ A brick to be broken
    """

    def __init__(self, xypos):
        super().__init__()
        self.image = load_image("brick.gif")
        self.rect = self.image.get_rect()
        self.rect.center = xypos



class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.control = "menu"
        pygame.display.set_caption("Breakout!")

        self.update_background()
        
        # Load fonts
        font_path = os.path.join(os.path.dirname(__file__), "assets", "ModernDOS4378x8.ttf")
        try:
            self.font_small = pygame.freetype.Font(font_path, 16)
            self.font_large = pygame.freetype.Font(font_path, 32)
            self.font_medium = pygame.freetype.Font(font_path, 24)
        except pygame.error:
            # Fallback if font file is missing
            self.font_small = pygame.freetype.SysFont("Arial", 16)
            self.font_large = pygame.freetype.SysFont("Arial", 32)
            self.font_medium = pygame.freetype.SysFont("Arial", 24)
            
        self.lives = 2
        self.score = 0

    def update_background(self):
        self.background = pygame.Surface(self.screen.get_size())
        self.background.fill(WHITE)
        self.screen.blit(self.background, (0, 0))

    def handle_resize(self, size):
        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        self.update_background()

    def reset_level(self):
        self.background.fill(WHITE)
        sw, sh = self.screen.get_size()
        self.bat = Bat([sw // 2, sh - 30])
        self.ball = Ball([sw // 2, sh // 2 + 60])
        
        self.bricks = pygame.sprite.Group()
        brick_width = 40
        brick_height = 20
        padding = 10
        cols = sw // (brick_width + padding)
        rows = 5
        
        start_x = (sw - (cols * (brick_width + padding) - padding)) // 2
        
        for r in range(rows):
            for c in range(cols):
                x = start_x + c * (brick_width + padding) + brick_width // 2
                y = 100 + r * (brick_height + padding) + brick_height // 2
                self.bricks.add(Block((x, y)))

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.all_sprites.add(self.bat)
        self.all_sprites.add(self.ball)
        self.all_sprites.add(self.bricks)

    def play_level(self):
        self.reset_level()
        keep_going = True
        
        while keep_going:
            self.clock.tick(FPS)
            pygame.mouse.set_visible(False)
            
            sw, sh = self.screen.get_size()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    keep_going = False
                    self.control = "finish"
                if event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event.size)
                    sw, sh = self.screen.get_size()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    keep_going = False
                    self.control = "menu"

            # Update
            self.bat.update(True, sw)
            ball_lost = self.ball.update(sw, sh)
            
            if ball_lost:
                self.lives -= 1
                if self.lives < 0:
                    self.game_over()
                    keep_going = False
                else:
                    self.ball.x, self.ball.y = sw // 2, sh // 2 + 60
                    self.ball.dx = 5
                    self.ball.dy = -5
                    self.ball.rect.center = (int(self.ball.x), int(self.ball.y))

            # Collisions
            self.handle_collisions()

            if len(self.bricks) == 0:
                self.level_complete()
                keep_going = False

            # Draw
            self.draw()

        pygame.mouse.set_visible(True)

    def handle_collisions(self):
        # Ball and Bat
        if pygame.sprite.collide_rect(self.ball, self.bat):
            if self.ball.dy > 0: # Only bounce if moving down
                self.ball.dy *= -1
                self.ball.hit_count += 1
                self.ball.speed_up()
                
                # Change angle based on where it hit the bat
                offset = (self.ball.rect.centerx - self.bat.rect.centerx) / (self.bat.rect.width / 2)
                self.ball.dx += offset * 2

        # Ball and Bricks
        hit_bricks = pygame.sprite.spritecollide(self.ball, self.bricks, True)
        if hit_bricks:
            # Simple bounce logic
            self.ball.dy *= -1
            self.score += len(hit_bricks)

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.all_sprites.draw(self.screen)
        
        # UI
        sw, sh = self.screen.get_size()
        self.font_small.render_to(self.screen, (10, 10), f"Lives: {self.lives}", BLACK)
        self.font_small.render_to(self.screen, (sw - 140, 10), f"Score: {self.score}", BLACK)
        
        pygame.display.flip()

    def game_over(self):
        sw, sh = self.screen.get_size()
        self.font_large.render_to(self.screen, (sw // 2 - 140, sh // 2), "GAME OVER!", BLACK)
        pygame.display.flip()
        self.wait_for_input()
        self.control = "menu"

    def level_complete(self):
        sw, sh = self.screen.get_size()
        self.font_large.render_to(self.screen, (sw // 2 - 150, sh // 2), "LEVEL COMPLETE!", BLACK)
        pygame.display.flip()
        self.wait_for_input()
        self.control = "menu"

    def show_instructions(self):
        instructions = [
            "BREAKOUT",
            "",
            "Bounce the ball against ",
            "the bricks",
            "",
            "Keys:",
            "Arrows - Move Left/Right",
            "Space  - Move Faster",
            "Esc    - Return to Menu",
            "",
            "Press Any Key to Start"
        ]

        sw, sh = self.screen.get_size()
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, WHITE, (50, 50, sw - 100, sh - 100))
        
        for i, line in enumerate(instructions):
            self.font_small.render_to(self.screen, (100, 100 + i * 30), line, BLACK)
            
        pygame.display.flip()
        if self.wait_for_input() == "quit":
            self.control = "finish"
        else:
            self.control = "level1"

    def wait_for_input(self):
        pygame.time.wait(500)
        pygame.event.clear()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event.size)
                    # For instructions and game over, we might want to redraw
                    if self.control == "menu":
                        self.show_instructions()
                        return "resize" # Special return to trigger redraw
                if event.type == pygame.KEYDOWN:
                    return "key"
            self.clock.tick(FPS)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    game = Game(screen)

    while game.control != "finish":
        if game.control == "menu":
            res = game.show_instructions()
            if res == "resize":
                continue # Redraw menu
        elif game.control.startswith("level"):
            game.play_level()
            
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
