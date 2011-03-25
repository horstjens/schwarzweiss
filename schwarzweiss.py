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

config =\
{'fullscreen': False,
 'width': 800,
 'height': 600,
 'fps': 100,
 'dt': 0.01,
 'friction': 0.987,
 'player_sizefac': 1.2,
 'player_color': (0, 0, 255),
 'player_accel': 400,
 'width_sensors': 8,
 'height_sensors': 8,
 'title': "SchwarzWeiss (press Esc to exit)",
 'waiting_text': "quit=Esc, again=Other Key"}
    

class Bullet(pygame.sprite.Sprite):
    """ a single bullet, fired from a Tank's cannon"""
    def __init__(self, boss):
        pass
    
class Tank(pygame.sprite.Sprite):
    # a tank moving up and down at on side of the screen
    # bouncing at upper or lower screen edge
    side = 100 # side of the quadratic tank sprite
    recoiltime = 0.5 # how many seconds  the cannon is busy after firing one time
    def __init__(self, border="left"):
        """left... white, right...black"""
        #self._layer = 4
        pygame.sprite.Sprite.__init__(self, self.groups) # THE most important line !
        
        self.border = border
        self.side = Tank.side
        self.x = 0.0
        self.y = config["height"] / 2
        self.dx = 0
        self.dy = 25
        if self.border == "left":
            self.color = (255,255,255)
            self.dy *= -1
            self.x = self.side/2
        elif self.border == "right":
            self.color = (0,0,0)
            self.x = config["width"] - self.side/2
            self.dy = 25
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
        if self.dy < 0:
            self.image = self.imageUp
        else:
            self.image = self.imageDown
        self.rect = self.image.get_rect()
        # turret
        self.firestatus = 0.0 # time left until cannon can fire again
        Turret(self)
        

    
        
    def update(self, seconds):
        # no need for seconds but the other sprites need it
        self.y += self.dy * seconds
        if self.y + self.side/2 >= config["height"]:
            self.y = config["height"] - self.side/2
            self.dy *= -1
            self.image = self.imageUp
        elif self.y -self.side/2 <= 0:
            self.y = 0 + self.side/2
            self.dy *= -1
            self.image = self.imageDown
        self.rect.centerx = round(self.x, 0)
        self.rect.centery = round(self.y, 0)
        if self.firestatus > 0:
            self.firestatus -= seconds # cannon will soon be ready again
            if self.firestatus <0:
                self.firestatus = 0 #avoid negative numbers
        
    def fire(self):
        if self.firestatus > 0:
            print "cannot fire, cannon busy"
        else:
            print "boom!"
            self.firestatus = Tank.recoiltime # seconds until tank can fire again

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

        self.turndirection = 1   
        self.angle = 0
        self.turnspeed = 55
        
        self.image = self.images[0]
        
         
    def update(self, seconds):
        #print seconds
        
        if self.boss.firestatus > 0:
            #print int(self.boss.firestatus / (Tank.recoiltime / 10.0))
            #print "fire!"
            self.image = self.images[int(self.boss.firestatus / (Tank.recoiltime / 10.0))]
        else:
            self.image = self.images[0]

        # --------- rotating -------------
        
        self.angle += self.turndirection * self.turnspeed * seconds # time-based turning
        if self.angle > 90:
            self.turndirection *= -1
            self.angle = 90
        elif self.angle < -90:
            self.turndirection *= -1
            self.angle = -90
        oldrect = self.image.get_rect() # store current surface rect
        self.image  = pygame.transform.rotate(self.image, self.angle) 
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
         if self.boss.border == "right":
           return pygame.transform.flip(image, True, False) # x flip
         else:
           return image
    
        

def main():
    """versuche die Kasterln in Deine Farbe zu färben"""
    pygame.init()
    screen=pygame.display.set_mode((config["width"],config["height"])) 
    screenrect = screen.get_rect()
    background = pygame.Surface((screen.get_size()))
    backgroundrect = background.get_rect()
    background.fill((128,128,128)) # fill white
    pygame.draw.rect(background, (128,128,255), (0,0,Tank.side, config["height"])) # strip for left tank
    pygame.draw.rect(background, (128,128,255), (config["width"]-Tank.side,0,Tank.side, config["height"])) # strip for right tank
    background = background.convert()
    background0 = background.copy()
    screen.blit(background,(0,0))

    #ballsurface = pygame.Surface((10,10))
    #ballsurface.set_colorkey((0,0,0)) # black transparent
    #pygame.draw.circle(ballsurface,(255,0,0),(5,5),5) # red ball
    #ballsurface = ballsurface.convert_alpha()
    #ballrect = ballsurface.get_rect()
    screen.blit(background, (0,0)) # delete all
    clock = pygame.time.Clock() #create pygame clock object
    mainloop = True
    FPS = config["fps"]         # desired max. framerate in frames per second. 
    playtime = 0
    
    
    tankgroup = pygame.sprite.Group()
    allgroup = pygame.sprite.LayeredUpdates()
    
    Tank._layer = 4
 
    #assign default groups to each sprite class
    Tank.groups = tankgroup, allgroup
    Turret.groups = allgroup
    

    
    player1 = Tank("left")#
    player2 = Tank("right")
    
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
                #if event.key == pygame.K_UP:
                #    dy -= 1 
                #if event.key == pygame.K_DOWN:
                #    dy += 1
                #if event.key == pygame.K_RIGHT:
                #    dx += 1
                #if event.key == pygame.K_LEFT:
                #    dx -= 1
                if event.key == pygame.K_SPACE:
                    player1.fire() 
                if event.key == pygame.K_RETURN:
                    player2.fire()
        
        pygame.display.set_caption("FPS: %.2f >>> dx: %i dy %i %s" % (clock.get_fps(), player1.firestatus, player2.y, config["title"]))
        #screen.blit(background, (0,0)) # delete all
        allgroup.clear(screen, background)
        allgroup.update(seconds)
        allgroup.draw(screen)
        pygame.display.flip() # flip the screen 30 times a second
    return 0

if __name__ == '__main__':
    main()

