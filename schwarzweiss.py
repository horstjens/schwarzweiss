#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       schwarzweiss.py
#       
#       Copyright 2010 Horst JENS <horst.jens@spielend-programmieren.at>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.


import pygame
import random
import math

GRAD = math.pi / 180 # 2 * pi / 360   # math module needs Radiant instead of Grad

config =\
{'fullscreen': False,
 'width': 800,
 'height': 600,
 'fps': 100,
 'title': "SchwarzWeiss (press Esc to exit)",
 '-----------------------':0,
 'dt': 0.01,
 'friction': 0.987,
 'player_sizefac': 1.2,
 'player_color': (0, 0, 255),
 'player_accel': 400,
 'width_sensors': 8,
 'height_sensors': 8,
 
 'waiting_text': "quit=Esc, again=Other Key"}
    

        
        
    
        

class Bullet(pygame.sprite.Sprite):
    side = 10
    vec = 180 # velocity
    def __init__(self, boss):
        pygame.sprite.Sprite.__init__(self, self.groups) # THE most important line !
        self.boss = boss
        self.vec = Bullet.vec
        self.radius = Bullet.side # for collision detection
        self.color = self.boss.color
        image = pygame.Surface((Bullet.side, Bullet.side))
        image.fill((128,128,128)) # fill grey
        pygame.draw.circle(image, self.color, (self.side/2,self.side/2), self.side/2) #  circle
        pygame.draw.circle(image, (255,0,0), (self.side/2,self.side/2), self.side/2,1) #  circle
        image.set_colorkey((128,128,128)) # grey transparent
        self.image = image.convert_alpha()
        self.rect = image.get_rect()
        if self.boss.border == "left":
            self.dy = math.sin(degrees_to_radians(-self.boss.angle)) * self.vec
            self.dx = math.cos(degrees_to_radians(self.boss.angle)) * self.vec
        elif self.boss.border == "right":
            self.dy = -math.sin(degrees_to_radians(-self.boss.angle)) * self.vec
            self.dx = -math.cos(degrees_to_radians(self.boss.angle)) * self.vec
        self.value = 255
        #    self.dx = -99
        self.dy += self.boss.dy # add boss movement
        self.pos = self.boss.pos[:] # copy (!!!) of boss position
        self.update() # to avoid ghost sprite in upper left corner, force position calculation
        
    #def repaint(self):
    #    pygame.draw.circle(image, self.color, (self.side/2,self.side/2), self.side/2) #  circle
        
    def update(self, seconds=0.0):
        if self.value <= 0:
            self.kill()
        self.pos[0] += self.dx * seconds
        self.pos[1] += self.dy * seconds
        # ----- kill if out of screen
        if self.pos[0] < 0:
            self.kill()
        elif self.pos[0] > config["width"]:
            self.kill()
        # ----- bounce from upper or lower border
        if self.pos[1] < 0:
            self.pos[1] = 0
            self.dy *= -1
        elif self.pos[1] > config["height"]:
            self.pos[1] = config["height"]
            self.dy *= -1
        #------- move -------
        self.rect.centerx = round(self.pos[0],0)
        self.rect.centery = round(self.pos[1],0)
        
        
    
class Tank(pygame.sprite.Sprite):
    # a tank moving up and down at on side of the screen
    # bouncing at upper or lower screen edge
    side = 100 # side of the quadratic tank sprite
    recoiltime = 0.25 # how many seconds  the cannon is busy after firing one time
    turnspeed = 25
    movespeed = 25
    def __init__(self, border="left"):
        """left... white, right...black"""
        pygame.sprite.Sprite.__init__(self, self.groups) # THE most important line !
        self.pos = [0.0,0.0] # x,y
        self.border = border
        self.side = Tank.side
        self.pos[0] = 0.0
        self.pos[1] = config["height"] / 2 # <
        self.dx = 0
        self.dy = 0
        if self.border == "left":
            self.color = (255,255,255)
            self.dy *= -1
            self.pos[0] = self.side/2
            self.angle = 0
            self.firekey = pygame.K_LCTRL
            self.leftkey = pygame.K_a
            self.rightkey = pygame.K_d
            self.upkey = pygame.K_w
            self.downkey = pygame.K_s
        elif self.border == "right":
            self.color = (0,0,0)
            self.pos[0] = config["width"] - self.side/2
            self.dy = 25
            self.angle = 180
            self.firekey = pygame.K_RETURN
            self.leftkey = pygame.K_LEFT
            self.rightkey = pygame.K_RIGHT
            self.upkey = pygame.K_UP
            self.downkey = pygame.K_DOWN
        else:
            print "ERROR in class Tank: only left or right at the moment"
        
        image = pygame.Surface((self.side,self.side)) # created on the fly
        image.fill((128,128,128)) # fill grey
        pygame.draw.circle(image, (255,0,0), (self.side/2,self.side/2), 50, 2) # red circle
        pygame.draw.line(image, (255,0,0), (0,self.side), (self.side/2,0), 1) #red diagonal
        pygame.draw.line(image, (255,0,0), (self.side/2,0), (self.side,self.side), 1) # red diagonal
        image.set_colorkey((128,128,128)) # grey transparent
        self.imageUp = image.convert_alpha()
        self.imageDown = pygame.transform.flip(self.imageUp, False, True) # y flip
        #if self.dy < 0:
        #    self.image = self.imageUp
        #else:
        #    self.image = self.imageDown
        self.image = self.imageUp # default
        self.rect = self.image.get_rect()
        #---------- turret ------------------
        self.firestatus = 0.0 # time left until cannon can fire again
        self.turndirection = 0   
        #self.angle = 0
        self.movespeed = Tank.movespeed
        self.turnspeed = Tank.turnspeed
        Turret(self)
        

    
        
    def update(self, seconds):
        # no need for seconds but the other sprites need it
        
        #-------- reloading, firestatus----------
        if self.firestatus > 0:
            self.firestatus -= seconds # cannon will soon be ready again
            if self.firestatus <0:
                self.firestatus = 0 #avoid negative numbers
        # ------------ keyboard --------------
        pressedkeys = pygame.key.get_pressed()
        # -------- turret manual rotate ----------
        self.turndirection = 0    #  left / right turret rotation
        if pressedkeys[self.leftkey]:
            self.turndirection += 1
        if pressedkeys[self.rightkey]:
            self.turndirection -= 1
        self.updown = 0           # up / down tank movement
        if pressedkeys[self.upkey]:
            self.updown -= 1
        if pressedkeys[self.downkey]:
            self.updown += 1
        self.dy = self.movespeed * self.updown
        # ------------- up/down movement ---------------------
        self.pos[1] += self.dy * seconds
        if self.pos[1] + self.side/2 >= config["height"]:
            self.pos[1] = config["height"] - self.side/2
            #self.dy *= -1
            #self.image = self.imageUp
            self.dy = 0 # crash into border
        elif self.pos[1] -self.side/2 <= 0:
            self.pos[1] = 0 + self.side/2
            #self.dy *= -1
            #self.image = self.imageDown
            self.dy = 0
        if self.dy >0:
            self.image = self.imageDown
        elif self.dy <0:
            self.image = self.imageUp
        else:
            pass # no movement up/down
        self.rect.centerx = round(self.pos[0], 0) #x
        self.rect.centery = round(self.pos[1], 0) #y
        # -------- turret autorotate ----------
        self.angle += self.turndirection * self.turnspeed * seconds # time-based turning
        if self.angle > 90:
            #self.turndirection *= -1
            self.angle = 90
        elif self.angle < -90:
            #self.turndirection *= -1
            self.angle = -90
        # --------------- fire? -----------
        if self.firestatus ==0:
            if pressedkeys[self.firekey]:
                self.firestatus = Tank.recoiltime # seconds until tank can fire again
                Bullet(self)    
        else:
            pass # cannon busy
            
            
            

class Turret(pygame.sprite.Sprite):
    """turret on top of tank"""
    def __init__(self, boss):
        self._layer = 5
        pygame.sprite.Sprite.__init__(self, self.groups) # THE most important line !
        self.boss = boss
        
        self.side = self.boss.side
        self.heading = 0
        
        self.images = {}
        for recoil in range(6):
            self.images[recoil] = self.draw_cannon(recoil)
        for recoil in range(4):
            self.images[6+recoil] = self.draw_cannon(4-recoil)        
        self.image = self.images[0]
        self.images[10] = self.draw_cannon(0)
         
    def update(self, seconds):
        #print seconds
        
        if self.boss.firestatus > 0:
            #print int(self.boss.firestatus / (Tank.recoiltime / 10.0))
            #print "fire!"
            self.image = self.images[int(self.boss.firestatus / (Tank.recoiltime / 10.0))]
        else:
            self.image = self.images[0]

        # --------- rotating -------------
        # angle etc from Tank (boss)
        oldrect = self.image.get_rect() # store current surface rect
        self.image  = pygame.transform.rotate(self.image, self.boss.angle) 
        self.rect = self.image.get_rect()
        #self.rect.center = oldrect.center
        # put new surface rect center on same spot as old surface rect center
        # ---------- move with boss ---------
        self.rect = self.image.get_rect()
        self.rect.center = self.boss.rect.center

    
    def draw_cannon(self, offset):
         image = pygame.Surface((self.boss.side,self.boss.side)) # created on the fly
         image.fill((128,128,128)) # fill grey
         pygame.draw.circle(image, (255,0,0), (self.side/2,self.side/2), 22, 0) # red circle
         pygame.draw.circle(image, (0,255,0), (self.side/2,self.side/2), 18, 0) # green circle
         pygame.draw.rect(image, (0,255,0), (self.side/2-20 - offset,self.side/2 - 5, self.side/2+15 - offset,10)) # green cannon
         pygame.draw.rect(image, (255,0,0), (self.side/2-20 - offset,self.side/2 - 5, self.side/2+15 - offset,10),1) # red rect 
         image.set_colorkey((128,128,128))
         image = pygame.transform.rotate(image,self.boss.angle)
         #if self.boss.border == "right":
         #  return pygame.transform.flip(image, True, False) # x flip
         #else:
         return image

class Field(pygame.sprite.Sprite):
    sidex = 164
    sidey = 48
    cornerx = 0
    cornery = 0
    book = {}
    def __init__(self, posx, posy, value = 128):
        self.posy = posy
        self.posx = posx
        self.value = value
        self.color = (value,value,value)
        pygame.sprite.Sprite.__init__(self, self.groups) #THE most important line !
        self.image = pygame.Surface((Field.sidex, Field.sidey))
        self.image.fill((self.color))
        pygame.draw.rect(self.image,  (128,128,255), (0,0,Field.sidex, Field.sidey),1) # grid-rect around field
        self.rect = self.image.get_rect()
        #self.pos = [-100,-100]
        #self.dx = 0
        #self.dy = 0
        self.oldcolor = self.color[:]
        self.rect.centerx = Field.cornerx + Field.sidex / 2 + self.posx * Field.sidex
        self.rect.centery = Field.cornery + Field.sidey / 2 + self.posy * Field.sidey
    
    def update(self, seconds):
        if self.color != self.oldcolor:
            self.image.fill((self.color))
            pygame.draw.rect(self.image,  (128,128,255), (0,0,Field.sidex, Field.sidey),1)
        self.oldcolor = self.color[:]
        #print "ich werde geupdated"
    
#------------ defs ------------------
def radians_to_degrees(radians):
    return (radians / math.pi) * 180.0

def degrees_to_radians(degrees):
    return degrees * (math.pi / 180.0)

def elastic_collision(sprite1, sprite2):
    """elasitc collision between 2 sprites (calculated as disc's).
       The function alters the dx and dy movement vectors of both sprites.
       The sprites need the property .mass, .radius, .pos[0], .pos[1], .dx, dy
       pos[0] is the x postion, pos[1] the y position"""
    # here we do some physics: the elastic
    # collision
    # first we get the direction of the push.
    # Let's assume that the sprites are disk
    # shaped, so the direction of the force is
    # the direction of the distance.
    dirx = sprite1.pos[0] - sprite2.pos[0]
    diry = sprite1.pos[1] - sprite2.pos[1]
    # the velocity of the centre of mass
    sumofmasses = sprite1.mass + sprite2.mass
    sx = (sprite1.dx * sprite1.mass + sprite2.dx * sprite2.mass) / sumofmasses
    sy = (sprite1.dy * sprite1.mass + sprite2.dy * sprite2.mass) / sumofmasses
    # if we sutract the velocity of the centre
    # of mass from the velocity of the sprite,
    # we get it's velocity relative to the
    # centre of mass. And relative to the
    # centre of mass, it looks just like the
    # sprite is hitting a mirror.
    bdxs = sprite2.dx - sx
    bdys = sprite2.dy - sy
    cbdxs = sprite1.dx - sx
    cbdys = sprite1.dy - sy
    # (dirx,diry) is perpendicular to the mirror
    # surface. We use the dot product to
    # project to that direction.
    distancesquare = dirx * dirx + diry * diry
    if distancesquare == 0:
        # no distance? this should not happen,
        # but just in case, we choose a random
        # direction
        dirx = random.randint(0,11) - 5.5
        diry = random.randint(0,11) - 5.5
        distancesquare = dirx * dirx + diry * diry
    dp = (bdxs * dirx + bdys * diry) # scalar product
    dp /= distancesquare # divide by distance * distance.
    cdp = (cbdxs * dirx + cbdys * diry)
    cdp /= distancesquare
    # We are done. (dirx * dp, diry * dp) is
    # the projection of the velocity
    # perpendicular to the virtual mirror
    # surface. Subtract it twice to get the
    # new direction.
    # Only collide if the sprites are moving
    # towards each other: dp > 0
    if dp > 0:
        sprite2.dx -= 2 * dirx * dp 
        sprite2.dy -= 2 * diry * dp
        sprite1.dx -= 2 * dirx * cdp 
        sprite1.dy -= 2 * diry * cdp

        

def main():
    """versuche die Kasterln in Deine Farbe zu färben"""
    pygame.init()
    screen=pygame.display.set_mode((config["width"],config["height"])) 
    screenrect = screen.get_rect()
    background = pygame.Surface((screen.get_size()))
    backgroundrect = background.get_rect()
    #background.fill((128,128,128)) # fill grey
    pygame.draw.rect(background, (128,128,255), (0,0,Tank.side, config["height"])) # strip for left tank
    pygame.draw.rect(background, (128,128,255), (config["width"]-Tank.side,0,Tank.side, config["height"])) # strip for right tank
    background = background.convert()
    #background0 = background.copy()


    screen.blit(background, (0,0)) # delete all
    clock = pygame.time.Clock() #create pygame clock object
    mainloop = True
    FPS = config["fps"]         # desired max. framerate in frames per second. 
    playtime = 0
    
    
    tankgroup = pygame.sprite.Group()
    bulletgroup = pygame.sprite.Group()
    allgroup = pygame.sprite.LayeredUpdates()
    fieldgroup = pygame.sprite.Group()
    
    Tank._layer = 4
    Bullet._layer = 3
    Turret._layer = 6
    Field._layer = 2
    
 
    #assign default groups to each sprite class
    Tank.groups = tankgroup, allgroup
    Field.groups = allgroup, fieldgroup
    Turret.groups = allgroup
    Bullet.groups = bulletgroup, allgroup
    
    player1 = Tank("left")#
    player2 = Tank("right")
    
    #---------- fill grid with Field sprites ------------
    # 20 x 15
    lenx = 20
    leny = 15
    # how much space x in playfield ?
    lengthx = config["width"] - 2* Tank.side
    lengthy = config["height"]
    Field.sidex = lengthx / lenx
    Field.sidey = lengthy / leny
    Field.cornerx = Tank.side
    Field.cornery = 0
    
    for y in range(leny):
       for x in range(lenx):
           Field(x,y,128)
           
           
    while mainloop:
        milliseconds = clock.tick(config["fps"])  # milliseconds passed since last frame
        seconds = milliseconds / 1000.0 # seconds passed since last frame (float)
        playtime += seconds
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # pygame window closed by user
                mainloop = False 
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mainloop = False 

        for ball in bulletgroup:       
            crashgroup = pygame.sprite.spritecollide(ball, fieldgroup, False, pygame.sprite.collide_circle)      
            for crashfield in crashgroup:
                if ball.boss.border == "left" and crashfield.value <255:
                    crashfield.value += 1
                    crashfield.color = (crashfield.value,crashfield.value,crashfield.value)
                    ball.value -= 1
                elif ball.boss.border == "right" and crashfield.value >0:
                    crashfield.value -= 1
                    crashfield.color = (crashfield.value,crashfield.value,crashfield.value)
                    ball.value -= 1

        
        pygame.display.set_caption("FPS: %.2f >>> dx: %i dy %i %s" % (clock.get_fps(), player1.angle, player2.angle, config["title"]))
        #screen.blit(background, (0,0)) # delete all
        allgroup.clear(screen, background)
        allgroup.update(seconds)
        allgroup.draw(screen)
        pygame.display.flip() # flip the screen 30 times a second
    return 0

if __name__ == '__main__':
    main()

