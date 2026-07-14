import pygame
import random
import sys
import os
import json

pygame.init()

# ==================================================
# BASE DIRECTORY
# ==================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def path(*parts):
    return os.path.join(BASE_DIR, *parts)

# ==================================================
# SOUND
# ==================================================
try:
    pygame.mixer.init()
    slice_sound = pygame.mixer.Sound(path("sounds", "slice.wav"))
    bomb_sound = pygame.mixer.Sound(path("sounds", "bomb.wav"))
except:
    slice_sound = None
    bomb_sound = None

# ==================================================
# SCREEN
# ==================================================
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Ninja INSANE 🔥")

# ==================================================
# IMAGES
# ==================================================
try:
    bg = pygame.transform.scale(
        pygame.image.load(path("images", "background.png")), (980, 650)
    )

    apple = pygame.transform.scale(
        pygame.image.load(path("images", "apple.png")), (100, 100)
    )

    orange = pygame.transform.scale(
        pygame.image.load(path("images", "orange.png")), (100, 100)
    )

    watermelon = pygame.transform.scale(
        pygame.image.load(path("images", "watermelon.png")), (110, 110)
    )

    bomb = pygame.transform.scale(
        pygame.image.load(path("images", "bomb.png")), (80, 80)
    )

    knife = pygame.transform.scale(
        pygame.image.load(path("images", "knife.png")), (90, 90)
    )

except Exception as e:
    print("Image loading error:", e)
    pygame.quit()
    sys.exit()

fruits = [apple, orange, watermelon]

font = pygame.font.SysFont("Arial", 28)
big_font = pygame.font.SysFont("Arial", 60)

# ==================================================
# MULTI USER JSON DB
# ==================================================
DB_FILE = path("userscores.json")

def load_users():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ==================================================
# BUTTON
# ==================================================
class Button:
    def __init__(self, text, x, y, w, h, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color

    def draw(self):
        mouse = pygame.mouse.get_pos()
        c = self.color

        if self.rect.collidepoint(mouse):
            c = (
                min(c[0] + 40, 255),
                min(c[1] + 40, 255),
                min(c[2] + 40, 255),
            )

        pygame.draw.rect(screen, c, self.rect, border_radius=15)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 3, border_radius=15)

        txt = font.render(self.text, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.rect.center))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)

# ==================================================
# FRUIT
# ==================================================
class Fruit:
    def __init__(self, speed_boost
                 _boost):
        self.type = "bomb" if random.random() < 0.2 else "fruit"
        self.image = bomb if self.type == "bomb" else random.choice(fruits)

        self.x = random.randint(50, WIDTH - 100)
        self.y = -100
        self.speed = random.randint(4, 7) + speed_boost

    def move(self):
        self.y += self.speed

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def rect(self):
        return self.image.get_rect(topleft=(self.x, self.y))

# ==================================================
# SLICED HALVES
# ==================================================
class SliceHalf:
    def __init__(self, img, x, y, side):
        w, h = img.get_size()

        if side == "left":
            self.image = img.subsurface((0, 0, w // 2, h)).copy()
            self.vx = -6
        else:
            self.image = img.subsurface((w // 2, 0, w // 2, h)).copy()
            self.vx = 6

        self.x = x
        self.y = y
        self.vy = -8
        self.g = 0.4
        self.angle = 0
        self.rot = random.randint(-12, 12)

    def move(self):
        self.x += self.vx
        self.vy += self.g
        self.y += self.vy
        self.angle += self.rot

    def draw(self):
        img = pygame.transform.rotate(self.image, self.angle)
        screen.blit(img, img.get_rect(center=(self.x, self.y)))

# ==================================================
# PARTICLES
# ==================================================
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-6, -1)
        self.life = 25

    def move(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.4
        self.life -= 1

    def draw(self):
        pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), 3)

# ==================================================
# FLOAT TEXT
# ==================================================
class FloatText:
    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y
        self.life = 40

    def move(self):
        self.y -= 1
        self.life -= 1

    def draw(self):
        txt = font.render(self.text, True, (255, 255, 0))
        screen.blit(txt, (self.x, self.y))

# ==================================================
# RESET
# ==================================================
def reset():
    return [], [], [], [], 0, 3, False

# ==================================================
# VARIABLES
# ==================================================
objects, halves, particles, texts, score, lives, game_over = reset()

users = load_users()
current_user = ""
input_text = ""
high = 0

combo = 0
combo_timer = 0
shake = 0

spawn_delay = 1200
speed_boost = 0
last_level = 0

spawn = pygame.USEREVENT + 1
pygame.time.set_timer(spawn, spawn_delay)

clock = pygame.time.Clock()
prev_mouse = None

state = "login"

start_btn = Button("START", 350, 300, 200, 60, (0, 150, 255))
restart_btn = Button("RESTART", 350, 360, 200, 60, (255, 80, 80))
menu_btn = Button("CHANGE USER", 330, 435, 240, 60, (0, 140, 255))
login_btn = Button("PLAY", 350, 360, 200, 60, (0, 180, 0))


# ==================================================
# GAME LOOP
# ==================================================
while True:

    mouse = pygame.mouse.get_pos()

    offset_x = random.randint(-shake, shake) if shake else 0
    offset_y = random.randint(-shake, shake) if shake else 0

    if shake > 0:
        shake -= 1

    screen.blit(bg, (offset_x, offset_y))

    # ------------------------------------------------
    # EVENTS
    # ------------------------------------------------
    for e in pygame.event.get():

        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # LOGIN
        if state == "login":

            if e.type == pygame.KEYDOWN:

                if e.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]

                elif e.key == pygame.K_RETURN:

                    if input_text.strip() != "":
                        current_user = input_text.strip()

                        if current_user not in users:
                            users[current_user] = 0
                            save_users(users)

                        high = users[current_user]
                        state = "menu"

                else:
                    if len(input_text) < 15:
                        if e.unicode.isprintable():
                            input_text += e.unicode

            if e.type == pygame.MOUSEBUTTONDOWN:
                if login_btn.clicked(mouse):

                    if input_text.strip() != "":
                        current_user = input_text.strip()

                        if current_user not in users:
                            users[current_user] = 0
                            save_users(users)

                        high = users[current_user]
                        state = "menu"

        # MENU
        elif state == "menu":

            if e.type == pygame.MOUSEBUTTONDOWN:
                if start_btn.clicked(mouse):
                    state = "play"

        # PLAY
        elif state == "play":

            if e.type == spawn and not game_over:
                objects.append(Fruit(speed_boost))

            if game_over and e.type == pygame.MOUSEBUTTONDOWN:

                if restart_btn.clicked(mouse):

                    objects, halves, particles, texts, score, lives, game_over = reset()

                    combo = 0
                    speed_boost = 0
                    spawn_delay = 1200
                    last_level = 0

                    pygame.time.set_timer(spawn, spawn_delay)

        elif menu_btn.clicked(mouse):

            objects, halves, particles, texts, score, lives, game_over = reset()

            combo = 0
            speed_boost = 0
            spawn_delay = 1200
            last_level = 0

            input_text = ""
            current_user = ""
            high = 0
            state = "login"

        pygame.time.set_timer(spawn, spawn_delay)

    # ==================================================
    # LOGIN SCREEN
    # ==================================================
    if state == "login":

        screen.blit(big_font.render("ENTER USER ID", True, (255, 255, 255)), (220, 180))

        pygame.draw.rect(screen, (255, 255, 255), (250, 280, 400, 50), 2)

        txt = font.render(input_text, True, (255, 255, 0))
        screen.blit(txt, (270, 292))

        login_btn.draw()

        y = 450
        screen.blit(font.render("Saved IDs:", True, (255,255,255)), (40, y))
        y += 35

        for name in users:
            screen.blit(font.render(name, True, (0,255,255)), (40, y))
            y += 30

        pygame.display.update()
        clock.tick(60)
        continue

    # ==================================================
    # MENU SCREEN
    # ==================================================
    if state == "menu":

        screen.blit(big_font.render("FRUIT NINJA", True, (255,255,255)), (240,200))
        start_btn.draw()

        pygame.display.update()
        clock.tick(60)
        continue

    # ==================================================
    # PLAY GAME
    # ==================================================
    level = score // 10

    if level > last_level:
        last_level = level
        speed_boost = min(5, speed_boost + 0.4)
        spawn_delay = max(250, spawn_delay - 70)
        pygame.time.set_timer(spawn, spawn_delay)

    # OBJECTS
    for obj in objects[:]:
        obj.move()
        obj.draw()

        if obj.y > HEIGHT:
            if obj.type == "fruit":
                lives -= 1
            objects.remove(obj)

    # TRAIL
    if prev_mouse:
        pygame.draw.line(screen, (255,255,255), prev_mouse, mouse, 3)

    # CUTTING
    if pygame.mouse.get_pressed()[0]:

        if prev_mouse:

            for obj in objects[:]:

                if obj.rect().inflate(30,30).clipline(prev_mouse, mouse):

                    if obj.type == "bomb":
                        shake = 20
                        if bomb_sound:
                            bomb_sound.play()
                        game_over = True

                    else:
                        if slice_sound:
                            slice_sound.play()

                        halves.append(SliceHalf(obj.image, obj.x, obj.y, "left"))
                        halves.append(SliceHalf(obj.image, obj.x, obj.y, "right"))

                        for _ in range(12):
                            particles.append(Particle(obj.x, obj.y))

                        combo += 1
                        combo_timer = pygame.time.get_ticks()

                        gain = combo
                        score += gain

                        texts.append(FloatText(f"+{gain}", obj.x, obj.y))

                        if score > high:
                            high = score
                            users[current_user] = high
                            save_users(users)

                    objects.remove(obj)

        prev_mouse = mouse

    else:
        prev_mouse = None

    # combo reset
    if pygame.time.get_ticks() - combo_timer > 800:
        combo = 0

    # HALVES
    for h in halves[:]:
        h.move()
        h.draw()
        if h.y > HEIGHT:
            halves.remove(h)
    # PARTICLES
    for p in particles[:]:
        p.move()
        p.draw()
        if p.life <= 0:
            particles.remove(p)

    # FLOAT TEXT
    for t in texts[:]:
        t.move()
        t.draw()
        if t.life <= 0:
            texts.remove(t)

    # UI
    pygame.draw.rect(screen, (0,0,0), (0,0,WIDTH,90))
    pygame.draw.line(screen, (255,255,255), (0,90), (WIDTH,90), 2)

    screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (20,20))
    screen.blit(font.render(f"Lives: {lives}", True, (255,80,80)), (20,50))
    screen.blit(font.render(current_user, True, (0,255,255)), (390,20))
    screen.blit(font.render(f"High: {high}", True, (255,215,0)), (700,30))

    if combo > 1:
        screen.blit(font.render(f"x{combo}", True, (255,255,0)), (430,50))

    screen.blit(
        pygame.transform.rotate(knife, -45),
        (mouse[0]-45, mouse[1]-45)
    )

    # GAME OVER
    if lives <= 0:
        game_over = True

    if game_over:
        screen.blit(big_font.render("GAME OVER", True, (255,0,0)), (250,200))
        restart_btn.draw()
        menu_btn.draw()

    pygame.display.update()
    clock.tick(60)