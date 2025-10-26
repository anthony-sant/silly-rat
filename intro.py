import pgzrun
import pygame
import random
import math

TILE_SIZE = 16
WIDTH = 640
HEIGHT = 384
MAP_WIDTH = WIDTH // TILE_SIZE
MAP_HEIGHT = HEIGHT // TILE_SIZE

MAX_HP = 100

game_state = "playing"
current_level = 1
last_door_x_position = 0
door_open = False
number_trees = 1



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
    BL: "tiles/tile_0153",
    TR: "tiles/tile_0170",
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

FLOOR = {
    GRASS: "tiles/tile_0024",
    STONE: "tiles/tile_0119"
}

LEFT = "LEFT"
RIGHT = "RIGHT"
LDL = "LYING_DOWN_LEFT"
LDR = "LYING_DOWN_RIGHT"

PLAYER_SPRITES = {
    "left": {
        "idle": ["tile_player/idle_left"],
        "walk": ["tile_player/idle_left", "tile_player/walk_left"],
        "lying": ["tile_player/lying_down_left"]
    },
    "right": {
        "idle": ["tile_player/idle_right"],
        "walk": ["tile_player/idle_right", "tile_player/walk_right"],
        "lying": ["tile_player/lying_down_right"]
    }
}
BLOCKED_TILES = list(WALL_ROCK.values()) + [TREE[B]]
class Player:
    hp_max = 100
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, TILE_SIZE, TILE_SIZE)
        #self.rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        #self.rect.centerx = WIDTH // 2
        #self.rect.centery = HEIGHT //2
        self.speed = TILE_SIZE / 7
        self.direction = None
        self.facing_direction = "left"
        self.current_frame = 0
        self.frame_counter = 0
        self.animation_speed = 10
        self.state = "idle"
        self.image = PLAYER_SPRITES[self.facing_direction][self.state][self.current_frame]
        self.step_timer = 0

    def move(self, map_):

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

        if map_[tile_y][tile_x] in FLOOR.values():
            self.rect = new_rect

    def update_direction(self):
        if keyboard.w:
            self.direction = "up"
            self.state = "walk"
        elif keyboard.s:
            self.direction = "down"
            self.state = "walk"
        elif keyboard.a:
            self.direction = "left"
            self.facing_direction = self.direction
            self.state = "walk"
        elif keyboard.d:
            self.direction = "right"
            self.facing_direction = self.direction
            self.state = "walk"
        else:
            self.direction = None
            self.state = "idle"

    def update_sprite(self):
        self.frame_counter += 1
        if self.frame_counter >= self.animation_speed:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % len(PLAYER_SPRITES[self.facing_direction][self.state])
            self.image = PLAYER_SPRITES[self.facing_direction][self.state][self.current_frame]

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))




        
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
        if map_[tree_y][tree_x] in FLOOR.values():
            map_[tree_y][tree_x] = "TREE"
            wood_position = tree_y + 1
            map_[wood_position][tree_x] = "WOOD"
            placed = True

def generate_map1():
    map1 = [[None for _ in range(WIDTH // TILE_SIZE)] for _ in range(HEIGHT // TILE_SIZE)]
    generate_floor(map1, GRASS)
    build_wall(map1)
    number_trees = random.randint(10, 15)
    door_x = random.randint(1, (WIDTH // TILE_SIZE) - 2)
    door_y = 2

    door_position = (door_x, door_y)

    for _ in range(20):
        generate_tree(map1)

    return map1, door_position

current_map, door_position = generate_map1()



def draw_floor(floor_key):
    for y, line in enumerate(current_map):
        for x, _ in enumerate(line):
            screen.blit(FLOOR[floor_key], (x * TILE_SIZE, y * TILE_SIZE))

def draw_wall():
    for y, line in enumerate(current_map):
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
    for y, line in enumerate(current_map):
        for x, name in enumerate(line):
            if name == "TREE":
                for key, tile_name in TREE.items():
                    offset = TREE_OFFSETS[key]
                    xt = x + offset[0]
                    yt = y + offset[1]

                    screen.blit(tile_name, (xt * TILE_SIZE, yt * TILE_SIZE))


def play_walk_sound(player):
    if player.state == "walk":
        player.step_timer += 1
        if player.step_timer >= 10:  # número de frames entre passos
            sounds.step.play()
            player.step_timer = 0
    else:
        player.step_timer = 0

player = Player()

def update():
    player.update_direction()
    player.move(current_map)
    player.update_sprite()
    play_walk_sound(player)


def draw():
    screen.clear()
    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        if current_level == 1:
            
            draw_floor(GRASS)
            draw_wall()
            draw_door()
            player.draw()
            draw_trees()
    

pgzrun.go()