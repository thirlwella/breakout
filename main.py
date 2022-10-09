""" Breakout
    This is a simple breakout
    game. started long ago..
    """

import pygame
import pygame.freetype

pygame.init()
screen = pygame.display.set_mode((640, 480))

class Bat(pygame.sprite.Sprite):
    """ Bat
    """

    def __init__(self, xypos):
        """ Creates Bat in xypos 100,450
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("bat.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.dx = 0
        self.relative_dx = 0
        (self.x, self.y) = xypos
        self.prev_x = self.x
        self.rect.centerx = self.x
        self.rect.centery = self.y


    def checkEvents(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            if self.rect.left > 0:
                self.x += -10
        if keys[pygame.K_RIGHT]:
            if self.rect.right < screen.get_width():
                self.x += 10
        # Space bar doubles the speed
        if keys[pygame.K_SPACE]:
            if keys[pygame.K_LEFT]:
                if self.rect.left > 0 + 10:
                    self.x += -20
            if keys[pygame.K_RIGHT]:
                if self.rect.right < screen.get_width() - 10:
                    self.x += 20

    def update(self, control):
        if control:
            self.checkEvents()
        self.rect.centerx = self.x
        self.rect.centery = self.y


class Ball(pygame.sprite.Sprite):
    """ Ball
    """

    def __init__(self, xypos):
        """ Creates Ball in xypos 100,450
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("ball.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.dx = 5
        self.dy = -5
        self.relative_dx = 0
        self.relative_dy = 0
        (self.x, self.y) = xypos
        self.prev_x = self.x
        self.rect.centerx = self.x
        self.rect.centery = self.y
        self.count = 0

    def checkEvents(self):

        scrWidth = screen.get_width()
        scrHeight = screen.get_height()
        offRight = offLeft = offTop = offBottom = offScreen = False

        if self.rect.right > scrWidth:
            offRight = True
        if self.rect.left < 0:
            offLeft = True
        if self.y > scrHeight:
            offBottom = True
        if self.y < 0:
            offTop = True

        if offLeft or offRight:
            self.dx *= -1
            self.relative_dx *= -1
        if offTop or offBottom:
            self.dy *= -1
            self.relative_dy *= -1

        # This speed ups the ball
        if self.count == 2:
            self.dy *= 1.20
            self.dx *= 1.20
            self.count += 1
        elif self.count == 10:
            self.dy *= 1.20
            self.dx *= 1.20
            self.count += 1
        elif self.count == 20:
            self.dy *= 1.20
            self.dx *= 1.20
            self.count += 1

    def update(self):
        self.checkEvents()
        self.x += self.relative_dx
        self.y += self.relative_dy
        self.rect.centerx = self.x
        self.rect.centery = self.y

class Block(pygame.sprite.Sprite):
    """ Block
    """

    def __init__(self, xypos):
        """ Creates block in xypos
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("brick.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        (self.x, self.y) = xypos
        self.rect.centerx = self.x
        self.rect.centery = self.y



class Game():
    def __init__(self):
        # Set up the drawing window
        self.ball_speed = 1
        self.control = ""
        pygame.display.set_caption("Breakout!")

        self.background = pygame.Surface(screen.get_size())
        self.background.fill((255, 255, 255))
        screen.blit(self.background, (0, 0))
        self.scrHeight = screen.get_height()
        self.my_ft_font = pygame.freetype.Font("ModernDOS4378x8.ttf", 16)
        self.my_ft_font2 = pygame.freetype.Font("ModernDOS4378x8.ttf", 32)
        self.my_ft_font3 = pygame.freetype.Font("ModernDOS4378x8.ttf", 24)
        self.lives = 2
        self.score = 0


    def level(self, level):
        self.background.fill((255, 255, 255))
        screen.blit(self.background, (0, 0))
        bat = Bat([250, 450])
        ball = Ball([250, 300])
        #scoreboard = Scoreboard()
        bricks = []

        for x in range(19, 669, 50):
            for y in range(100, 225, 25):
                coords = [x, y]
                bricks.append(Block(coords))

        blockGroup = pygame.sprite.OrderedUpdates(bricks)
        blockSprites = pygame.sprite.Group(blockGroup)

        batSprite = pygame.sprite.Group(bat)
        ballSprite = pygame.sprite.Group(ball)

        clock = pygame.time.Clock()
        keepGoing = True
        while keepGoing:
            clock.tick(30)
            pygame.mouse.set_visible(False)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    keepGoing = False
                    self.control = "menu"

            #Calculate relative speeds of objects (convert to a factor of 1)
            #find the fastest movement either x or y axis
            speeds = []
            for _ in ballSprite:
                speeds.append(abs(_.dx))
                speeds.append(abs(_.dy))
            for _ in ballSprite:
                speeds.append(abs(_.dx))
            # need to think about implications of turning into an integer to loop..
            fastest_object = int(max(speeds))
            #update all objects with their relative speed
            # They will move this whilst the fasted object will move 1
            for _ in ballSprite:
                _.relative_dx = _.dx / fastest_object
                _.relative_dy = _.dy / fastest_object
            for _ in ballSprite:
                _.relative_dx = _.dx / fastest_object

            #Add a loop here for ball speed
            for updates in range (1,fastest_object):
                if updates == 1:
                    batSprite.update(True)
                else:
                    batSprite.update(False)
                ballSprite.update()
                blockSprites.update()

                # collision detection bat against ball
                hitbat = pygame.sprite.spritecollideany(ball,batSprite)
                if hitbat:
                    if ball.rect.top + 1 == hitbat.rect.bottom or ball.rect.bottom - 1 == hitbat.rect.top:
                        ball.dy *= -1
                        ball.relative_dy *= -1
                        #calculate any adjustment needed to horizontal movement of the ball speed
                        # will split into 3 regions, right , mid and left
                        bat_thirds = (hitbat.rect.right - hitbat.rect.left) /3
                        if ball.rect.left >= (hitbat.rect.left + (bat_thirds *2)):
                            #Right hand side
                            ball.dx += 1
                            ball.relative_dx += 1
                        elif ball.rect.left >= (hitbat.rect.left + (bat_thirds)):
                            # Middle
                            pass
                        else:
                            # Left
                            ball.dx -= 1
                            ball.relative_dx -= 1

                    else:
                        if ball.rect.right - 1 == hitbat.rect.left or ball.rect.left + 1 == hitbat.rect.right:
                            ball.dx *= -1
                            ball.relative_dx *= -1
                    ball.count += 1

                hitbrick = pygame.sprite.spritecollideany(ball, blockSprites)

                if hitbrick:
                    if ball.rect.top + 1 == hitbrick.rect.bottom or ball.rect.bottom - 1 == hitbrick.rect.top:
                        ball.dy *= -1
                        ball.relative_dy *= -1
                    else:
                        if ball.rect.right - 1 == hitbrick.rect.left or ball.rect.left + 1 == hitbrick.rect.right:
                            ball.dx *= -1
                            ball.relative_dx *= -1
                    hitbrick.kill()
                    self.score +=1

                if ball.y > self.scrHeight:
                    if self.lives == 0:
                        self.game_finish()
                        keepGoing = False
                        # Message stating end of game
                    self.lives += -1
                    ball.x = 250
                    ball.y = 300
                    if ball.dy >= 0:
                        ball.dy *= -1
                    ball.dx = 5

            # update to movements completed, now time to refresh the screen
            batSprite.clear(screen, self.background)
            ballSprite.clear(screen, self.background)
            blockSprites.clear(screen, self.background)

            batSprite.draw(screen)
            ballSprite.draw(screen)
            blockSprites.draw(screen)

            text = "Lives: %d" % (self.lives)
            self.my_ft_font.render_to(screen, (0, 0), text, (0, 0, 0),(255,255,255))
            text = "Score: %d"  % (self.score)
            self.my_ft_font.render_to(screen, (450, 0), text, (0, 0, 0), (255, 255, 255))

            pygame.display.flip()

            if len(blockSprites) == 0:
                keepGoing = False
                self.my_ft_font2.render_to(screen, (50, 300), "LEVEL COMPLETE!", (0, 0, 0), (255, 255, 255))
                pygame.display.flip()
                waiting = Wait_for_key_press()
                waiting.update(self.background)
                return "level1"



        pygame.mouse.set_visible(True)
        return

    def update(self):
        self.text = "Lives: %d" % (self.lives)

    def game_finish(self):
        print("Game over")

        self.my_ft_font2.render_to(screen, (160, 300), "GAME OVER!", (0, 0, 0), (255, 255, 255))
        pygame.display.flip()
        self.control = "menu"
        waiting = Wait_for_key_press()
        test = waiting.update(self.background)

    def instructions(self):

        insLabels = []
        instructions = (
            "",
            "",
            "    This is BREAKOUT, bounce the ball      ",
            "           against the bricks              ",
            "",
            "       written by Adam Thirlwell           ",
            "",
            "",
            "    Keys : Arrows = left and right,        ",
            "           space = go faster               "
            "",
            "        Press Any Key to Continue          ",
        )

        background = pygame.Surface(screen.get_size())
        background.fill((0, 0, 0))
        screen.blit(background, (0, 0))
        pygame.draw.rect(screen, (255,255,255), (30, 30, screen.get_width()-60, self.background.get_height()-60))


        row = 0
        for line in instructions:
            self.my_ft_font.render_to(screen, (0, 0 + (row * 24)), line, (0, 0, 0), (255, 255, 255))
            row += 1
        pygame.display.flip()
        waiting = Wait_for_key_press()
        test = waiting.update(self.background)
        if test == 'finish':
            self.control = "finish"
        else:
            self.control = 'level1'

        pygame.mouse.set_visible(True)

class Wait_for_key_press:
    def __init__(self):
        self.wait = True

    def update(self,surface):
        pygame.time.wait(1000)
        pygame.event.clear()
        while self.wait:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                self.wait = False
                return "finish"
            elif event.type == pygame.KEYDOWN:
                self.wait = False


def main():
    pygame.init()
    breakout = Game()
    breakout.control = "menu"

    donePlaying = False

    while not donePlaying:
        if not donePlaying:
            # open main menu
            if breakout.control == "menu":
                breakout.instructions()
            # open level to play
            if breakout.control[:5] == "level":
                level_num = int(breakout.control[5:])
                breakout.level(level_num)
            if breakout.control == "finish":
                donePlaying = True
    # Done! Time to quit.
    pygame.quit()


if __name__ == "__main__":
    main()
