import pygame
from sys import exit
from random import randint, choice


class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('graphics/powerUp.png').convert_alpha()
        self.rect = self.image.get_rect(midbottom=(randint(900, 1100), 300))

    def update(self):
        self.rect.x -= 5
        if self.rect.x <= -100:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.jump = False
        self.invincible = False
        self.on_ground = True
        self.gravity_increase_time = pygame.time.get_ticks() # Give your gravity a time to start increasing
        self.gravity_increase_interval = 1  # Counts the number of times gravity has increased

        self.frame_counter = 0
        player_walk_1 = pygame.image.load('graphics/Player/player_walk_1.png').convert_alpha()
        player_walk_2 = pygame.image.load('graphics/Player/player_walk_2.png').convert_alpha()
        self.player_walk = [player_walk_1, player_walk_2]
        self.player_index = 0
        self.player_jump = pygame.image.load('graphics/Player/jump.png').convert_alpha()
        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom=(80, 300))
        self.gravity = 0
        self.jump_sound = pygame.mixer.Sound('audio/jump.mp3')
        self.jump_sound.set_volume(0.25)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not self.jump and self.on_ground:
            self.gravity = -15
            self.jump_sound.play()
            self.jump = True
            self.on_ground = False
        elif not keys[pygame.K_SPACE]:
            self.jump = False

    def apply_gravity(self):
        # If current time is greater than the start time plus (30 seconds * how many times gravity has already increased)
        if pygame.time.get_ticks() > self.gravity_increase_time + (30000 * self.gravity_increase_interval) and self.gravity_increase_interval <= 4:
            self.gravity += 0.05  # Increase the gravity
            self.gravity_increase_interval += 1  # Increase the interval count

        if self.jump and self.gravity < -3:
            self.gravity += 0.5
        else:
            self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 300:
            self.rect.bottom = 300
            self.on_ground = True

    def animation(self):
        self.frame_counter += 1
        if self.rect.bottom < 300:
            self.image = self.player_jump
        else:
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk): self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]
            if self.invincible and self.frame_counter % 10 < 5: # flash every 10 frames
                invincible_image = self.image.copy()
                invincible_image.fill((204, 255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)  # Change color to green
                self.image = invincible_image

    def become_invincible(self):
        self.invincible = True
        pygame.time.set_timer(pygame.USEREVENT + 5, 5000)  # Invincibility lasts for 5 seconds

    def end_invincibility(self):
        self.invincible = False
        self.image = self.player_walk[int(self.player_index)]  # Reset color

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        self.last_obstacle_pos = 0

        if type == 'fly':
            fly_1 = pygame.image.load(
                'graphics/Fly/Fly1.png').convert_alpha()
            fly_2 = pygame.image.load(
                'graphics/Fly/Fly2.png').convert_alpha()
            self.frames = [fly_1, fly_2]
            y_pos = 190

        else:
            snail_1 = pygame.image.load('graphics/snail/snail1.png').convert_alpha()
            snail_2 = pygame.image.load('graphics/snail/snail2.png').convert_alpha()
            self.frames = [snail_1, snail_2]
            y_pos = 300

        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        x_pos = choice([900, 915, 930, 945, 960, 975, 990, 1005])
        self.rect = self.image.get_rect(midbottom=(x_pos, y_pos))

    def animation(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames): self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.animation()
        self.rect.x -= 5
        self.destroy()

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()


def display_score():
    current_time = int(pygame.time.get_ticks() / 1000) - start_time  # info to use
    score_surf = test_font.render(f'Score: {current_time}', False, (64, 64, 64))
    score_rect = score_surf.get_rect(center=(400, 50))
    screen.blit(score_surf, score_rect)
    return current_time


def display_instruction(score) -> None:
    game_name = test_font.render('RUN', False, (111, 196, 169))
    game_name_rect = game_name.get_rect(center=(400, 80))
    screen.blit(game_name, game_name_rect)
    if score == 0:
        instructions = "Press Space to Run"
        instru_surf = test_font.render(instructions, False, (111, 196, 169))
        instru_rect = instru_surf.get_rect(center=(400, 350))
        screen.blit(instru_surf, instru_rect)
    else:
        score_message = test_font.render(f'Your Score: {score}', False, (111, 196, 169))
        score_message_rect = score_message.get_rect(center=(400, 330))
        screen.blit(score_message, score_message_rect)


def collision_sprite():
    # Check for collisions between the player and the obstacles
    if pygame.sprite.spritecollide(player.sprite, obstacle_group, False):
        # If the player is invincible, ignore the collision
        if player.sprite.invincible:
            print("Player collided with an obstacle but is invincible")
            return True
        # If the player is not invincible, end the game
        else:
            obstacle_group.empty()
            return False
            print("Player collided with an obstacle and is not invincible")

    else:
        return True


pygame.init()

#miscillaneos
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("Runner")
clock = pygame.time.Clock()
bg_sound = pygame.mixer.Sound('audio/music.wav')
bg_sound.set_volume(0.125)
bg_sound.play(loops = -1)
power_up_time = 0


# Moving Stuff
obstacle_group = pygame.sprite.Group()
player = pygame.sprite.GroupSingle()
player.add(Player())
power_up_group = pygame.sprite.Group()

#background
test_font = pygame.font.Font('font/Pixeltype.ttf', 50)
test_surface = pygame.image.load('graphics/Sky.png').convert()
test_surface2 = pygame.image.load('graphics/ground.png').convert()

#Pre-Game & Post-Game
player_stand = pygame.image.load(
    'graphics/Player/player_stand.png').convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand, 0, 2)
player_stand_rect = player_stand.get_rect(center=(400, 200))
game_active = False
start_time = 0
score = 0

#Timers
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, randint(800, 1400))
snail_animation_timer = pygame.USEREVENT + 2
pygame.time.set_timer(snail_animation_timer, 500)
fly_animation_timer = pygame.USEREVENT + 3
pygame.time.set_timer(fly_animation_timer, 200)

power_up_timer = pygame.USEREVENT + 4
pygame.time.set_timer(power_up_timer, randint(30000, 60000))


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if not game_active:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_active = True
                start_time = int(pygame.time.get_ticks() / 1000)
        if game_active:
            if event.type == obstacle_timer:
                obstacle_group.add(Obstacle(choice(['fly', 'snail', 'snail', 'snail'])))

            if event.type == power_up_timer:
                power_up_group.add(PowerUp())
                print("PUP")

            if event.type == pygame.USEREVENT + 5:
                player.sprite.end_invincibility()

    #Game Loop
    if game_active:
        screen.blit(test_surface, (0, 0))
        screen.blit(test_surface2, (0, 300))
        score = display_score()

        power_up_group.draw(screen)
        power_up_group.update()

        player.draw(screen)
        player.update()

        obstacle_group.draw(screen)
        obstacle_group.update()

        if pygame.sprite.spritecollide(player.sprite, power_up_group, True):
            player.sprite.become_invincible()
            print("Player has collided with a power-up")  # Add this line

        game_active = collision_sprite()

    else:
        screen.fill((94, 129, 162))
        screen.blit(player_stand, player_stand_rect)
        player_gravity = 0
        display_instruction(score)

    pygame.display.update()
    clock.tick(60)
