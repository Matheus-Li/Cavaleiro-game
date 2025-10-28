import pgzrun
import math
import random
from pygame import Rect

WIDTH = 960  # Era 480
HEIGHT = 640 # Era 320
TITLE = "Cavaleiro"
GRAVITY = 1 # Era 0.6
JUMP_STRENGTH = -16 # Era -16
TILE_SIZE = 32 # Era 16
STATE = "MENU"
selected_option = 0  # 0 = Play, 1 = Quit
keyboard.up_previous = False
keyboard.down_previous = False
solid_tiles = []
slimes = []
# Sound/menu music control
sound_on = True
menu_music_playing = False
  # Posição inicial do slime

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
            if number == 212:  # Números 0
                screen.blit('tiles/water1', (x * tile_size, y * tile_size))
            elif number == 228:  # Números 16
                screen.blit('tiles/water2', (x * tile_size, y * tile_size))

def draw_map1_ground(map, tile_size=16):
    for y, line in enumerate(map):
        for x, number in enumerate(line):
            if number == 0:  # Números 0
                screen.blit('tiles/ground1', (x * tile_size, y * tile_size))
            elif number == 16:  # Números 16
                screen.blit('tiles/ground2', (x * tile_size, y * tile_size))

def draw_map1_platform(map, tile_size=16):
    for y, line in enumerate(map):
        for x, number in enumerate(line):
            if number == 1:
                screen.blit('tiles/platform1', (x * tile_size, y * tile_size))
            elif number == 2:
                screen.blit('tiles/platform2', (x * tile_size, y * tile_size))
            elif number == 3:  # Adicionar platform3
                screen.blit('tiles/platform3', (x * tile_size, y * tile_size))
            elif number == 0:  # Usar platform1 para números 0
                screen.blit('tiles/platform1', (x * tile_size, y * tile_size))
            elif number in [198, 216]:  # Usar platform3 para números especiais
                screen.blit('tiles/platform3', (x * tile_size, y * tile_size))

# Animation frames lists using exact file names that exist
knight_idle_images = [f'player/animation_idle_{i}' for i in range(4)]
knight_idle_images_flip = [f'player/animation_idle_flip_{i}' for i in range(4)]
knight_run_images = [f'player/animation_run_{i}' for i in range(16)]
knight_run_images_flip = [f'player/animation_run_flip_{i}' for i in range(16)]
knight_jump_images = ['player/animation_jump_0']  # Single frame
knight_jump_images_flip = ['player/animation_jump_flip_0']  # Single frame
knight_fall_images = ['player/animation_fall_0']  # Single frame
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
    # use the first frame as the initial image (Actor expects a string, not a list)
    new_slime = Actor(slime_run_images[0])
    new_slime.pos = x, y
    new_slime.anchor = ('center', 'bottom')
    new_slime.frame = 0
    new_slime.vx = 2
    return new_slime

def spawn_slimes():
    slimes.append(create_slime(933, 529))
    slimes.append(create_slime(40, 241))

# spawn initial slimes once
spawn_slimes()

def slime_animation():
    for s in slimes:
        s.frame = (s.frame + 1) % len(slime_run_images)  # Usa a lista de imagens, não a imagem atual
        if s.vx > 0:
            s.image = slime_run_images[int(s.frame)]
        else:
            s.image = slime_run_images_flip[int(s.frame)]

clock.schedule_interval(slime_animation, 0.1)
 
def slime_movement():
    for s in slimes:
        # Atualiza posição horizontal para este slime
        s.x += s.vx

        # Verifica limites da tela para ESTE slime
        if s.left < 0 or s.right > WIDTH:
            s.vx = -s.vx
            s.x += s.vx  # empurra um passo para fora da borda para evitar "grudar"

        # Verifica colisões com tiles para ESTE slime
        for tile in solid_tiles:
            if s.colliderect(tile):
                s.vx = -s.vx
                s.x += s.vx  # empurra para fora do tile
                break  # só trata a primeira colisão relevante

def update_game():
    global STATE
    # --- Movimento Horizontal (Eixo X) ---
    
    # 1. Define a velocidade horizontal com base no input
    knight.vx = 0
    direction = 0
    if keyboard.left or keyboard.a: # Era -3
        direction = -1
    if keyboard.right or keyboard.d:  # Era 3
        direction = 1

    knight.vx = direction * knight.speed

    knight.x += knight.vx

    if direction != 0:
        knight.is_facing_right = direction > 0

    for tile in solid_tiles:
        if knight.colliderect(tile):
            if knight.vx > 0:
                knight.right = tile.left # ...alinhamos sua direita com a esquerda do tile
                knight.vx = 0
            elif knight.vx < 0:  # Para a velocidade de queda
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

    # --- Movimento Vertical (Eixo Y) ---

    # 4. Aplica a gravidade
    knight.vy += GRAVITY # Ajusta a gravidade para ser independente do frame rate
    
    # 5. Move o personagem no eixo Y
    knight.y += knight.vy

    # 6. Checa colisões APENAS no eixo Y
    knight.on_ground = False # Assume que está no ar até provar o contrário
    
    for tile in solid_tiles:
       if knight.colliderect(tile):
            # Se estava caindo (vy > 0) e colidiu...
            if knight.vy > 0:
                knight.bottom = tile.top # ...alinhamos sua base com o topo do tile
                knight.on_ground = True # Marca que está no chão
                knight.vy = 0 # Para a velocidade de queda
            
            # Se estava subindo (pulando) e colidiu...
            elif knight.vy < 0:
                knight.top = tile.bottom # ...alinhamos seu topo com a base do tile (bateu a cabeça)
                knight.vy = 0 # Para a velocidade de subida

    if knight.bottom > HEIGHT:
        knight.pos = (10, 500)
        STATE = "MENU"


    # --- Lógica do Pulo ---
    if keyboard.space and knight.on_ground:
        knight.vy = JUMP_STRENGTH
        if sound_on:  # Só toca o som se o som estiver ligado
            sounds.jump.play()

    global current_frame
    
    # 1. Seleciona a lista de animação correta baseada no estado
    animation_lists = {
        'idle': (knight_idle_images, knight_idle_images_flip),
        'run': (knight_run_images, knight_run_images_flip),
        'jump': (knight_jump_images, knight_jump_images_flip),
        'fall': (knight_fall_images, knight_fall_images_flip)
    }

    # 2. Pega a lista correta baseada na direção
    current_animation = animation_lists[knight.state]
    if knight.is_facing_right:
        frames = current_animation[0]  # lista normal
    else:
        frames = current_animation[1]  # lista flip

    # 3. Atualiza o frame atual (velocidade da animação = 0.2)
    current_frame = (current_frame + 0.2) % len(frames)
    
    # 4. Aplica o frame atual à imagem do knight
    knight.image = frames[int(current_frame)]

    if knight.left < 0:
        knight.left = 0
    if knight.right > WIDTH:
        knight.right = WIDTH

    slime_movement()

    # Checa colisão do jogador com a moeda -> tela de vitória
    if coin and knight.colliderect(coin):
        # remove a moeda da cena (opcional) e vai para tela de vitória
        coin.pos = (-1000, -1000)
        STATE = "VICTORY"
        return

    for s in slimes:
        if knight.colliderect(s):
            knight.pos = (10, 500)
            STATE = "MENU"  

    pass

    #print(direction)
    #print(knight.state)
    #print(knight.on_ground)
    #print(knight.on_ground)
    #print(knight.pos)

def draw_colliders():
        # Desenha um contorno vermelho em volta de cada tile sólido
    for tile in solid_tiles:
        screen.draw.rect(tile, 'red')

def draw_menu():
    screen.clear()
    screen.fill((0, 0, 0))  # Optional background
    screen.draw.text("Cavaleiro", center=(WIDTH / 2, HEIGHT / 4), fontsize=60, color="white")
    
    # Draw Play option
    play_color = "yellow" if selected_option == 0 else "white"
    screen.draw.text("Jogar", center=(WIDTH / 2, HEIGHT / 2), fontsize=40, color=play_color)

    # Draw Quit option
    quit_color = "yellow" if selected_option == 1 else "white"
    screen.draw.text("Sair", center=(WIDTH / 2, HEIGHT / 2 + 50), fontsize=40, color=quit_color)

    som_color = "yellow" if selected_option == 2 else "white"
    som_text = "Som: On" if sound_on else "Som: Off"
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
    #draw_colliders()
    pass

def draw_victory():
    # Simple victory screen with two buttons: Menu and Quit
    screen.clear()
    screen.fill((0, 0, 0))
    screen.draw.text("Sucesso!", center=(WIDTH / 2, HEIGHT / 4), fontsize=72, color="white")

    menu_rect = Rect((WIDTH / 2 - 100, HEIGHT / 2), (200, 50))
    quit_rect = Rect((WIDTH / 2 - 100, HEIGHT / 2 + 80), (200, 50))

    # Draw buttons
    play_color = "yellow" if selected_option == 0 else "white"
    screen.draw.text("Menu", center=(WIDTH / 2, HEIGHT / 2), fontsize=40, color=play_color)
    
    # Draw Quit option
    quit_color = "yellow" if selected_option == 1 else "white"
    screen.draw.text("Sair", center=(WIDTH / 2, HEIGHT / 2 + 50), fontsize=40, color=quit_color)

def update_victory():
    global STATE, selected_option   

    if (keyboard.up or keyboard.w) and not keyboard.up_previous:
        selected_option = (selected_option - 1) % 3
    if (keyboard.down or keyboard.s) and not keyboard.down_previous:
        selected_option = (selected_option + 1) % 3

    if keyboard.RETURN:
        if selected_option == 0:  # Menu
            STATE = "MENU"
            knight.pos = (10, 500)
            coin.pos = (30, 220)
        elif selected_option == 1:  # Sair
            exit()

    # Keyboard shortcuts
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
        if selected_option == 0:  # Play
            STATE = "PLAYING"
        elif selected_option == 1:  # Quit        
            exit()
        if selected_option == 2:
            # Toggle sound on/off
            global sound_on
            sound_on = not sound_on
            if sound_on:
                # Play menu music immediately when turning sound back on
                music.play('time_for_adventure')
            else:
                music.stop()
                sounds.jump.stop()

    if keyboard.escape:  # Escape still works to quit
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