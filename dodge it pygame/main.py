import pygame
import time
import random
import os

pygame.init()
pygame.font.init()
pygame.mixer.init()

# --- Screen Setup ---
WIDTH, HEIGHT = 1350, 735
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge It!")

# --- Assets ---
BG = pygame.transform.scale(pygame.image.load("maingame.gif"), (WIDTH, HEIGHT))
GAME_OVER_IMG = pygame.image.load("over.png")
GAME_OVER_BG = pygame.transform.scale(pygame.image.load("gameov.png"), (WIDTH, HEIGHT))
MENU_BG = pygame.transform.scale(pygame.image.load("mainmenu.png"), (WIDTH, HEIGHT))
CONTROL_BG = pygame.transform.scale(pygame.image.load("controlmenu.png"), (WIDTH, HEIGHT))
ARROW_IMG = pygame.transform.scale(pygame.image.load("arrow.png"), (200, 100))
PAUSE_ICON = pygame.transform.scale(pygame.image.load("pause_icon.png"), (150, 100))

# Bird Player Pics
BIRD_IMG_RIGHT = pygame.transform.scale(pygame.image.load("birdright.png"), (150, 100))
BIRD_IMG_LEFT = pygame.transform.flip(BIRD_IMG_RIGHT, True, False)

# Raindrop Projectile
RAINDROP_IMG = pygame.transform.scale(pygame.image.load("raindrop3.png"), (50, 70))

# Shield Power-Up
SHIELD_IMG = pygame.transform.scale(pygame.image.load("shield.png"), (70, 70))
SHIELD_ICON = pygame.transform.scale(pygame.image.load("shield_icon.png"), (70, 70))

# Player and Object Sizes
PLAYER_VEL = 5
STAR_WIDTH = 50
STAR_HEIGHT = 70
STAR_VEL = 5.5

# Fonts
FONT = pygame.font.SysFont("Pixelify Sans", 80)
SMALL_FONT = pygame.font.SysFont("Pixelify Sans", 35)

# Sounds
HIT_SOUND = pygame.mixer.Sound("hit.mp3")
GAMEOVER_SOUND = pygame.mixer.Sound("gameovson.mp3")
SHIELD_SOUND = pygame.mixer.Sound("powerup.mp3") if os.path.exists("powerup.mp3") else None
pygame.mixer.music.load("music.mp3")

# Files for saving data
BEST_TIME_FILE = "best_time.txt"
SAVE_FILE = "savegame.txt"

# --- Helper Functions ---
def get_best_time():
    if os.path.exists(BEST_TIME_FILE):
        with open(BEST_TIME_FILE, "r") as f:
            try:
                return float(f.read().strip())
            except:
                return 0.0
    return 0.0


def save_best_time(new_time):
    with open(BEST_TIME_FILE, "w") as f:
        f.write(str(new_time))


def save_game(elapsed_time):
    with open(SAVE_FILE, "w") as f:
        f.write(str(elapsed_time))


def load_game():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            try:
                return float(f.read().strip())
            except:
                return 0.0
    return 0.0


def delete_save():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)


def format_time(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs}s" if minutes > 0 else f"{secs}s"


def fade_out(surface, duration=600):
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill((0, 0, 0))
    for alpha in range(0, 255, 8):
        fade.set_alpha(alpha)
        surface.blit(fade, (0, 0))
        pygame.display.update()
        pygame.time.delay(duration // 50)


# --- Drawing ---
def draw(player_img, player_rect, elapsed_time, stars, facing_right, shield_active, shield_time_left, shield_rect):
    WIN.blit(BG, (0, 0))
    time_text = FONT.render(f"Time: {format_time(elapsed_time)}", 1, "black")
    WIN.blit(time_text, (10, 10))

    WIN.blit(player_img, (player_rect.x, player_rect.y))

    # Draw raindrops
    for star in stars:
        WIN.blit(RAINDROP_IMG, (star.x, star.y))

    # shield power-up 
    if shield_rect:
        WIN.blit(SHIELD_IMG, (shield_rect.x, shield_rect.y))

    # active shield icon
    if shield_active:
        WIN.blit(SHIELD_ICON, (WIDTH - 90, 120))
        shield_text = SMALL_FONT.render(f"{int(shield_time_left)}s", True, "white")
        WIN.blit(shield_text, (WIDTH - 80, 200))

    # Pause icon
    WIN.blit(PAUSE_ICON, (WIDTH - PAUSE_ICON.get_width() - 15, 10))
    pygame.display.update()


# --- Game Over Screen ---
def game_over_screen(elapsed_time):
    best_time = get_best_time()
    if elapsed_time > best_time:
        best_time = elapsed_time
        save_best_time(best_time)

    fade_out(WIN)
    pygame.mixer.music.stop()
    GAMEOVER_SOUND.play()
    delete_save()

    WIN.blit(GAME_OVER_BG, (0, 0))
    WIN.blit(pygame.transform.scale(GAME_OVER_IMG, (600, 400)),
             (WIDTH / 2 - 300, HEIGHT / 2 - 200))

    best_text = FONT.render(f"High Score: {format_time(best_time)}", True, "black")
    WIN.blit(best_text, (WIDTH / 2 - best_text.get_width() / 2, HEIGHT / 2 + 210))

    restart_text = SMALL_FONT.render("Press R to Restart", True, "black")
    menu_text = SMALL_FONT.render("Press M for Main Menu", True, "black")
    WIN.blit(restart_text, (WIDTH / 2 - restart_text.get_width() / 2, HEIGHT / 2 + 285))
    WIN.blit(menu_text, (WIDTH / 2 - menu_text.get_width() / 2, HEIGHT / 2 + 320))

    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            waiting = False
            GAMEOVER_SOUND.stop()
            main()
        elif keys[pygame.K_m]:
            waiting = False
            main_menu()


# --- Main Game Loop ---
def main(loaded_time=0.0):
    run = True
    pygame.mixer.music.play(-1)

    facing_right = True
    player_img = BIRD_IMG_RIGHT
    player_rect = player_img.get_rect(center=(WIDTH // 2, HEIGHT - 150))
    player_mask = pygame.mask.from_surface(player_img)

    clock = pygame.time.Clock()
    start_time = time.time() - loaded_time
    elapsed_time = loaded_time

    star_add_increment = 2000
    star_count = 0
    stars = []
    paused = False
    pause_start = 0

    # Shield setup
    shield_rect = None
    shield_active = False
    shield_start_time = 0
    SHIELD_DURATION = 5  # seconds

    while run:
        dt = clock.tick(60)
        star_count += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game(elapsed_time)
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                icon_rect = pygame.Rect(WIDTH - PAUSE_ICON.get_width() - 15, 10,
                                        PAUSE_ICON.get_width(), PAUSE_ICON.get_height())
                if icon_rect.collidepoint(mouse_x, mouse_y):
                    paused = not paused
                    if paused:
                        pause_start = time.time()
                    else:
                        start_time += time.time() - pause_start

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                    if paused:
                        pause_start = time.time()
                    else:
                        start_time += time.time() - pause_start
                elif event.key == pygame.K_ESCAPE:  # Save and exit
                    save_game(elapsed_time)
                    main_menu()

        keys = pygame.key.get_pressed()

        if not paused:
            elapsed_time = time.time() - start_time

            # Spawn raindrops
            if star_count > star_add_increment:
                for _ in range(3):
                    star_x = random.randint(0, WIDTH - STAR_WIDTH)
                    star = pygame.Rect(star_x, -STAR_HEIGHT, STAR_WIDTH, STAR_HEIGHT)
                    stars.append(star)

                # Occasionally spawn a shield
                if random.random() < 0.1 and not shield_active and not shield_rect:
                    shield_rect = pygame.Rect(random.randint(50, WIDTH - 100), -80, 70, 70)

                star_add_increment = max(200, star_add_increment - 50)
                star_count = 0

            # Move player
            if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player_rect.left - PLAYER_VEL >= 0:
                player_rect.x -= PLAYER_VEL
                facing_right = False
            if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player_rect.right + PLAYER_VEL <= WIDTH:
                player_rect.x += PLAYER_VEL
                facing_right = True
            if (keys[pygame.K_w] or keys[pygame.K_UP]) and player_rect.top - PLAYER_VEL >= 0:
                player_rect.y -= PLAYER_VEL
            if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player_rect.bottom + PLAYER_VEL <= HEIGHT:
                player_rect.y += PLAYER_VEL

            player_img = BIRD_IMG_RIGHT if facing_right else BIRD_IMG_LEFT
            player_mask = pygame.mask.from_surface(player_img)

            # Move raindrops
            for star in stars[:]:
                star.y += STAR_VEL
                if star.y > HEIGHT:
                    stars.remove(star)
                    continue

                offset_x = star.x - player_rect.x
                offset_y = star.y - player_rect.y

                star_surface = pygame.Surface((STAR_WIDTH, STAR_HEIGHT), pygame.SRCALPHA)
                star_surface.blit(RAINDROP_IMG, (0, 0))
                star_mask = pygame.mask.from_surface(star_surface)

                if player_mask.overlap(star_mask, (offset_x, offset_y)) and not shield_active:
                    HIT_SOUND.play()
                    game_over_screen(elapsed_time)
                    return

            # Move and handle shield
            if shield_rect:
                shield_rect.y += 4
                if shield_rect.y > HEIGHT:
                    shield_rect = None
                elif player_rect.colliderect(shield_rect):
                    shield_active = True
                    shield_start_time = time.time()
                    shield_rect = None
                    if SHIELD_SOUND:
                        SHIELD_SOUND.play()

            # Check shield duration
            if shield_active and time.time() - shield_start_time > SHIELD_DURATION:
                shield_active = False

            draw(player_img, player_rect, elapsed_time, stars, facing_right, shield_active,
                 max(0, SHIELD_DURATION - (time.time() - shield_start_time)) if shield_active else 0, shield_rect)

        else:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(120)
            overlay.fill((0, 0, 0))
            WIN.blit(overlay, (0, 0))
            pause_text = FONT.render("PAUSED", True, "white")
            WIN.blit(pause_text, (WIDTH / 2 - pause_text.get_width() / 2,
                                  HEIGHT / 2 - pause_text.get_height() / 2))
            pygame.display.update()
            clock.tick(15)

    pygame.quit()


# --- Control Menu ---
def control_menu():
    while True:
        WIN.blit(CONTROL_BG, (0, 0))
        WIN.blit(ARROW_IMG, (40, HEIGHT - 120))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                arrow_rect = pygame.Rect(40, HEIGHT - 120, ARROW_IMG.get_width(),
                                         ARROW_IMG.get_height())
                if arrow_rect.collidepoint(mouse_pos):
                    return


# --- Main Menu ---
def main_menu():
    GAMEOVER_SOUND.stop()
    pygame.mixer.music.play(-1)
    best_time = get_best_time()
    controls_rect = pygame.Rect(30, HEIGHT - 130, 250, 100)
    saved_time = load_game()

    while True:
        WIN.blit(MENU_BG, (0, 0))
        best_text = SMALL_FONT.render(f"{format_time(best_time)}", True, "black")
        WIN.blit(best_text, (WIDTH / 2 + 111, HEIGHT / 2 + 256))

        if saved_time > 0:
            continue_text = SMALL_FONT.render("Continue", True, "white")
            WIN.blit(continue_text, (WIDTH / 2 - continue_text.get_width() / 2, HEIGHT / 2 + 170))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if controls_rect.collidepoint(mouse_pos):
                    control_menu()
                else:
                    main()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_q]:
                pygame.quit()
                quit()
            if saved_time > 0 and keys[pygame.K_c]:
                main(saved_time)


if __name__ == "__main__":
    main_menu()
