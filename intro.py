import pgzrun
from pygame import Rect
import random
import math
from abc import ABC, abstractmethod
from pgzero import music

TILE_SIZE = 16
WIDTH = 640
HEIGHT = 384
MAP_WIDTH = WIDTH // TILE_SIZE
MAP_HEIGHT = HEIGHT // TILE_SIZE
TITLE = "Silly Rat"
FONT_TITLE = "pixelfont"
FONT_MENU = "pixelfont"

MAX_HP = 100

game_state = "menu"
options = ["Start Game", "Toggle Sound", "Exit"]
selected_option = 0
current_level = 1
map1 = []
door_position = (0,0)
door_open = False
number_trees = 1
enemies = []
player = None
sound = None
menu_image = Actor("menu_rat")
menu_image.x = WIDTH // 2  # centraliza horizontalmente
CURRENT_MAP = {
    1: map1
}

OBJECTS = {
    "KEY": "tiles/tile_0198"
}
PLET = "PLET"
PMT = "PMT"
PLDT = "PLDT"
PLES = "PLES"
PMS = "PMS"
PLDS = "PLDS"
PLEM = "PLEM"
PM = "PM"
PLDM = "PLDM"
PLEI = "PLEI"
PMI = "PMI"
PLDI = "PLDI"

WALL_ROCK = {
    PLET: "tiles/tile_0015",
    PMT:  "tiles/tile_0016",
    PLDT: "tiles/tile_0017",

    PLES: "tiles/tile_0051",
    PMS:  "tiles/tile_0052",
    PLDS: "tiles/tile_0053",

    PLEM: "tiles/tile_0069",
    PM:   "tiles/tile_0070",
    PLDM: "tiles/tile_0071",

    PLEI: "tiles/tile_0087",
    PMI:  "tiles/tile_0088",
    PLDI: "tiles/tile_0089"
}
WALL_PATTERN = {
    0: (PLET, PMT, PLDT),
    1: (PLES, PMS, PLDS),
    2: (PLEM, PM, PLDM),
    3: (PLEI, PMI, PLDI)

}


T = "T"
B = "B"

TREE = {
    T: "tiles/tile_0062",
    B: "tiles/tile_0080"
}

TREE_OFFSETS = {
    T: (0, 0),
    B: (0, 1)
}

TL = "TL"
BL = "BL"
TR = "TR"
BR = "BR"

DOOR_CLOSED = {
    TL: "tiles/tile_0188",
    BL: "tiles/tile_0206",
    TR: "tiles/tile_0189",
    BR: "tiles/tile_0207"
}

DOOR_OPEN = {
    TL: "tiles/tile_0152",
    BL: "tiles/tile_0170",
    TR: "tiles/tile_0153",
    BR: "tiles/tile_0171"
}

DOOR_OFFSETS = {
    TL: (0,0),
    BL: (0,1),
    TR: (1,0),
    BR: (1,1)
}

GRASS = "GRASS"
STONE = "STONE"
GRASS_WIN = "GRASS_WIN"
STONE_WIN = "STONE_WIN"

WIN_POINT = {
    GRASS_WIN: "tiles/tile_0088",
    STONE_WIN: "tiles/tile_0088"
}

FLOOR = {
    GRASS: "tiles/tile_0024",
    STONE: "tiles/tile_0119"
}


PLAYER_SPRITES = {
    "left": {
        "idle": ["tile_player/idle_left", "tile_player/idle2_left"],
        "walk": ["tile_player/idle_left", "tile_player/walk_left"],
        "lying": ["tile_player/lying_down_left"]
    },
    "right": {
        "idle": ["tile_player/idle_right", "tile_player/idle2_right"],
        "walk": ["tile_player/idle_right", "tile_player/walk_right"],
        "lying": ["tile_player/lying_down_right"]
    }
}

WORM_SPRITES = {
    "left": {
        "idle": ["tile_enemies/worm_idle_left"],
        "walk": ["tile_enemies/worm_idle_left", "tile_enemies/worm_walk_left"],
        "lying": ["tile_enemies/worm_lying_down_left"]
    },
    "right": {
        "idle": ["tile_enemies/worm_idle_right"],
        "walk": ["tile_enemies/worm_idle_right", "tile_enemies/worm_walk_right"],
        "lying": ["tile_enemies/worm_lying_down_right"]
    }
}

BLOCKED_TILES = list(WALL_ROCK.values()) + [TREE[B]]

class SoundManager:
    def __init__(self):
        self.sound_on = True

    def player_damage_sound(self):
        if self.sound_on:
            sounds.player_damage.play()


    def play_walk_sound(self, player):
        if self.sound_on:
            if player.state == "walk":
                player.step_timer += 1
                if player.step_timer >= 10:
                    sounds.step.play()
                    player.step_timer = 0
            else:
                player.step_timer = 0

    def play_music(self):
        if self.sound_on:
            music.play("silly_rat_music")

    def pick_a_key_sound(self):
        if self.sound_on:
            sounds.pick_key.play()

    def sound_door_open(self):
        if self.sound_on:
            sounds.door_open.play()

    def win_sound(self):
        if self.sound_on:
            sounds.win_sound.play()

class Entity(ABC):
    def __init__(self, x, y, speed):
        self.rect = Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.speed = TILE_SIZE / speed
        self.direction = None
        self.facing_direction = "left"
        self.current_frame = 0
        self.frame_counter = 0
        self.animation_speed = 10
        self.state = "idle"
        self.image = None
        self.step_timer = 0
        self.hp = MAX_HP
        self.damage = 25
        self.attack_cooldown = 60
        self.attack_timer = 0

    @abstractmethod
    def update(self, map_, entity):
        pass

    def atack(self, entity):
        if hasattr(entity, "take_damage"):
            entity.take_damage(self.damage)

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        sound.player_damage_sound()
        print(f"{self.__class__.__name__} levou {amount} de dano. HP restante: {self.hp}")

    def update_sprite(self, sprites):
        self.frame_counter += 1
        if self.frame_counter >= self.animation_speed:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % len(sprites[self.facing_direction][self.state])
            self.image = sprites[self.facing_direction][self.state][self.current_frame]

        
    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))


    def is_dead(self):
        return self.hp<=0

class Worm(Entity):
    def __init__(self, x, y, speed):
        super().__init__(x,y, speed)
        self.image = WORM_SPRITES[self.facing_direction][self.state][self.current_frame]
        self.direction = random.choice(["up", "down", "left", "right"])
        self.move_cooldown = 80
        self.timer = 0

    def update(self, map_, entity):
        self.random_walk(map_, player)
        self.move(map_)
        self.update_sprite(WORM_SPRITES)


        

    def update_direction(self):
        current_direction = random.choice(["up", "down", "left", "right"])
        self.direction = current_direction
        if current_direction == "right" or current_direction == "left":
            self.facing_direction = current_direction

        self.state = "walk" if self.direction else "idle"

    def move(self, map_, target=None):
        new_rect = self.rect.copy()

        # Movimento como antes (igual ao seu código anterior)
        if self.direction == "up":
            new_rect.y -= self.speed
        elif self.direction == "down":
            new_rect.y += self.speed
        elif self.direction == "left":
            new_rect.x -= self.speed
        elif self.direction == "right":
            new_rect.x += self.speed

        # Mantém dentro dos limites do mesmo jeito que você usava (preserva comportamento)
        new_rect.x = max(0, min(new_rect.x, WIDTH - (1.5 * TILE_SIZE)))
        new_rect.y = max(0, min(new_rect.y, HEIGHT - (1.5 * TILE_SIZE)))

        # Tile em que o "pé" está (igual ao seu original)
        tile_x = new_rect.centerx // TILE_SIZE
        tile_y = new_rect.bottom // TILE_SIZE

        # Proteção contra IndexError — se sair dos limites, não move
        if not (0 <= tile_y < len(map_) and 0 <= tile_x < len(map_[0])):
            return

        # Pare quando houver parede (igual ao seu original)
        if map_[tile_y][tile_x] not in FLOOR.values():
            self.update_direction()
            return  # parede, não move

        # Ataque por colisão — mantém comportamento de "não atravessar o player"
        if target and new_rect.colliderect(target.rect):
            # se quiser o comportamento antigo (parar ao colidir), mantemos o return
            if self.attack_timer <= 0:
                self.atack(target)
                self.attack_timer = self.attack_cooldown
            return  # colidiu com o player, não anda (igual ao seu original)

        # finalmente aplica a nova posição
        self.rect = new_rect

        # decrementa cooldown (se houver)
        if self.attack_timer > 0:
            self.attack_timer -= 1
    def random_walk(self, map_, player):
        if self.timer > 0:
            self.timer -= 1
        else:
            self.update_direction()
            self.timer = self.move_cooldown

        if self.attack_timer > 0:
            self.attack_timer -= 1

        self.state = "walk"
        self.move(map_)

        if self.rect.colliderect(player.rect) and self.attack_timer == 0:
            self.atack(player)
            self.attack_timer = self.attack_cooldown

    def flip_direction(self, direction):
        if direction == "up":
            return "down"
        elif direction == "down":
            return "up"
        elif direction == "left":
            self.facing_direction = "right"
            return "right"
        elif direction == "right":
            self.facing_direction = "left"
            return "left"
        return direction


    

class Player(Entity):
    def __init__(self, x, y, speed):
        super().__init__(x, y, speed)
        self.image = PLAYER_SPRITES[self.facing_direction][self.state][self.current_frame]
        self.speed = TILE_SIZE / 10
        self.key_counter = 0

    def update(self, map_, entity):
        global game_state
        self.update_direction()
        self.move(map_)
        self.update_sprite(PLAYER_SPRITES)
        if self.is_dead():
            game_state = "game_over"

    

    def update_direction(self):
        if keyboard.w:
            self.direction = "up"
        elif keyboard.s:
            self.direction = "down"
        elif keyboard.a:
            self.direction = "left"
            self.facing_direction = self.direction
        elif keyboard.d:
            self.direction = "right"
            self.facing_direction = self.direction
        else:
            self.direction = None

        self.state = "walk" if self.direction else "idle"

    def move(self, map_):
        global game_state
        new_rect = self.rect.copy()
        if self.direction == "up":
            new_rect.y -= self.speed
        elif self.direction == "down":
            new_rect.y += self.speed
        elif self.direction == "left":
            new_rect.x -= self.speed
        elif self.direction == "right":
            new_rect.x += self.speed

        new_rect.x = max(0, min(new_rect.x, WIDTH - (1.5* TILE_SIZE)))
        new_rect.y = max(0, min(new_rect.y, HEIGHT - (1.5* TILE_SIZE)))


        tile_x = new_rect.centerx// TILE_SIZE
        tile_y = new_rect.bottom // TILE_SIZE

        if not (0 <= tile_y < len(map_) and 0 <= tile_x < len(map_[0])):
            return

        current_tile = map_[tile_y][tile_x]
        if current_tile not in FLOOR.values():
            
            print(f"Tile atual: '{current_tile}'")  # debug
            if current_tile in "KEY":
                self.pick_key()
                map_[tile_y][tile_x] = FLOOR[GRASS]
            elif current_tile in "GRASS_WIN":
                print("Detectou GRASS_WIN")  # debug
                if door_open:
                    print("You Win!")
                    sound.win_sound()
                    game_state = "win_menu"
            else:
                return  # parede, não move

   
        for enemy in enemies:
            if new_rect.colliderect(enemy.rect):
                return 
        
        
        self.rect = new_rect

    def pick_key(self):
        sound.pick_a_key_sound()
        self.key_counter += 1

    
    

def get_random_floor_position(map_):
    while True:
        x = random.randint(0, MAP_WIDTH - 1)
        y = random.randint(0, MAP_HEIGHT - 1)
        if map_[y][x] in FLOOR.values():
                return x * TILE_SIZE, y*TILE_SIZE


def draw_menu():
    global game_state, selected_option
    screen.fill((10, 10, 20))

    menu_image.draw()

    screen.draw.text(
        TITLE,
        center=(WIDTH // 2, HEIGHT // 2 - 40),
        fontsize=32,
        color="white",
        fontname=FONT_TITLE,
        owidth=1, ocolor="black"
    )

    for i, option in enumerate(options):
        color = "yellow" if i == selected_option else "white"
        screen.draw.text(
            option,
            center=(WIDTH // 2, HEIGHT //2 + 20+ i * 35),
            fontsize=16,
            color=color,
            fontname=FONT_MENU,
            owidth=2, ocolor="black"
        )

    screen.draw.text(
        "Use Up/Down to navigate and Enter to select",
        center=(WIDTH // 2, HEIGHT - 40),
        fontsize=10,
        color="white",
        fontname=FONT_MENU,
    )

def is_near_door(pos_x, pos_y, door_x, door_y, threshold=0.5):
    return abs(pos_x - door_x) <= threshold and abs(pos_y - door_y) <= threshold

def build_wall(map_):
    for y in range(4):
        left, middle, right = WALL_PATTERN[y]
        for x in range(WIDTH // TILE_SIZE):
            if x == 0:
                map_[y][x] = left
            elif x == (WIDTH // TILE_SIZE) - 1:
                map_[y][x] = right
            else:
                map_[y][x] = middle


def generate_floor(map_, floor_key):
    for y, line in enumerate(map_):
        for x, name in enumerate(line):
            map_[y][x] = FLOOR[floor_key]

                

def generate_tree(map_):
    placed = False
    while not placed:
        tree_x = random.randint(0, (WIDTH // TILE_SIZE)-1)
        tree_y = random.randint(0, (HEIGHT // TILE_SIZE) - 2)
        if map_[tree_y][tree_x] in FLOOR.values() and (WIDTH // 2, HEIGHT // 2) != (tree_x * TILE_SIZE, tree_y * TILE_SIZE):
            map_[tree_y][tree_x] = "TREE"
            wood_position = tree_y + 1
            map_[wood_position][tree_x] = "WOOD"
            placed = True

def generate_key(map_):
    placed = False
    while not placed:
        key_x = random.randint(0, (WIDTH // TILE_SIZE)-1)
        key_y = random.randint(0, (HEIGHT // TILE_SIZE) - 2)
        if map_[key_y][key_x] in FLOOR.values():
            map_[key_y][key_x] = "KEY"
            placed = True

def generate_map1():
    global door_position, map1
    map1 = [[None for _ in range(WIDTH // TILE_SIZE)] for _ in range(HEIGHT // TILE_SIZE)]
    generate_floor(map1, GRASS)
    door_x = random.randint(1, (WIDTH // TILE_SIZE) - 3)
    door_y = 2

    map1[door_y+2][door_x] = "WIN"
    map1[door_y+2][door_x+2] = "WIN"
    door_position = (door_x, door_y)
    build_wall(map1)


    for _ in range(25):
        generate_tree(map1)

    for _ in range(30):
        x, y = get_random_floor_position(map1)
        enemies.append(Worm(x, y, 15))

    for _ in range(3):
        generate_key(map1)
    return map1





def draw_floor(floor_key):
    for y, line in enumerate(CURRENT_MAP[current_level]):
        for x, _ in enumerate(line):
            screen.blit(FLOOR[floor_key], (x * TILE_SIZE, y * TILE_SIZE))

def draw_wall():
    for y, line in enumerate(CURRENT_MAP[current_level]):
        for x, name in enumerate(line):
            if name in WALL_ROCK:
                screen.blit(WALL_ROCK[name], (x*TILE_SIZE, y*TILE_SIZE))

def draw_door():
    if door_open:
        door_tiles = DOOR_OPEN
    else:
        door_tiles = DOOR_CLOSED

    for key, tile_name in door_tiles.items():
        offset = DOOR_OFFSETS[key]
        x = door_position[0] + offset[0]
        y = door_position[1] + offset[1]

        screen.blit(tile_name, (x * TILE_SIZE, y * TILE_SIZE))

def draw_trees():
    for y, line in enumerate(CURRENT_MAP[current_level]):
        for x, name in enumerate(line):
            if name == "TREE":
                for key, tile_name in TREE.items():
                    offset = TREE_OFFSETS[key]
                    xt = x + offset[0]
                    yt = y + offset[1]

                    screen.blit(tile_name, (xt * TILE_SIZE, yt * TILE_SIZE))

def draw_key():
    for y, line in enumerate(CURRENT_MAP[current_level]):
        for x, name in enumerate(line):
            if name == "KEY":
                screen.blit("tiles/tile_0198", (x * TILE_SIZE, y * TILE_SIZE))


def draw_win_menu():
    screen.fill((0, 0, 0))
    screen.draw.text(
        "You Win!",
        center=(WIDTH // 2, HEIGHT // 2 - 20),
        fontsize=48,
        color="white",
        fontname=FONT_TITLE,
        owidth=2, ocolor="black"
    )
    screen.draw.text(
        "Press Enter to return to Menu",
        center=(WIDTH // 2, HEIGHT // 2 + 40),
        fontsize=16,
        color="white",
        fontname=FONT_MENU,
        owidth=1, ocolor="black"
    )


def draw_game_over():
    screen.fill((0, 0, 0))
    screen.draw.text(
        "Game Over!",
        center=(WIDTH // 2, HEIGHT // 2 - 20),
        fontsize=48,
        color="white",
        fontname=FONT_TITLE,
        owidth=2, ocolor="black"
    )
    screen.draw.text(
        "Press Enter to return to Menu",
        center=(WIDTH // 2, HEIGHT // 2 + 40),
        fontsize=16,
        color="white",
        fontname=FONT_MENU,
        owidth=1, ocolor="black"
    )

def init():
    global player, map1, CURRENT_MAP, current_level, sound, enemies, door_open
    door_open = False
    enemies = []
    map1 = generate_map1()
    CURRENT_MAP = {1: map1}
    current_level = 1
    if sound is None:
        sound = SoundManager()
    player = Player(WIDTH // 2, HEIGHT // 2, 10)
    sound.play_music()
    

def update_game():
    global door_open
    if not player or not CURRENT_MAP or current_level not in CURRENT_MAP:
        return
    player.update(CURRENT_MAP[current_level], player)
    sound.play_walk_sound(player)
    
    for enemy in enemies:
        enemy.update(CURRENT_MAP[current_level], player)
        if enemy.is_dead():
            enemies.remove(enemy)

    if player.key_counter >= 3 and not door_open:
        sound.sound_door_open()
        door_open = True
    


def on_key_down(key):
    global selected_option, game_state, sound_on, sound

    if game_state == "menu":
        # navegação ↑ ↓
        if key == keys.UP:
            selected_option = (selected_option - 1) % len(options)
        elif key == keys.DOWN:
            selected_option = (selected_option + 1) % len(options)

        # confirmação
        elif key == keys.RETURN:
            option = options[selected_option]
            if option == "Start Game":
                init()
                game_state = "playing"
            elif option == "Toggle Sound":
                if sound is None:
                    sound = SoundManager()
                    sound.sound_on = False
                    music.stop()
                else:
                    sound.sound_on = not sound.sound_on
                    if not sound.sound_on:
                        music.stop()
                print("Sound:", "ON" if sound.sound_on else "OFF")
            elif option == "Exit":
                exit()
    elif game_state == "win_menu" or game_state == "game_over":
        if key == keys.RETURN:
            game_state = "menu"

def update():
    if game_state == "playing":
        update_game()

    elif game_state == "win_menu" or game_state == "game_over":
        if sound:
            music.stop()

    


def draw():
    screen.clear()
    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        if current_level == 1:
            
            draw_floor(GRASS)
            draw_wall()
            draw_door()
            for enemy in enemies:
                enemy.draw()
            player.draw()
            draw_trees()
            draw_key()
    elif game_state == "win_menu":
        draw_win_menu()

    elif game_state == "game_over":
        draw_game_over()
pgzrun.go()