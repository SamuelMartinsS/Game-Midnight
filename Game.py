import pygame
import sys
from pygame import *
import pandas as pd
import csv
from pygame import mixer

pygame.init()
mixer.init()

pygame.mixer.Channel(0).play(pygame.mixer.Sound('Audio/music.wav'))

LINHAS = 21
COLUNAS = 150
TAMANHO = 800 // LINHAS
level = 0
display = pygame.display.set_mode((800,600))
FPS = pygame.time.Clock()

#criar lista pixeis vazia
world_data =  []
for row in range(LINHAS):
    r = [-1] * COLUNAS
    world_data.append(r)

#carregar dados do mundo
df = pd.read_csv(f'Niveis/level{level}_data.csv')
img_list = []
for i in range(8):
    try:
        img = pygame.image.load(f'Blocos/{i}.png')
        img = pygame.transform.scale(img, (TAMANHO,TAMANHO))
        img_list.append(img)
    except:
        img = pygame.image.load('Blocos/1.png')
        img_list.append(img)

###############################################################################
# PLAYER
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.animation_list = []
        self.index = 0
        self.update_timer = pygame.time.get_ticks()
        for i in range(4):
            img = pygame.image.load(f'Player/{i}.png')
            img = pygame.transform.scale(
                img, (int(img.get_width() * 3), int(img.get_height() * 3)))

            self.animation_list.append(img)

        self.image = self.animation_list[self.index]
        self.rect = self.image.get_rect()
        self.jumped = False
        self.jumping = False
        self.vel_y = 0
        self.flip = False
        self.rect.center = (200, 400)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.in_air = False

    def idle(self):
        self.animation_list = []
        for i in range(4):
            if self.in_air:
                img = pygame.image.load(f'Player/j{i}.png')
            else:
                img = pygame.image.load(f'Player/{i}.png')
            img = pygame.transform.scale(img, (int(img.get_width() * 3), int(img.get_height() * 3)))
            img = pygame.transform.flip(img, self.flip, False)
            self.animation_list.append(img)
            
    def colisao(self,x):
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + x, self.rect.y, self.width, self.height):
                return True
        return False

    def move(self, x):
        self.animation_list = []
        if self.colisao(x):
            x=0
        self.rect.move_ip(x, 0)
        for i in range(4):
            if jumping:
                img = pygame.image.load(f'Player/j{i}.png')
            else:
                img = pygame.image.load(f'Player/r{i}.png')
            img = pygame.transform.scale(img, (int(img.get_width() * 3), int(img.get_height() * 3)))
            img = pygame.transform.flip(img, self.flip, False)
            self.animation_list.append(img)

    def animation(self):
        COOLDOWN = 100
        try:
            self.image = self.animation_list[self.index]
            if pygame.time.get_ticks() - self.update_timer > COOLDOWN:
                self.update_timer = pygame.time.get_ticks()
                self.index += 1
            if self.index >= len(self.animation_list):
                self.index = 0
        except:
            self.index = 0

    def getX(self):
        return self.rect.centerx

    def getY(self):
        return self.rect.centery

    def jump(self):
        if jumping and self.in_air == False:
            self.vel_y = -27
            self.in_air = True

    def gravity(self):
        dy = 0
        self.vel_y += 2
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    dy = tile[1].bottom - self.rect.top
                    self.vel_y = 0
                elif self.vel_y >= 0:
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom
                    self.vel_y = 0
        self.rect.y += dy

    def getFlip(self):
        return self.flip

    def setFlip(self,aflip):
        self.flip = aflip


    def createBullet(self, name):
        pygame.mixer.Channel(6).play(pygame.mixer.Sound('Audio/enemy_gun.wav'))
        return PlayerBullet(name, self.rect.centerx+10, self.rect.centery-5)

    def reset(self):
        self.rect.center = (200, 400)

    def draw(self):
        display.blit(self.image, self.rect)

###############################################################################
# BALAS DO JOGADOR

class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self,name,x,y):
        super().__init__()
        self.path = 5
        self.image = pygame.image.load(name)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    
    def setPath(self,condition):
        if condition:
            self.path = -10
        else :
            self.path = 10
            
    def update(self):
        self.rect.centerx += self.path

        for _enemy in all_enemy:
            if self.rect.colliderect(_enemy):
                if _enemy.getAlive() == True :
                    pygame.mixer.Channel(5).play(pygame.mixer.Sound('Audio/enemy_death.wav'))
                    self.kill()
                    _enemy.setAlive(False)
                    _enemy.kill()
        for _boss in gameboss:
            if self.rect.colliderect(_boss.rect.x, _boss.rect.y, _boss.width, _boss.height):
                pygame.mixer.Channel(1).play(pygame.mixer.Sound('Audio/hit.wav'))
                _boss.damage()
                self.kill()

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + self.path/2, self.rect.y, self.width, self.height):
                self.kill()

###############################################################################
# VIDA DO JOGADOR

class Stats(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.index = 0
        self.image = pygame.image.load(f'Stats/hp_0.png')
        self.rect = self.image.get_rect()
        self.rect.center = (60,15)

    def updateHP(self):
        self.index += 1

        if self.index < 6 and self.index >= 0:
            self.image = pygame.image.load(f'Stats/hp_{self.index}.png')
            self.rect = self.image.get_rect()
        else:
            self.image = pygame.image.load(f'Stats/hp_6.png')
            self.rect = self.image.get_rect()
    
    def gethp(self):
        return self.index
    
    def reset(self):
        self.image = pygame.image.load(f'Stats/hp_0.png')
        self.rect = self.image.get_rect()
        self.index = 0

    def draw(self):
        display.blit(self.image, self.rect)

###############################################################################
# ENEMY

class Enemy(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.animation_list = []
        self.alive = True
        self.index = 0
        self.flip = True
        self.update_timer = pygame.time.get_ticks()
        self.vel_y = 0;
        
        for i in range(4):
            img = pygame.image.load(f'enemy/i{i}.png')
            img = pygame.transform.flip(img,self.flip, False)
            img = pygame.transform.scale(img, (int(img.get_width() * 3), int(img.get_height() * 3)))
            self.animation_list.append(img)

        self.image = self.animation_list[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    
    def getAlive(self):
        return self.alive
    
    def setAlive(self,bool):
        self.alive = bool

    def whereisplayer(self,playerx):
        if self.rect.centerx < playerx:
            self.flip = False
        else :
            self.flip = True

    def enemylook(self):
        self.animation_list = []
        for i in range(4):
            img = pygame.image.load(f'enemy/i{i}.png')
            img = pygame.transform.flip(img, self.flip, False)
            img = pygame.transform.scale(img, (int(img.get_width() * 3), int(img.get_height() * 3)))
            self.animation_list.append(img)

    def animation(self):
        COOLDOWN = 200
        try:
            self.image = self.animation_list[self.index]
            if pygame.time.get_ticks() - self.update_timer > COOLDOWN:
                self.update_timer = pygame.time.get_ticks()
                self.index += 1
            if self.index >= len(self.animation_list):
                self.index = 0
        except:
            self.index = 0

    def getX(self):
        return self.rect.centerx

    def getY(self):
        return self.rect.centery

    def createBullet_left(self, name):
        pygame.mixer.Channel(4).play(pygame.mixer.Sound('Audio/enemy_gun.wav'))
        return EnemyBullet_left(name, self.rect.centerx-10, self.rect.centery-15)

    def createBullet_right(self, name):
        pygame.mixer.Channel(4).play(pygame.mixer.Sound('Audio/enemy_gun.wav'))
        return EnemyBullet_right(name, self.rect.centerx-10, self.rect.centery-15)
    
    def hit(self,bullet):
        if self.rect.colliderect(bullet):
            self.kill

    def move(self,scroll):
        self.rect.centerx += scroll
        
    def gravity(self):
        dy = 0
        self.vel_y += 2
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    dy = tile[1].bottom - self.rect.top
                    self.vel_y = 0
                elif self.vel_y >= 0:
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom
                    self.vel_y = 0
        self.rect.y += dy

    def draw(self):
        display.blit(self.image, self.rect)

###############################################################################
# BALAS DA ESQUERDA

class EnemyBullet_left(pygame.sprite.Sprite):
    def __init__(self, name, x, y):
        super().__init__()
        self.image = pygame.image.load(name)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self,player,stats):
        self.inicio = self.rect.centerx
        self.rect.centerx -= 10
        if self.rect.centerx == 0:
            self.kill()
        if self.rect.colliderect(player):
            stats.updateHP()
            self.kill()
        for tile in world.obstacle_list:
        #check collision in the x direction
            if tile[1].colliderect(self.rect.x + 5, self.rect.y, self.width, self.height):
                self.kill()

###############################################################################
# BALAS DA DIREITA

class EnemyBullet_right(pygame.sprite.Sprite):
    def __init__(self, name, x, y):
        super().__init__()
        self.image = pygame.image.load(name)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
   
    def update(self,player,stats):
        self.rect.centerx += 10
        if self.rect.centerx == 800:
            self.kill()
        if self.rect.colliderect(player):
            stats.updateHP()
            self.kill()

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x - 5, self.rect.y, self.width, self.height):
                self.kill()
class Token(pygame.sprite.Sprite):
    def __init__(self,x,y,tipo):
        super().__init__()
        self.tipo = tipo
        if self.tipo == 1:
            name = "Tokens/next.png"
        else:
            name = "Tokens/upgrade.png"
        self.image = pygame.image.load(name)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.level = 0
    
    def update(self,player):
        if self.rect.colliderect(player):
            if self.tipo == 1:
                self.kill()
                self.level += 1
                return True
            else:
                if level >= 3:
                    for _boss in gameboss:
                        _boss.setDamage()
                    self.kill()
        return False

    def move(self,scroll):
        self.rect.centerx += scroll

    def draw(self):
        display.blit(self.image, self.rect)


            
###############################################################################
# CARREGAR BACKGROUND
class World(pygame.sprite.Sprite):
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TAMANHO
                    img_rect.y = y * TAMANHO
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 3:
                        self.obstacle_list.append(tile_data)
                    if tile == 4:
                        nextlevel = Token(x*TAMANHO, y*TAMANHO,1)
                        next_level.add(nextlevel)
                    elif tile == 5:
                        enemy = Enemy(x*TAMANHO-20, y*TAMANHO-20)
                        all_enemy.add(enemy)   
                    elif tile == 6:
                        leboss = Boss(x*TAMANHO,y*TAMANHO)   
                        gameboss.add(leboss)
                    elif tile == 7:
                        Damage_Boost = Token(x*TAMANHO, y*TAMANHO,2)
                        next_level.add(Damage_Boost)
                     
    def removemap(self):
        self.obstacle_list = []

    def screen_scroll(self,scroll):
        for tile in self.obstacle_list:
            tile[1][0] += scroll

    def draw(self):
        for tile in self.obstacle_list:
            display.blit(tile[0], tile[1])

class Background(pygame.sprite.Sprite):
    def __init__(self,name,x,y):
        super().__init__()
        self.index = 0
        self.update_timer = pygame.time.get_ticks()
        img = pygame.image.load(name)
        self.image = pygame.transform.scale(img, (int(img.get_width() * 1.85), int(img.get_height() * 1.85)))

        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
    
    def animation(self,acooldown,move):
        COOLDOWN = acooldown
        if pygame.time.get_ticks() - self.update_timer > COOLDOWN:
            self.update_timer = pygame.time.get_ticks()
            self.rect.centerx += -move
        if self.rect.centerx <= 0:
            self.rect.centerx = 1060

    def draw(self):
        display.blit(self.image, self.rect)

###############################################################################
# CARREGAR IMAGENS

class LoadImage(pygame.sprite.Sprite):
    def __init__(self,name,y):
        super().__init__()
        self.image = pygame.image.load(name)
        self.rect = self.image.get_rect()
        self.rect.center = (400,y)

    def draw(self):
        display.blit(self.image, self.rect)

###############################################################################
# BOSS

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.animation_list = []
        self.index = 0
        self.damageplayer = True
        self.second_stage = False
        self.flip = True
        self.stop = False
        self.hp = 20
        self.update_timer = pygame.time.get_ticks()
        self.damage_ = 1


        for i in range(4):
            img = pygame.image.load(f'boss/{i}.png')
            img = pygame.transform.flip(img, self.flip, False)
            img = pygame.transform.scale(img, (int(img.get_width() * 2), int(img.get_height() * 2)))
            self.animation_list.append(img)
    

        self.image = self.animation_list[self.index]
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)



    def secondstage(self):
        if self.second_stage == False:
            self.second_stage = True
            self.rect.y -= 100

        self.animation_list = []
        for i in range(4):
            img = pygame.image.load(f'boss/e{i}.png')
            img = pygame.transform.flip(img, self.flip, False)
            img = pygame.transform.scale(
                img, (int(img.get_width() * 3), int(img.get_height() * 3)))
            self.animation_list.append(img)


    def animation(self):
        COOLDOWN = 100
        try:
            self.image = self.animation_list[self.index]
            if pygame.time.get_ticks() - self.update_timer > COOLDOWN:
                self.update_timer = pygame.time.get_ticks()
                self.index += 1
            if self.index >= len(self.animation_list):
                self.index = 0
        except:
            self.index = 0

    def chase(self, x):
        if self.stop == False:
            if x < self.rect.centerx:
                self.rect.centerx -= 1

            if x > self.rect.centerx:
                self.rect.centerx += 1

    def gethp(self):
        return self.hp

    def setDamage(self):
        self.damage_ = 2
        
    def damage(self):
        self.hp -= self.damage_
    
    def hit(self,player,stats):
        if self.rect.colliderect(player):
            self.stop = True
            if self.damageplayer == True:
                pygame.mixer.Channel(2).play(pygame.mixer.Sound('Audio/boss.wav'))
                self.damageplayer = False
                stats.updateHP()

    def continuar(self):
        self.stop = False
        self.damageplayer = True

    def move(self,scroll):
        self.rect.centerx += scroll
    
    def bosskill(self):
        if self.hp <= 0:
            self.kill()
            self.bosskillsound()
            return True
        return False

    def bosskillsound(self):
        if self.hp <= 0:
            pygame.mixer.Channel(3).play(pygame.mixer.Sound('Audio/boss_death.wav'))
            self.kill()

    def draw(self):
        display.blit(self.image, self.rect)

###############################################################################
# VARIAVEIS

e_bullet = "Balas/e_bullet_.png"
p_bullet = "Balas/p_bullet_.png"


player = Player()


gameboss = pygame.sprite.Group()

all_enemy = pygame.sprite.Group()

stats = Stats()

all_bullets = pygame.sprite.Group()

enemy_bullets_left = pygame.sprite.Group()
enemy_bullets_right = pygame.sprite.Group()
next_level = pygame.sprite.Group()


#Cooldown
jumping = False
lock_pos = True
bullet_cd = True
bullet_enemy = True
cooldowns = True
timer = 1
bosstimer = 3
cd = 0
screen_scroll = 0
START = False
final_lvl = True
complete = False

_victory_ = False

bg0 = Background('Background/0.png',400, 300)
bg1 = Background('Background/1.png',400, 300)
bg2 = Background('Background/2.png',1060, 420)
bg3 = Background('Background/3.png',1060, 420)

building = LoadImage('Background/buildings.png',300)

over = LoadImage('Background/gameover.png',300)
menu = LoadImage('Background/main.png',300)
continuar = LoadImage('Background/continue.png',300)
victory = LoadImage('Background/victory.png',300)

INMENU = True
def updateworld():
    with open(f'Niveis/level{level}_data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                world_data[x][y] = int(tile)

    return world_data

world = World()
world.process_data(updateworld())
while True:

    keys = pygame.key.get_pressed()
    fps = FPS.tick(60)

    if INMENU == True:
        bullet_cd = False
        bg0.draw()
        bg1.draw()
        bg2.draw()
        bg3.draw()

        bg2.animation(300,1)
        bg3.animation(100,1)
        menu.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.QUIT
                sys.exit()

            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                INMENU = False


    else:
        building.draw()
        world.draw()
        stats.draw()
        player.draw()
        player.gravity()


        for _enemy in all_enemy:
            if _enemy.getAlive() == True:
                _enemy.draw()
                _enemy.gravity()

        playerx = player.getX()
        playery = player.getY()
        
        for _enemy in all_enemy:
            _enemy.whereisplayer(playerx)
            _enemy.enemylook()
            _enemy.animation()   
        player.animation()
        
        if final_lvl == True:
            for _boss in gameboss:
                _boss.draw()
                _boss.animation()
                _boss.chase(playerx)
                _boss.hit(player,stats)
                _victory_ =  _boss.bosskill()
                if _boss.gethp() < 10 :
                    _boss.secondstage()

        if player.getFlip() == False:
            player.setFlip(False)
            player.idle()
        if player.getFlip() == True:
            player.setFlip(True)
            player.idle()
    

        if keys[pygame.K_a]:
            player.setFlip(True)
            if player.getX() > 50 :
                player.move(-5)
                
            if player.getX() <= 50 and not(player.colisao(-5)) :
                world.screen_scroll(5)
                for _enemy in all_enemy:
                    _enemy.move(5)
                for _boss in gameboss:
                    _boss.move(5)
                for nxt in next_level:
                    nxt.move(5)
                player.move(0)

        if keys[pygame.K_d]:
            player.setFlip(False)
            if player.getX() < 500 :
                player.move(5)

            if player.getX() >= 500 and not(player.colisao(5)):
                world.screen_scroll(-5)
                for _enemy in all_enemy:
                    _enemy.move(-5)
                for _boss in gameboss:
                    _boss.move(-5)
                for nxt in next_level:
                    nxt.move(-5)
                player.move(0)

                
        if keys[pygame.K_SPACE] and player.in_air == False:
            jumping = True
        else:
            jumping = False


        player.jump()


        if timer <= 0:
            timer = 1
            bullet_cd = True 
            for _enemy in all_enemy:
                if player.getX() >= _enemy.getX():
                    if _enemy.getX()  > player.getX() - 500:
                        if _enemy.getY() < player.getY() + 180 and _enemy.getY() > player.getY() - 180:
                            enemy_bullets_right.add(_enemy.createBullet_right(e_bullet))
                else:
                    if _enemy.getX()  < player.getX() + 500:
                        if _enemy.getY() < player.getY() + 180 and _enemy.getY() > player.getY() - 180:
                            enemy_bullets_left.add(_enemy.createBullet_left(e_bullet))

        if bosstimer <= 0:
            for _boss in gameboss:
                _boss.continuar()
            bosstimer = 3

        cd = fps / 1000
        timer -= cd
        bosstimer -= cd
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.QUIT
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN and bullet_cd:
                if player.getFlip() == False:
                    bullet = player.createBullet(p_bullet)
                    bullet.setPath(False) 
                    all_bullets.add(bullet)
                    bullet_cd = False
                else :
                    bullet = player.createBullet(p_bullet)
                    bullet.setPath(True) 
                    all_bullets.add(bullet)
                    bullet_cd = False  


        all_bullets.draw(display)

        all_bullets.update()

        enemy_bullets_left.draw(display)
        enemy_bullets_left.update(player,stats)

        enemy_bullets_right.draw(display)
        enemy_bullets_right.update(player,stats)

        for nxt in next_level:
            nxt.draw()
            complete = nxt.update(player)

     
        if complete:
            level += 1
            timer = 1

            for _enemy in all_enemy:
                _enemy.kill()
            for nxt in next_level:
                nxt.kill()
            for _bullet in all_bullets:
                _bullet.kill()
            for _bullet in enemy_bullets_left:
                _bullet.kill()
            for _bullet in enemy_bullets_right:
                _bullet.kill()


            

            if level >= 0 and level <= 3:
                stats.reset()
                player.reset()  
                world.removemap()
                pygame.mixer.Channel(0).play(pygame.mixer.Sound('Audio/music.wav'))
                world.process_data(updateworld())
                complete = False
                if level == 3:

                    final_lvl = True

                
           

        if stats.gethp() >= 6:
            for _bullet in all_bullets:
                _bullet.kill()
            for _bullet in enemy_bullets_left:
                _bullet.kill()
            for _bullet in enemy_bullets_right:
                _bullet.kill()
            for _enemy in all_enemy:
                _enemy.kill()
            for nxt in next_level:
                nxt.kill()
            for _boss in gameboss:
                _boss.kill()

            level = 0
            over.draw()
            continuar.draw()

            if keys[pygame.K_r]:
                stats.reset()
                player.reset()     
                world.removemap()
                pygame.mixer.Channel(0).play(pygame.mixer.Sound('Audio/music.wav'))
                world.process_data(updateworld())
 

                INMENU = True

        if _victory_:
            for _enemy in all_enemy:
                _enemy.kill()
            for nxt in next_level:
                nxt.kill()
            for _bullet in all_bullets:
                _bullet.kill()
            for _bullet in enemy_bullets_left:
                _bullet.kill()
            for _bullet in enemy_bullets_right:
                _bullet.kill()

            victory.draw()
            continuar.draw()

            if keys[pygame.K_r]:
                level = 0
                stats.reset()
                player.reset()
                world.removemap()
                world.process_data(updateworld())
                _victory_ = False
                INMENU = True

    pygame.display.update()
    
    
