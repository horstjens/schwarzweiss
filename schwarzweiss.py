#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       schwarzweiss.py
#       
#       author: Horst JENS <horst.jens@spielend-programmieren.at>
#       license: GPL (see below)
#       part of The Python Game Book
#       homepage: http://thepythongamebook.com/en:resources:games:schwarzweiss
#       source & download: https://github.com/horstjens/schwarzweiss
#       needs Python 2.6 or better, pygame 1.9.1 or better
       
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

class Config(object):
    """the Config class is used to store some global game parameters"""
    fullscreen = False
    width = 1024 # pixel
    height = 600 # picel
    fps = 100  # max. framerate in frames per second
    xtiles = 10 # how many fields horizontal
    ytiles = 5 # how many fields vertical
    title = "Esc: quit, left player: WASD, right player: Cursor"
    neutraltanks = 2 # number of neutral tanks
    tankxpercent = 0.4 # left tank is allowed in the left 40 % of playfield
    tracktolerance = 15 # tolerance (pixel) for turning tank in corner


class Spark(pygame.sprite.Sprite):
    """a small spark to indicate that a field has changed color"""
    side = 4
    friction = .99
    def __init__(self, pos, color, heading, lifetime ):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.pos = [0.0,0.0]
        self.pos[0] = pos[0]
        self.pos[1] = pos[1]
        self.lifetime = lifetime
        self.heading = heading
        self.color = color
        self.vec = 160
        self.image = pygame.Surface((Spark.side, Spark.side))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.dy = math.sin(self.heading)
        self.dx = math.cos(self.heading)
        
    
    def update(self, seconds):
        self.lifetime -= seconds
        if self.lifetime < 0:
            self.kill()
        #print "ich sparke"
        self.dx *= Spark.friction
        self.dy *= Spark.friction
        self.pos[0] += self.vec * self.dx * seconds
        self.pos[1] += self.vec * self.dy * seconds
        self.rect.centerx = round(self.pos[0],0)
        self.rect.centery = round(self.pos[1],0)
        
class Obstacle(pygame.sprite.Sprite):
    """ a rectangular, bulletproof obstacle"""
    def __init__(self, x,y, vertical = True):
        pygame.sprite.Sprite.__init__(self, self.groups)
        if vertical:
            self.image = pygame.Surface((10,Tank.side))
        else:
            self.image = pygame.Surface((Tank.side, 10))
        #self.image.set_colorkey((0,0,0))
        self.red = 128
        self.green = 128
        self.blue = 0
        self.dr = 1 # changing of red color
        self.image.fill((self.red, self.green, self.blue))
        self.image.convert()
        self.rect = self.image.get_rect()
        self.pos = [0,0]
        self.pos[0] = x
        self.pos[1] = y
        self.rect.centerx = round(self.pos[0],0)
        self.rect.centery = round(self.pos[1],0)
        
    def update(self, seconds):
        """slowly cycle the yellow-red color"""
        self.red += self.dr
        if self.red > 255 or self.red < 200:
            self.dr *= -1
            self.red = max(200, self.red)
            self.red = min(255, self.red)
        self.image.fill((self.red, self.green, self.blue))
        
class Energybar(pygame.sprite.Sprite):
       """a bar to indicate energy loss or gain
          barnumber:
          1 = energy reserve
          2 = gain/loss
          3 = change
          """
       length = Config.width / 4
       height = 20
       def __init__(self, pos, boss, barnumber):
           pygame.sprite.Sprite.__init__(self, self.groups)
           self.boss = boss
           self.pos = [0.0,0.0]
           self.pos[0] = pos[0]
           self.pos[1] = pos[1]
           self.image = pygame.Surface((Energybar.length,Energybar.height))
           self.image.set_colorkey((0,0,0))
           pygame.draw.rect(self.image, (255,255,255),(0,0,Energybar.length, Energybar.height),1)
           self.rect = self.image.get_rect()
           self.rect.centerx = round(self.pos[0],0)
           self.rect.centery = round(self.pos[1],0)
       
       def update(self, seconds):
           pass     
           

class Text(pygame.sprite.Sprite):
    def __init__(self, pos, msg, fontsize=32, color=(0,0,0)):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.pos = [0.0,0.0]
        self.pos[0] = pos[0]
        self.pos[1] = pos[1]
        self.fontsize = fontsize
        self.color = color
        self.msg = msg
        self.changemsg(msg)
        
    def update(self, seconds):        
        pass
        
    def changemsg(self,msg):
        self.msg = msg
        self.image = write(self.msg, self.fontsize, self.color)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.pos[0]
        self.rect.centery = self.pos[1]


class Bullet(pygame.sprite.Sprite):
    """ a big projectile fired by the tank's main cannon"""
    side = 7 # small side of bullet rectangle
    vel = 180 # velocity
    mass = 50
    maxlifetime = 10.0 # seconds
    def __init__(self, boss):
        pygame.sprite.Sprite.__init__(self, self.groups) # THE most important line !
        self.boss = boss
        self.dx = 0
        self.dy = 0
        self.static = False
        self.radius = Bullet.side / 2
        self.angle = 0
        self.lifetime = 0.0
        self.color = self.boss.color
        self.calculate_heading() # !!!!!!!!!!!!!!!!!!!
        self.book = {}
        self.value = 255
        self.dx += self.boss.dx
        self.dy += self.boss.dy # add boss movement
        self.pos = self.boss.pos[:] # copy (!!!) of boss position 
        #self.pos = self.boss.pos   # uncomment this linefor fun effect
        self.calculate_origin()
        self.update() # to avoid ghost sprite in upper left corner, 
                      # force position calculation.
                      
    def calculate_heading(self):
        """ drawing the bullet and rotating it according to it's launcher"""
        self.radius = Bullet.side # for collision detection
        self.angle += self.boss.turretAngle
        self.mass = Bullet.mass
        self.vel = Bullet.vel
        image = pygame.Surface((Bullet.side * 2, Bullet.side)) # rect 2 x 1
        image.fill((128,128,128)) # fill grey
        pygame.draw.rect(image, self.color, (0,0,Bullet.side * 1.5, Bullet.side)) # rectangle 1.5 length
        pygame.draw.circle(image, self.color, (self.side *1.5 ,self.side/2), self.side/2) #  circle
        pygame.draw.rect(image, (255,0,0), (0,0,Bullet.side * 1.5, Bullet.side),1) # rectangle 1.5 length
        image.set_colorkey((128,128,128)) # grey transparent
        
        
        self.image0 = image.convert_alpha()
        #self.image = self.image0.copy()
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.rect = self.image.get_rect()
        self.dx = math.cos(degrees_to_radians(self.boss.turretAngle)) * self.vel
        self.dy = math.sin(degrees_to_radians(-self.boss.turretAngle)) * self.vel
        
    def calculate_origin(self):
        # - spawn bullet at end of turret barrel instead tank center -
        # cannon is around Tank.side long, calculatet from Tank center
        # later subtracted 20 pixel from this distance
        # so that bullet spawns closer to tank muzzle
        self.pos[0] +=  math.cos(degrees_to_radians(self.boss.turretAngle)) * (Tank.side-20)
        self.pos[1] +=  math.sin(degrees_to_radians(-self.boss.turretAngle)) * (Tank.side-20)
    
    def rotate_toward_moving(self):
        """calculate the angle (heading) of a moving object (dx, dy)"""
        self.angle =  -90+math.atan2(self.dx, self.dy)/math.pi*180.0 
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.rect = self.image.get_rect()
            
    def update(self, seconds=0.0):
        if self.value <= 0:
            self.kill() 
        # ---- kill if too old ---
        # --- value kill
        self.lifetime += seconds
        if self.lifetime > Bullet.maxlifetime:
            self.kill()
        # ------ calculate movement --------
        self.pos[0] += self.dx * seconds
        self.pos[1] += self.dy * seconds
        # ----- kill if out of screen
        if self.pos[0] < 0:
            self.kill()
        elif self.pos[0] > Config.width:
            self.kill()
        # bounce upper or lower border
        
        if self.pos[1] < 0 or self.pos[1] > Config.height:
            print self.angle
            self.pos[1] = max(0, self.pos[1])
            self.pos[1] = min(Config.height, self.pos[1])
            self.dy *= -1
            self.rotate_toward_moving()
            
        #------- move -------
        self.rect.centerx = round(self.pos[0],0)
        self.rect.centery = round(self.pos[1],0)

        
        
    

class Tracer(Bullet):
    """Tracer is nearly the same as Bullet, but smaller
       and with another origin (bow MG rect instead cannon.
       Tracer inherits all methods of Bullet, but i overwrite
       calculate_heading and calculate_origin"""
    side = 15 # long side of bullet rectangle
    vel = 200 # velocity
    mass = 10
    color = (200,0,100)
    maxlifetime = 10.0 # seconds
    def __init__(self, boss, turret=False):
        self.turret = turret
        Bullet.__init__(self,boss ) # this line is important 
        self.value = 16
        
    def calculate_heading(self):
        """overwriting the method because there are some differences 
           between a tracer and a main gun bullet"""
        self.radius = Tracer.side # for collision detection
        self.angle = 0
        self.angle += self.boss.tankAngle
        if self.turret:
            self.angle = self.boss.turretAngle
        self.mass = Tracer.mass
        self.vel = Tracer.vel
        image = pygame.Surface((Tracer.side, Tracer.side / 4)) # a line 
        image.fill(self.boss.color) # fill yellow ? 
        pygame.draw.rect(image, (255,0,0), (Tracer.side * .75, 0, Tracer.side, Tracer.side / 4)) # red dot at front
        image.set_colorkey((128,128,128)) # grey transparent
        self.image0 = image.convert_alpha()
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.rect = self.image.get_rect()
        if self.turret:
            # turret mg
            self.dx = math.cos(degrees_to_radians(self.boss.turretAngle)) * self.vel
            self.dy = math.sin(degrees_to_radians(-self.boss.turretAngle)) * self.vel
        else:
            # bow mg
            self.dx = math.cos(degrees_to_radians(self.boss.tankAngle)) * self.vel
            self.dy = math.sin(degrees_to_radians(-self.boss.tankAngle)) * self.vel

    def calculate_origin(self):
        """overwriting because another point of origin is needed"""
        # - spawn bullet at end of machine gun muzzle (bow or turret)
        if self.turret:
            self.pos[0] +=  math.cos(degrees_to_radians(-90+self.boss.turretAngle)) * 15
            self.pos[1] +=  math.sin(degrees_to_radians(90-self.boss.turretAngle)) * 15
        else:
            self.pos[0] +=  math.cos(degrees_to_radians(30+self.boss.tankAngle)) * (Tank.side/2)
            self.pos[1] +=  math.sin(degrees_to_radians(-30-self.boss.tankAngle)) * (Tank.side/2)


            
class Tank(pygame.sprite.Sprite):
    """ A Tank, controlled by the Player with Keyboard commands.
    This Tank draw it's own Turret (including the main gun) 
    and it's bow rectangle (slit for Tracer Machine Gun"""
    side = 100 # side of the quadratic tank sprite
    recoiltime = 0.75 # how many seconds  the cannon is busy after firing one time
    mgrecoiltime = 0.2 # how many seconds the bow mg (machine gun) is idle
    turretTurnSpeed = 50 # turret
    tankTurnSpeed = 80 # tank
    movespeed = 80
    #maxrotate = 360 # maximum amount of degree the turret is allowed to rotate
    book = {} # a book of tanks to store all tanks
    number = 0 # each tank gets his own number
    # keys for tank control, expand if you need more tanks
    #          player1,        player2    etc
    firekey = (pygame.K_LSHIFT, pygame.K_RCTRL)
    #mgfirekey = (pygame.K_LCTRL, pygame.K_KP_ENTER)
    #mg2firekey = (pygame.K_i, pygame.K_UP)
    turretLeftkey = (pygame.K_a, pygame.K_LEFT)
    turretRightkey = (pygame.K_d, pygame.K_RIGHT)
    forwardkey = (pygame.K_w, pygame.K_UP)
    backwardkey = (pygame.K_s, pygame.K_DOWN)
    #tankLeftkey = (pygame.K_a, pygame.K_KP4)
    #tankRightkey = (pygame.K_d, pygame.K_KP6)
    color = ((255,255,255), (0,0,0))
    #msg = ["wasd LCTRL, ijkl", "Keypad: 4852, ENTER, cursor"]
    # ----- energy gain and loss per second -----
    ebasegain = 10 # energy gain per second
    ehitgain = 1
    eturrethitgain = 25
    egridgain = 5
    egridconvert = 50
    emoveloss = 9
    erotateloss = 12
    ebulletloss = 40
    etracerloss = 15
    ehitloss = 2
    eturrethitloss = 50
    
          
    def __init__(self, startpos = (150,150), turretangle=0, tankangle=90):
        self.number = Tank.number # now i have a unique tank number
        Tank.number += 1 # prepare number for next tank
        Tank.book[self.number] = self # store myself into the tank book
        pygame.sprite.Sprite.__init__(self, self.groups) # THE most important line !
        self.pos = [startpos[0], startpos[1]] # x,y
        self.dx = 0
        self.dy = 0
        self.damage = 0
        self.mass = 20000
        self.static = True
        self.radius = self.side / 3 # for collision detection
        #self.ammo = 30 # main gun
        self.mgammo = 500 # machinge gun
        self.energy = 100
        
        self.turretAngle = turretangle #turret facing
        self.tankAngle = tankangle # tank facing
        #self.msg =  "tank%i: x:%i y:%i facing: turret:%i tank:%i"  % (self.number, self.pos[0], self.pos[1], self.turretAngle, self.tankAngle )
        #Text((Config.width/2, 30+20*self.number), self.msg) # create status line text sprite
        if self.number < 2:
            self.color = Tank.color[self.number]
            self.firekey = Tank.firekey[self.number] # main gun
            #self.mgfirekey = Tank.mgfirekey[self.number] # bow mg
            #self.mg2firekey = Tank.mg2firekey[self.number] # turret mg
            self.turretLeftkey = Tank.turretLeftkey[self.number] # turret
            self.turretRightkey = Tank.turretRightkey[self.number] # turret
            self.forwardkey = Tank.forwardkey[self.number] # move tank
            self.backwardkey = Tank.backwardkey[self.number] # reverse tank
        else: # neutral tank
            self.color = (0,128,0) # dark green
        #self.tankLeftkey = Tank.tankLeftkey[self.number] # rotate tank
        #self.tankRightkey = Tank.tankRightkey[self.number] # rotat tank
        # painting facing north, have to rotate 90° later
        image = pygame.Surface((Tank.side,Tank.side)) # created on the fly
        image.fill((128,128,128)) # fill grey
        if self.side > 10:
             pygame.draw.rect(image, self.color, (5,5,self.side-10, self.side-10)) #tank body, margin 5
             pygame.draw.rect(image, (139,105,20), (0,0,self.side/6, self.side)) # brown track left
             pygame.draw.rect(image, (139,105,20), (self.side-self.side/6, 0, self.side,self.side)) # brown right track
             pygame.draw.rect(image, (255,0,0), (self.side/6+5 , 10, 10, 5)) # red bow rect left
             #pygame.draw.rect(image, (255,0,0), (self.side/2 - 5, 10, 10, 5)) # red bow rect middle
        pygame.draw.circle(image, (255,0,0), (self.side/2,self.side/2), self.side/3 , 2) # red circle for turret
        image = pygame.transform.rotate(image,-90) # rotate so to look east
        self.image0 = image.convert_alpha()
        self.image = image.convert_alpha()
        self.rect = self.image0.get_rect()
        #---------- turret ------------------
        self.firestatus = 0.0 # time left until cannon can fire again
        #self.mgfirestatus = 0.0 # time until mg can fire again
        #self.mg2firestatus = 0.0 # time until turret mg can fire again
        self.turndirection = 0    # for turret
        self.tankturndirection = 0
        self.movespeed = Tank.movespeed
        self.turretTurnSpeed = Tank.turretTurnSpeed
        self.tankTurnSpeed = Tank.tankTurnSpeed
        Turret(self) # create a Turret for this tank
        if self.number > 1: # neutral tanks
            self.dx = 0
            # make speed between 1/4 and 1/2 of player speed with random direction
            self.dy = (Tank.movespeed * 0.25 + random.random() * Tank.movespeed * 0.25) * random.choice((-1,1))
            self.targetplayer = random.choice((0,1))
            
    def update(self, seconds):
        # no need for seconds but the other sprites need it
        if self.firestatus > 0:
            self.firestatus -= seconds # cannon will soon be ready again
            if self.firestatus <0:
                self.firestatus = 0 #avoid negative numbers
        if self.number > 1: # neutral tanks
             self.aim_at_player(self.targetplayer)
        else: # player tanks
            #-------- reloading, firestatus----------

            #if self.mgfirestatus > 0:
            #    self.mgfirestatus -= seconds # bow mg will soon be ready again
            #    if self.mgfirestatus <0:
            #        self.mgfirestatus = 0 #avoid negative numbers
            #if self.mg2firestatus > 0:
            #    self.mg2firestatus -= seconds # turret mg will soon be ready again
            #    if self.mg2firestatus <0:
            #        self.mg2firestatus = 0 #avoid negative numbers
            
            # ------------ keyboard --------------
            pressedkeys = pygame.key.get_pressed()
            # -------- turret manual rotate ----------
            self.turndirection = 0    #  left / right turret rotation
            if self.number > 1:   # only for tank2
                self.aim_at_player()       # default aim at player0
            else:
                if pressedkeys[self.turretLeftkey]:
                    self.turndirection += 1
                if pressedkeys[self.turretRightkey]:
                    self.turndirection -= 1
               
            #---------- tank rotation ---------
            self.tankturndirection = 0 # reset left/right rotation
            #if pressedkeys[self.tankLeftkey]:
            #    self.tankturndirection = 1
            #if pressedkeys[self.tankRightkey]:
            #    self.tankturndirection = -1
            

            # ---------- fire cannon -----------
            #if (self.firestatus ==0) and (self.ammo > 0):
            if (self.firestatus ==0) :
                if pressedkeys[self.firekey]:
                    self.firestatus = Tank.recoiltime # seconds until tank can fire again
                    Bullet(self)    
                    #self.ammo -= 1
                    #self.msg =  "player%i: ammo: %i/%i keys: %s" % (self.number+1, self.ammo, self.mgammo, Tank.msg[self.number])
                    #Text.book[self.number].changemsg(self.msg)
            # -------- fire bow mg ---------------
            #if (self.mgfirestatus ==0) and (self.mgammo >0):
            #    if pressedkeys[self.mgfirekey]:
            #        self.mgfirestatus = Tank.mgrecoiltime
            #        Tracer(self, False) # turret mg = False
            #        self.mgammo -= 1
            #        #self.msg = "player%i: ammo: %i/%i keys: %s" % (self.number+1, self.ammo, self.mgammo, Tank.msg[self.number])
            #        #Text.book[self.number].changemsg(self.msg)
            # -------- fire turret mg ---------------
            #if (self.mg2firestatus ==0) and (self.mgammo >0):
            #    if pressedkeys[self.mg2firekey]:
            #        self.mg2firestatus = Tank.mgrecoiltime # same recoiltime for both mg's
            #        Tracer(self, True) # turret mg = True
            #        self.mgammo -= 1
            #        #self.msg =  "player%i: ammo: %i/%i keys: %s" % (self.number+1, self.ammo, self.mgammo, Tank.msg[self.number])
            #        #Text.book[self.number].changemsg(self.msg)
            # ---------- movement ------------
            self.dx = 0
            self.dy = 0
            self.forward = 0 # movement calculator
            if pressedkeys[self.forwardkey]:
                self.forward += 1
            if pressedkeys[self.backwardkey]:
                self.forward -= 1
            # if both are pressed togehter, self.forward becomes 0
            if self.forward == 1:
                self.dx =  math.cos(degrees_to_radians(self.tankAngle)) * self.movespeed
                self.dy =  -math.sin(degrees_to_radians(self.tankAngle)) * self.movespeed
            if self.forward == -1:
                self.dx =  -math.cos(degrees_to_radians(self.tankAngle)) * self.movespeed
                self.dy =  math.sin(degrees_to_radians(self.tankAngle)) * self.movespeed
        # ------------- check border collision ---------------------
        self.pos[0] += self.dx * seconds
        self.pos[1] += self.dy * seconds
        # ---- check norht / south border. rotate tank if touching border and moving
        #print self.tankAngle
        # -------- south border ---------
        # messy code
        if self.number > 1 and self.pos[1] > Config.height - Tank.side * 1.5:
            self.pos[1] = Config.height - Tank.side *1.5
            self.dy *= -1
        if self.pos[1] + self.side/2 >= Config.height:
            self.pos[1] = Config.height - self.side/2
            if self.number < 2:
                self.dy = 0 # do not leave screen
            else:
                self.dy *= -1
            if self.number == 0: # left tank, lower border, turn left
                if self.tankAngle < 180 and self.forward == -1:
                    self.tankturndirection = 1
            elif self.number == 1: # right tank, lower border, turn right
                if self.tankAngle > 0 and self.forward == -1:
                    self.tankturndirection = -1
        elif ((self.pos[0] > self.side/2 + 15) and
              (self.pos[0] <  Config.width - self.side / 2-15) and
              (self.pos[1] < Config.height/2) and self.number <2):
            # creeping on upper border
            if self.pos[1] > 0:
                self.pos[1] = self.side / 2
                self.dy = 0
        # ---------- north border -------------
        if self.number < 2: # player tanks are not allowed in upper area
            if self.pos[1] < Tank.side+ Tank.side/2 + 10:
                self.pos[1] = Tank.side+ Tank.side/2 + 10
                self.dy = 0
        else: # neutral tanks 
            if self.pos[1] < Tank.side / 2:
                self.pos[1] = Tank.side / 2
                self.dy *= -1
    
        # ----------- west border ------------
        if self.number < 2:
            if self.pos[0] - self.side/2 < 0: # left border
                 self.pos[0] = self.side/2 # do not leave screen   
                 if self.number == 0: # left tank
                     if self.tankAngle < 90 and self.forward == -1: # left tank , upper, turn left
                        self.tankturndirection = 1
                     elif self.tankAngle >0 and self.forward == 1:
                        self.tankturndirection = -1
            if self.number == 1: # right tank   
                 if (self.pos[1] <= self.side/2 +Config.tracktolerance )or (self.pos[1] >= Config.height - self.side/2 - Config.tracktolerance):
                     # creeping at north/south border
                     if self.pos[0] < Config.width - Config.width * Config.tankxpercent:
                         self.pos[0] = Config.width - Config.width * Config.tankxpercent
                 else:  # right of playfield
                     if self.pos[0] < Config.width - self.side/2:
                         self.pos[0] = Config.width - self.side/2
                                    
        #----- east border --------
        if self.number < 2:            
            if self.number == 0: # left tank
               if (self.pos[1] <= self.side/2 +Config.tracktolerance )or (self.pos[1] >= Config.height - self.side/2 - Config.tracktolerance):
                   # creeping at north/south border
                   if self.pos[0] > Config.width * Config.tankxpercent:
                       self.pos[0] = Config.width * Config.tankxpercent
               else:
                   # left of playfield:
                   if self.pos[0] > self.side / 2:
                        self.pos[0] = self.side / 2
            elif self.number == 1: # right tank
               if self.pos[0] > Config.width - self.side/2:
                   self.pos[0] = Config.width - self.side/2
                   if self.tankAngle > 90 and self.forward == -1: #uper right corner, turn right
                       self.tankturndirection = -1
                   elif self.tankAngle < 90 and self.forward == 1: # lower right corner, turn left
                       self.tankturndirection = 1
                       
                
            
            
        # ---------------- rotate tank ---------------
        self.tankAngle += self.tankturndirection * self.tankTurnSpeed * seconds # time-based turning of tank
        # angle etc from Tank (boss)
        oldcenter = self.rect.center
        oldrect = self.image.get_rect() # store current surface rect
        self.image  = pygame.transform.rotate(self.image0, self.tankAngle) 
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter 
        # if tank is rotating, turret is also rotating with tank !
        # -------- turret autorotate ----------
        self.turretAngle += self.tankturndirection * self.tankTurnSpeed * seconds  + self.turndirection * self.turretTurnSpeed * seconds # time-based turning                
                
                
                
        # --------- move -------
        self.rect.centerx = round(self.pos[0], 0) #x
        self.rect.centery = round(self.pos[1], 0) #y    
        #self.msg =  "tank%i: x:%i y:%i facing: turret:%i tank:%i"  % (self.number, self.pos[0], self.pos[1], self.turretAngle, self.tankAngle )
        #Text.book[self.number].changemsg(self.msg)
                    
    def aim_at_player(self, targetnumber=0):
        #print "my  pos: x:%.1f y:%.1f " % ( self.pos[0], self.pos[1])
        #print "his pos: x:%.1f y:%.1f " % ( Tank.book[0].pos[0], Tank.book[0].pos[1])  
        deltax = Tank.book[targetnumber].pos[0] - self.pos[0]
        deltay = Tank.book[targetnumber].pos[1] - self.pos[1]
        angle =   math.atan2(-deltax, -deltay)/math.pi*180.0            
        diff = (angle - self.turretAngle - 90) %360 #reset at 360
        
        # at 180° the target is in sight
        if diff > 179 and diff < 181: # target in sight
            #print "Bumm"
            self.turndirection = 0
            self.firestatus = Tank.recoiltime # seconds until tank can fire again
            Bullet(self)
            if self.targetplayer == 0:
                self.targetplayer = 1
            else:
                self.targetplayer = 0
        elif diff > 180:
            self.turndirection = 1
        else:
            self.turndirection = -1
        return diff

class Turret(pygame.sprite.Sprite):
    """turret on top of tank"""
    radius = 22 # red circle
    def __init__(self, boss):
        pygame.sprite.Sprite.__init__(self, self.groups) # THE most important line !
        self.boss = boss
        self.side = self.boss.side
        
        self.images = {} # how much recoil after shooting, reverse order of apperance
        self.images[0] = self.draw_cannon(0)  # idle position
        self.images[1] = self.draw_cannon(1)
        self.images[2] = self.draw_cannon(2)
        self.images[3] = self.draw_cannon(3)
        self.images[4] = self.draw_cannon(4)
        self.images[5] = self.draw_cannon(5)
        self.images[6] = self.draw_cannon(6)
        self.images[7] = self.draw_cannon(7)
        self.images[8] = self.draw_cannon(8)  # position of max recoil
        self.images[9] = self.draw_cannon(4)
        self.images[10] = self.draw_cannon(0) # idle position
         
    def update(self, seconds):        
        # painting the correct image of cannon
        if self.boss.firestatus > 0:
            self.image = self.images[int(self.boss.firestatus / (Tank.recoiltime / 10.0))]
        else:
            self.image = self.images[0]
        # --------- rotating -------------
        # angle etc from Tank (boss)
        oldrect = self.image.get_rect() # store current surface rect
        self.image  = pygame.transform.rotate(self.image, self.boss.turretAngle) 
        self.rect = self.image.get_rect()
        # ---------- move with boss ---------
        self.rect = self.image.get_rect()
        self.rect.center = self.boss.rect.center

    
    def draw_cannon(self, offset):
         # painting facing right, offset is the recoil
         image = pygame.Surface((self.boss.side * 2,self.boss.side * 2)) # created on the fly
         image.fill((128,128,128)) # fill grey
         pygame.draw.circle(image, (255,0,0), (self.side,self.side), Turret.radius, 0) # red circle
         pygame.draw.circle(image, (0,255,0), (self.side,self.side), 18, 0) # green circle
         pygame.draw.rect(image, (255,0,0), (self.side-10, self.side + 10, 15,2)) # turret mg rectangle
         pygame.draw.rect(image, (0,255,0), (self.side-20 - offset,self.side - 5, self.side - offset,10)) # green cannon
         pygame.draw.rect(image, (255,0,0), (self.side-20 - offset,self.side - 5, self.side - offset,10),1) # red rect 
         image.set_colorkey((128,128,128))
         return image            
            



class Field(pygame.sprite.Sprite):
    sidex = 164
    sidey = 48
    cornerx = 0
    cornery = 0
    book = {}
    whitesum = 0
    blacksum = 0
    fields = 0
    number = 0
    offsetx = 0
    def __init__(self, posx, posy, value = 128):
        self.posy = posy
        self.posx = posx
        self.number = Field.number
        Field.number += 1
        self.value = value
        self.oldvalue = value
        #self.color = (value,value,value)
        pygame.sprite.Sprite.__init__(self, self.groups) #THE most important line !
        self.image = pygame.Surface((Field.sidex, Field.sidey))
        self.image.fill((value,value,value))
        pygame.draw.rect(self.image,  (128,128,255), (0,0,Field.sidex, Field.sidey),1) # grid-rect around field
        self.rect = self.image.get_rect()
        
        self.rect.centerx = Field.offsetx + Field.cornerx + Field.sidex / 2 + self.posx * Field.sidex
        self.rect.centery = Field.cornery + Field.sidey / 2 + self.posy * Field.sidey
        self.black = False
        self.white = False
    
    def update(self, seconds):
        if self.value != self.oldvalue:
            self.image.fill((self.value, self.value, self.value))
            #print "changing  field" , str(self.number)
            pygame.draw.rect(self.image,  (128,128,255), (0,0,Field.sidex, Field.sidey),1) # grid-rect around field
            if self.white:
                pygame.draw.line(self.image, (0,0,0), (0,0),(Field.sidex, Field.sidey),2)
                pygame.draw.line(self.image, (0,0,0), (0,Field.sidey), (Field.sidex,0),2)
            elif self.black:
                pygame.draw.line(self.image, (255,255,255), (0,0),(Field.sidex, Field.sidey),2)
                pygame.draw.line(self.image, (255,255,255), (0,Field.sidey), (Field.sidex,0),2)
        self.oldvalue = self.value
        #print "ich werde geupdated"
    def changevalue(self,amount=0):
        if self.value > 0 and self.value < 255:
            self.value += amount
            self.value = min(255, self.value) # 0-255 only
            self.value = max(0,self.value)    # 0-255 only
            #Spark(self.rect.center, self.value)
            sparks = 4 # how many sparks
            if self.value == 0:
                self.black = True
                Field.blacksum += 1
                sparks = 10 
            elif self.value == 255:
                self.white = True
                Field.whitesum += 1
                sparks = 10
            if amount < 0:   # field becomes more black
                offset = 0  
                color = (0,255,0)  
            else:
                offset = math.pi/4.0    # field becomes more white
                color = (255,0,0)
            for x in range(sparks):
                Spark(self.rect.center,color, offset + (x+1) *(2*math.pi/sparks), sparks * 0.1)
                
    
#------------ defs ------------------


def radians_to_degrees(radians):
    return (radians / math.pi) * 180.0

def degrees_to_radians(degrees):
    return degrees * (math.pi / 180.0)

def getclassname(class_instance):
    """this function extract the class name of a class instance.
    For an instance of a XWing class, it will return 'XWing'."""
    text = str(class_instance.__class__) # like "<class '__main__.XWing'>"
    parts = text.split(".") # like ["<class '__main__","XWing'>"]
    return parts[-1][0:-2] # from the last (-1) part, take all but the last 2 chars

def elastic_collision(sprite1, sprite2):
    """elasitc collision between 2 sprites (calculated as disc's).
       The function alters the dx and dy movement vectors of both sprites,
       if both sprites have the flag .static set to False.
       If one sprite has the flag .static set to True, this sprite's 
       dx and dy vectors are not changed.
       (If both sprites have the flag .static set to True, you don't need 
        a elastic collision.)
       The sprites need the propertys:
             .mass 
             .radius
             .pos[0] # the x position
             .pos[1] # the y position
             .dx     # movement vector x
             .dy     # movement vector y
             .static # set to False (default)
       """
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
        if not sprite2.static:
            sprite2.dx -= 2 * dirx * dp 
            sprite2.dy -= 2 * diry * dp
            sprite2.rotate_toward_moving() # new heading
        if not sprite1.static:
            sprite1.dx -= 2 * dirx * cdp 
            sprite1.dy -= 2 * diry * cdp
            sprite1.rotate_toward_moving() # new heading

def write(msg="pygame is cool", fontsize = 32, color=(0,0,0)):
    myfont = pygame.font.SysFont("None", fontsize)
    mytext = myfont.render(msg, True, color)
    mytext = mytext.convert_alpha()
    return mytext        

def main():
    pygame.init()
    screen=pygame.display.set_mode((Config.width,Config.height)) 
    screenrect = screen.get_rect()
    background = pygame.Surface((screen.get_size()))
    backgroundrect = background.get_rect()
    playrect = pygame.Rect(Tank.side, Tank.side/2, Config.width - 2 * Tank.side, Config.height-Tank.side)
    uprect = pygame.Rect(Tank.side, Tank.side/2, Config.width - 2 * Tank.side, Config.height / 2 - Tank.side)
    
    background.fill((128,128,255)) # fill grey light blue:(128,128,255) 
    #pygame.draw.rect(background, (255,255,255), (0,0,Tank.side, Config.height)) # strip for left tank
    #pygame.draw.rect(background, (0,0,0), (Config.width-Tank.side,0,Tank.side, Config.height)) # strip for right tank
    background = background.convert()
    #background0 = background.copy()


    screen.blit(background, (0,0)) # delete all
    clock = pygame.time.Clock() #create pygame clock object
    mainloop = True
    FPS = Config.fps         # desired max. framerate in frames per second. 
    playtime = 0
    
    
    tankgroup = pygame.sprite.Group()
    bulletgroup = pygame.sprite.Group()
    fieldgroup = pygame.sprite.Group()
    obstaclegroup = pygame.sprite.Group()
    allgroup = pygame.sprite.LayeredUpdates()
    
    Tank._layer = 5
    Bullet._layer = 8
    Turret._layer = 6
    Field._layer = 2
    Obstacle._layer = 3
    Spark._layer = 2
    Text._layer = 4
    Energybar._layer = 2
 
    #assign default groups to each sprite class
    Tank.groups = tankgroup, allgroup
    Field.groups = allgroup, fieldgroup
    Turret.groups = allgroup
    Spark.groups = allgroup
    Bullet.groups = bulletgroup, allgroup
    Text.groups = allgroup
    Obstacle.groups = allgroup, obstaclegroup
    Energybar.groups = allgroup
    
    # ---- create Tanks ------
    #         Tank(pos, turretAngle, tankAngle)
    player1 = Tank((Tank.side/2, Config.height/2 ), 0, 90)#
    player2 = Tank((Config.width - Tank.side/2,Config.height/2),180,90)
    
    # ---- place obstacles ---
    Obstacle(Tank.side/2, Tank.side, False) # upper left horizontal
    Obstacle(Config.width - Tank.side/2, Tank.side, False) # upper right, horizontal
    #Obstacle(Config.width / 2, Tank.side/2, True) # upper border, vertical
    Obstacle(Config.width / 2, Config.height - Tank.side/2, True) #lower border, vertical
    
    #---------- fill grid with Field sprites ------------
    
    # how much space x in playfield ?
    lengthx = Config.width - 2* Tank.side
    lengthy = Config.height - 2* Tank.side
    Field.sidex = lengthx / Config.xtiles
    Field.sidey = lengthy / Config.ytiles
    #Ball.side = 2 * Field.sidex  # a Ball diameter is 2 times the length(x) of a field
    Field.cornerx = Tank.side
    Field.cornery = Tank.side
    # offset to center fields in x-axis of screen
    Field.offsetx =  (lengthx - ( Field.sidex * Config.xtiles) ) / 2
    Field.fields = Config.xtiles * Config.ytiles # amount of fields !!!!
    for y in range(Config.ytiles):
       for x in range(Config.xtiles):
           Field(x,y,128)
    # statusText
    status1 = Text((Config.width/2, 18), "SchwarzWeiss", 36 )
    score = Text((Config.width/2, 40),"%i (white player) vs. %i (black player) " % (0,0), 30)
    lefttext = Text((Config.width/2,60),"white player: press w,a,s,d + LSHIFT", 24)
    righttext = Text((Config.width/2,80),"black player: press cursor + RCTRL", 24)
    el1 = Text((65,10),"energy reserve:",24)
    ebl1 = Energybar((Config.width/4,10),player1,1)  # pos, boss, barnumber
    el2 = Text((70,40),"energy loss/gain:",24)
    el3 = Text((65,70),"energy change:",24)
    er1 = Text((Config.width-155,35),"energy:",24)
    # ---- create neutral green tanks -----
    neutralx = Config.neutraltanks * Tank.side
    spaces = Config.neutraltanks + 1 # space and tank and space
    spacex = (lengthx - neutralx) / spaces
    for neutralnumber in xrange(Config.neutraltanks):
         Tank((Tank.side + (neutralnumber+1) * spacex + (neutralnumber + 1) * Tank.side - Tank.side/2,
              Config.height/2), 90, 90)

           
    while mainloop:
        milliseconds = clock.tick(Config.fps)  # milliseconds passed since last frame
        seconds = milliseconds / 1000.0 # seconds passed since last frame (float)
        playtime += seconds
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # pygame window closed by user
                mainloop = False 
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mainloop = False 

        
        for bull in bulletgroup:  
            crashgroup = pygame.sprite.spritecollide(bull, fieldgroup, False )      #pygame.sprite.collide_circle
            for crashfield in crashgroup:
                if not bull.book.has_key(crashfield.number):
                    #if bull.boss.border == "left":
                    if bull.boss.number == 0: # left player
                        crashfield.changevalue(4)
                    #elif bull.boss.border == "right":
                    elif bull.boss.number ==1: # right player
                        crashfield.changevalue(-4)
                    bull.value -= 4
                    bull.book[crashfield.number] = True
                    #Spark(bull.pos, crashfield.value)
                    
        for tank in tankgroup:
            crashgroup = pygame.sprite.spritecollide(tank, bulletgroup, False, pygame.sprite.collide_circle) # bullet bounce from Turret
            for bouncebullet in crashgroup:
                tank.damage += 1
                if tank.number > 1: # neutral tank
                    if bouncebullet.boss.number < 2: # bullet come from player
                        tank.targetplayer = bouncebullet.boss.number
                elastic_collision(bouncebullet, tank)
                
                
            
            
        for obst in obstaclegroup:
            crashgroup = pygame.sprite.spritecollide(obst, bulletgroup, True) # kill bullets in obstacles
                    

                
        
 
        #print Field.fields, Field.whitesum , float(Field.whitesum / Field.fields)
        score.changemsg("%.1f %%  vs. %.1f %%" % (Field.whitesum *1.0 / Field.fields * 100 , Field.blacksum *1.0 / Field.fields *100 ))
        pygame.display.set_caption("FPS: %.2f press ESC to quit " % clock.get_fps())
        # ------------ textdisplays ---------------
        
        # ------------ win ------- 
        if Field.blacksum > Field.fields / 2:
            print "========================= GAME OVER ===================================="
            print "black side ist the winner"
            mainloop = False
        elif Field.whitesum > Field.fields / 2:
            print "========================= GAME OVER ===================================="
            print "white side is the winner"
            mainloop = False
        #screen.blit(background, (0,0)) # delete all
        allgroup.clear(screen, background) # funny effect if you outcomment this line
        allgroup.update(seconds)
        allgroup.draw(screen)
        pygame.display.flip() # flip the screen 30 times a second
    return 0

if __name__ == '__main__':
    main()

