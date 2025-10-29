import pgzrun
import math
import random
from pygame import Rect

WIDTH = 960
HEIGHT = 640
TITLE = "Cavaleiro"
GRAVITY = 1
JUMP_STRENGTH = -16
TILE_SIZE = 32
STATE = "MENU"

selected_option = 0
keyboard.up_previous = False
keyboard.down_previous = False
solid_tiles = []
sound_on = True
menu_music_playing = False
slimes = []

knight_image = 'player/animation_idle_0'
knight = Actor(knight_image)
knight.state = 'idle'
knight.pos = 10,500
knight.anchor = ('center', 'bottom')
knight.vy = 0  
knight.on_ground = False
knight.speed = 4
knight.is_facing_right = True
current_frame = 0

coin = Actor('tiles/coin_0')
coin.pos = 30, 220
coin.frame = 0

def load_csv(filename):
    with open(filename) as f:
        lines = f.readlines()
        map = []
        for line in lines:
            row = [int(x.strip()) for x in line.strip().split(',')]
            map.append(row)
        return map

map1_ground = load_csv('map1_ground.csv')
map1_platform = load_csv('map1_platforms.csv')
map1_sky = load_csv('map1_sky.csv')
map1_details = load_csv('map1_details.csv')

def create_tile_rects(map_data):
    tile_rects = []
    for y, line in enumerate(map_data):
        for x, number in enumerate(line):
            if number != -1:
                tile_rects.append(Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    return tile_rects

solid_tiles.extend(create_tile_rects(map1_ground))
solid_tiles.extend(create_tile_rects(map1_platform))

def draw_map1_details(map, tile_size=16):
    for y, line in enumerate(map):
        for x, number in enumerate(line):
            if number == 212:
                screen.blit('tiles/water1', (x * tile_size, y * tile_size))
            elif number == 228:
                screen.blit('tiles/water2', (x * tile_size, y * tile_size))

def draw_map1_ground(map, tile_size=16):
    for y, line in enumerate(map):
        for x, number in enumerate(line):
            if number == 0:
                screen.blit('tiles/ground1', (x * tile_size, y * tile_size))
            elif number == 16:
                screen.blit('tiles/ground2', (x * tile_size, y * tile_size))

def draw_map1_platform(map, tile_size=16):
    for y, line in enumerate(map):
        for x, number in enumerate(line):
            if number == 1:
                screen.blit('tiles/platform1', (x * tile_size, y * tile_size))
            elif number == 2:
                screen.blit('tiles/platform2', (x * tile_size, y * tile_size))
            elif number == 3:
                screen.blit('tiles/platform3', (x * tile_size, y * tile_size))
            elif number == 0:
                screen.blit('tiles/platform1', (x * tile_size, y * tile_size))
            elif number in [198, 216]:
                screen.blit('tiles/platform3', (x * tile_size, y * tile_size))

# Animation frames
knight_idle_images = [f'player/animation_idle_{i}' for i in range(4)]
knight_idle_images_flip = [f'player/animation_idle_flip_{i}' for i in range(4)]
knight_run_images = [f'player/animation_run_{i}' for i in range(16)]
knight_run_images_flip = [f'player/animation_run_flip_{i}' for i in range(16)]
knight_jump_images = ['player/animation_jump_0']
knight_jump_images_flip = ['player/animation_jump_flip_0']
knight_fall_images = ['player/animation_fall_0']
knight_fall_images_flip = ['player/animation_fall_flip_0']
slime_run_images = [f'enemies/slime_run_{i}' for i in range(10)]
slime_run_images_flip = [f'enemies/slime_run_flip_{i}' for i in range(10)]
coin_images = [f'tiles/coin_{i}' for i in range(7)]

def coin_animation():
    current_frame = (coin.frame + 1) % len(coin_images)
    coin.image = coin_images[int(current_frame)]
    coin.frame = current_frame

clock.schedule_interval(coin_animation, 0.1)

def create_slime(x, y):
    new_slime = Actor(slime_run_images[0])
    new_slime.pos = x, y
    new_slime.anchor = ('center', 'bottom')
    new_slime.frame = 0
    new_slime.vx = 2
    return new_slime

def spawn_slimes():
    slimes.append(create_slime(933, 529))
    slimes.append(create_slime(40, 241))

spawn_slimes()

def slime_animation():
    for s in slimes:
        s.frame = (s.frame + 1) % len(slime_run_images)  # Uses the image list, not the current image
        if s.vx > 0:
            s.image = slime_run_images[int(s.frame)]
        else:
            s.image = slime_run_images_flip[int(s.frame)]

clock.schedule_interval(slime_animation, 0.1)
 
def slime_movement():
    for s in slimes:
        s.x += s.vx

        # Screen boundaries
        if s.left < 0 or s.right > WIDTH:
            s.vx = -s.vx
            s.x += s.vx

        # Tile collisions
        for tile in solid_tiles:
            if s.colliderect(tile):
                s.vx = -s.vx
                s.x += s.vx
                break

def update_game():
    global STATE
    
    # Horizontal movement
    knight.vx = 0
    direction = 0
    if keyboard.left or keyboard.a:
        direction = -1
    if keyboard.right or keyboard.d:
        direction = 1

    knight.vx = direction * knight.speed

    knight.x += knight.vx

    if direction != 0:
        knight.is_facing_right = direction > 0

    for tile in solid_tiles:
        if knight.colliderect(tile):
            if knight.vx > 0:
                knight.right = tile.left # Align right side with tile's left side
                knight.vx = 0
            elif knight.vx < 0:
                knight.left = tile.right
                knight.vx = 0

    if direction != 0 and knight.on_ground:
        knight.state = 'run'
    elif direction == 0 and knight.on_ground:
        knight.state = 'idle'
    elif not knight.on_ground and knight.vy >= 0:
        knight.state = 'fall'
    elif not knight.on_ground and knight.vy < 0:
        knight.state = 'jump'

    knight.image = 'player/animation_' + knight.state + ('_flip_' if not knight.is_facing_right else '_') + '0'

    # Vertical movement and gravity
    knight.vy += GRAVITY
    knight.y += knight.vy
    knight.on_ground = False
    
    for tile in solid_tiles:
       if knight.colliderect(tile):
            # If falling (vy > 0) and collided:
            if knight.vy > 0:
                knight.bottom = tile.top # Align bottom with top side
                knight.on_ground = True
                knight.vy = 0

            # If jumping (vy < 0) and collided:
            elif knight.vy < 0:
                knight.top = tile.bottom # Align top with bottom side
                knight.vy = 0 

    if knight.bottom > HEIGHT:
        knight.pos = (10, 500)
        STATE = "MENU"


    # Jump
    if keyboard.space and knight.on_ground:
        knight.vy = JUMP_STRENGTH
        if sound_on:
            sounds.jump.play()

    global current_frame
    
    # Player animation
    animation_lists = {
        'idle': (knight_idle_images, knight_idle_images_flip),
        'run': (knight_run_images, knight_run_images_flip),
        'jump': (knight_jump_images, knight_jump_images_flip),
        'fall': (knight_fall_images, knight_fall_images_flip)
    }

    current_animation = animation_lists[knight.state]
    if knight.is_facing_right:
        frames = current_animation[0]  # Normal animation list
    else:
        frames = current_animation[1]  # Flip animation list

    # Update the current frame (animation speed = 0.2)
    current_frame = (current_frame + 0.2) % len(frames)
    knight.image = frames[int(current_frame)]

    if knight.left < 0:
        knight.left = 0
    if knight.right > WIDTH:
        knight.right = WIDTH

    slime_movement()

    
    if coin and knight.colliderect(coin):
        coin.pos = (-1000, -1000)
        STATE = "VICTORY"
        return

    for s in slimes:
        if knight.colliderect(s):
            knight.pos = (10, 500)
            STATE = "MENU"  

    pass

def draw_menu():
    screen.clear()
    screen.fill((0, 0, 0))
    screen.draw.text("Cavaleiro", center=(WIDTH / 2, HEIGHT / 4), fontsize=60, color="white")
    
    play_color = "yellow" if selected_option == 0 else "white"
    screen.draw.text("Jogar", center=(WIDTH / 2, HEIGHT / 2), fontsize=40, color=play_color)

    quit_color = "yellow" if selected_option == 1 else "white"
    screen.draw.text("Sair", center=(WIDTH / 2, HEIGHT / 2 + 50), fontsize=40, color=quit_color)

    som_color = "yellow" if selected_option == 2 else "white"
    som_text = "Som: Ligado" if sound_on else "Som: Desligado"
    screen.draw.text(som_text, center=(WIDTH / 2, HEIGHT / 2 + 100), fontsize=40, color=som_color)

def draw_game(): 
    screen.fill((3, 38, 89))
    draw_map1_ground(map1_ground, TILE_SIZE)
    draw_map1_platform(map1_platform, TILE_SIZE)
    draw_map1_details(map1_details, TILE_SIZE)
    knight.draw()
    coin.draw()
    for s in slimes:
        s.draw()

    pass

def draw_victory():
    # Victory screen: Menu and Sair
    screen.clear()
    screen.fill((0, 0, 0))
    screen.draw.text("Sucesso!", center=(WIDTH / 2, HEIGHT / 4), fontsize=72, color="white")

    menu_rect = Rect((WIDTH / 2 - 100, HEIGHT / 2), (200, 50))
    quit_rect = Rect((WIDTH / 2 - 100, HEIGHT / 2 + 80), (200, 50))

    play_color = "yellow" if selected_option == 0 else "white"
    screen.draw.text("Menu", center=(WIDTH / 2, HEIGHT / 2), fontsize=40, color=play_color)
    
    quit_color = "yellow" if selected_option == 1 else "white"
    screen.draw.text("Sair", center=(WIDTH / 2, HEIGHT / 2 + 50), fontsize=40, color=quit_color)

def update_victory():
    global STATE, selected_option   

    if (keyboard.up or keyboard.w) and not keyboard.up_previous:
        selected_option = (selected_option - 1) % 3
    if (keyboard.down or keyboard.s) and not keyboard.down_previous:
        selected_option = (selected_option + 1) % 3

    if keyboard.RETURN:
        if selected_option == 0:
            STATE = "MENU"
            knight.pos = (10, 500)
            coin.pos = (30, 220)
        elif selected_option == 1:
            exit()

    if keyboard.escape:
        exit()
        
    # Update previous key states
    keyboard.up_previous = keyboard.up
    keyboard.down_previous = keyboard.down

def update_menu():
    global STATE, selected_option

    if (keyboard.up or keyboard.w) and not keyboard.up_previous:
        selected_option = (selected_option - 1) % 3
    if (keyboard.down or keyboard.s) and not keyboard.down_previous:
        selected_option = (selected_option + 1) % 3

    if keyboard.RETURN:
        if selected_option == 0: # Jogar
            STATE = "PLAYING"
        elif selected_option == 1:  # Sair
            exit()
        if selected_option == 2:
            # Toggle sound on/off
            global sound_on
            sound_on = not sound_on
            if sound_on:
                music.play('time_for_adventure')
            else:
                music.stop()
                sounds.jump.stop()

    if keyboard.escape:
        exit()
        
    # Update previous key states
    keyboard.up_previous = keyboard.up
    keyboard.down_previous = keyboard.down

def draw():
    global menu_music_playing
    if STATE == "MENU":
        # Manage menu music without restarting it every frame
        if sound_on and not menu_music_playing:
            music.play('time_for_adventure')
            menu_music_playing = True
        if not sound_on and menu_music_playing:
            music.stop()
            menu_music_playing = False
        draw_menu()
    elif STATE == "PLAYING":
        draw_game()
    elif STATE == "VICTORY":
        if menu_music_playing:
            music.stop()
            menu_music_playing = False
        draw_victory()

def update():
    if STATE == "MENU":
        update_menu()
    elif STATE == "PLAYING":
        update_game()
    elif STATE == "VICTORY":
        update_victory()


pgzrun.go()