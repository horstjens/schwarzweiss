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
       
#    Copyright (C) 2011  Horst JENS

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.


import pygame
import random
import math
import os
import sys


#GRAD = math.pi / 180 # 2 * pi / 360   # math module needs Radiant instead of Grad








class Config(object):
    """the Config class is used to store some global game parameters"""
    fullscreen = False
    width = 1024 # pixel
    height = 600 # picel
    fps = 100  # max. framerate in frames per second
    xtiles = random.randint(8,16) # how many fields horizontal
    ytiles = random.randint(4,12) # how many fields vertical
    #title = "Esc: quit, left player: WASD, right player: Cursor"
    neutraltanks = random.randint(1,3) # number of neutral tanks
    tankxpercent = 0.4 # left tank is allowed in the left 40 % of playfield
    maxpause = 1.0 # seconds of immobilisation after turret hit
    tracktolerance = 15 # tolerance (pixel) for turning tank in corner
    barmax = 10.0 # max value for energy gain/loss bar
    bullethitpoints = 2 
    rockethitpoints = 10
    tracerdamage = 1
    bulletconvert = 10 # for how many colorpoints a field is changed when a bullet is flying over it
    tracerconvert = 1  # for how many colorpoints a field is changed when a tracer is flying over it
    #--------- energy --------
    ebasegain = 45 # energy gain per second
    ehitgain = 1
    eturrethitgain = 25 # once
    egridgain = 5 # once
    egridconvert = 300 # once
    emoveloss = 10 # per second !
    erotateloss = 200 # per second !
    ebulletloss = 300 # once per shot 
    repairloss = 1 # per second !
    etracerloss = 4
    #ehitloss = 2
    eturrethitloss = 50
    emax = 1000
    ebulletmin = 500
    etracermin = 50
    erocketlaunch = 700




class Dummysound:
    def play(self): pass


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

class Rocket(pygame.sprite.Sprite):
    """a rocket that fires only when the energy bar is full"""
    side = 70
    mass = 100
    def __init__(self, boss):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.boss = boss
        self.pos = [0.0,0.0]
        self.pos[0] = self.boss.pos[0]
        self.pos[1] = self.boss.pos[1]
        self.color = self.boss.color
        self.mass = Rocket.mass
        self.static = False
        self.dx = 0
        self.dy = 0
        if self.boss.number == 0:
            self.target = 1
            self.angle = 0
        else:
            self.target = 0
            self.angle = 180
        self.vel = 100 # velocity
        self.angle = self.boss.turretAngle
        self.image = pygame.Surface((Rocket.side, 20))
        self.image.set_colorkey((5,5,5))
        self.image.fill((5,5,5))
        pygame.draw.polygon(self.image, (0,255,0), ((Rocket.side/2,0),(Rocket.side/2+20,10),(Rocket.side/2,20))) # middle triangle
        pygame.draw.polygon(self.image, (0,255,0), ((0,0),(20,10),(0,20))) # back triangle
        pygame.draw.polygon(self.image, (0,255,0), ((Rocket.side-10, 5), (Rocket.side, 10), (Rocket.side-10,15))) # point
        pygame.draw.rect(self.image, self.color, (0,5,Rocket.side - 10, 10)) # color rect
        pygame.draw.rect(self.image, (0,255,0), (0,5,Rocket.side - 10, 10),1) # green outer rect
        
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = round(self.pos[0],0)
        self.rect.centery = round(self.pos[1],0)
        #self.lifetime = 15.0
        self.hitpoints = Config.rockethitpoints
        self.phase = 0 # first pahse fly to nord middle border, second phase aim at enemy player
        self.middletarget = Config.height / 2.0 * random.random() # aim at a point (y) between the top border and the middle of the screen
        
    def rotate_toward_moving(self):
        pass # the rocket is guided by itself and not by elastic_collision
        
    def update(self, seconds):
        #self.lifetime -= seconds
        #if self.lifetime < 0:
        #    self.kill()
        #if self.pos[1] <= Tank.side:
        #    self.phase = 1 # aim at enemy player if reaching north border
        if self.boss.number == 0: # left player, rocket flys from west to east
           if self.pos[0] >= Config.width / 2:
               self.phase = 1
        elif self.boss.number == 1:
            if self.pos[0] <= Config.width /2:
               self.phase = 1
        if self.hitpoints <= 0:
            self.kill()
        if self.phase == 0: # aim at middle north border
            deltax = Config.width / 2 - self.pos[0]
            #deltay = Tank.side - self.pos[1]
            deltay = self.middletarget - self.pos[1]
        else:  # aim at player
            deltax = Tank.book[self.target].pos[0] - self.pos[0]
            deltay = Tank.book[self.target].pos[1] - self.pos[1]
        angle =   math.atan2(-deltax, -deltay)/math.pi*180.0            
        diff = (angle - self.angle - 90) %360 #reset at 360
        if diff < 180:
            self.angle -= 1
        elif diff > 180:
            self.angle += 1
        
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.rect = self.image.get_rect()
        self.dx = math.cos(degrees_to_radians(self.angle)) * self.vel
        self.dy = math.sin(degrees_to_radians(-self.angle)) * self.vel
        
        
        self.pos[0] += self.dx * seconds
        self.pos[1] += self.dy * seconds
        self.rect.centerx = round(self.pos[0],0)
        self.rect.centery = round(self.pos[1],0)
        
        
class Obstacle(pygame.sprite.Sprite):
    """ a rectangular, bulletproof obstacle"""
    def __init__(self, x,y, vertical = True, bounce = False):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.vertical = vertical
        self.bounce = bounce
        if self.vertical:
            self.image = pygame.Surface((10,Tank.side))
        else:
            self.image = pygame.Surface((Tank.side, 10))
        self.red = 128
        self.green = 128
        self.blue = 0
        self.dr = 1 # changing of red color
        self.image.fill((self.red, self.green, self.blue))
        self.image.convert()
        self.rect = self.image.get_rect()
        self.pos = [0,0]
        self.dx = 0
        self.dy = 0
        if self.bounce:
            if self.vertical:
                self.dx = 0
                self.dy = random.choice((-1,1))
            else:
                self.dy = 0
                self.dx = random.choice((-1,1))
        self.vec = random.randint(25,75)
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
        if self.bounce:
            self.pos[0] += self.dx * self.vec * seconds
            self.pos[1] += self.dy * self.vec * seconds
            if self.vertical: # bounce up / down
                if self.pos[1] < int(Tank.side*1.5):
                    self.pos[1] = int(Tank.side*1.5)
                    self.dy *= -1
                elif self.pos[1] > Config.height - int(Tank.side*1.5):
                    self.pos[1] = Config.height - int(Tank.side*1.5)
                    self.dy *= -1
            else: # bounce left / right
                if self.pos[0] < int(Tank.side*1.5):
                    self.pos[0] = int(Tank.side*1.5)
                    self.dx *= -1
                elif self.pos[0] > Config.width - int(Tank.side * 1.5):
                    self.pos[0] = Config.width - int(Tank.side * 1.5)
                    self.dx *= -1
            self.rect.centerx = round(self.pos[0],0)
            self.rect.centery = round(self.pos[1],0)
                
        
class Bar(pygame.sprite.Sprite):
       """a bar to indicate energy loss or gain
          barnumber:
          1 = energy reserve
          2 = gain/loss
          3 = pause
          """
       length = Config.width / 4
       height = 20
       def __init__(self, pos, boss, barnumber):
           pygame.sprite.Sprite.__init__(self, self.groups)
           self.boss = boss
           self.pos = [0.0,0.0]
           self.pos[0] = pos[0]
           self.pos[1] = pos[1]
           self.barnumber = barnumber
           self.image = pygame.Surface((Bar.length,Bar.height))
           self.image.set_colorkey((0,0,0))
           self.rect = self.image.get_rect()
           self.rect.centerx = round(self.pos[0],0)
           self.rect.centery = round(self.pos[1],0)
           self.bulletx = Bar.length * (Config.ebulletloss * 1.0 / Config.emax)
           self.movex = Bar.length * (Config.emoveloss * 1.0 / Config.emax)
           if self.barnumber == 1: # energy reserve:
               self.red = 255
               self.green = 255
               self.blue = 0
           elif self.barnumber == 3: # pausebar
               self.red = 255
               self.green= 0
               self.blue = 255
       
       def update(self, seconds):
           if self.barnumber == 1: # energy reserve
               percent = self.boss.energy * 1.0 / Config.emax
               self.image.fill((0,0,0,)) # fill transparent
               energyx = int(percent * Bar.length)
               pygame.draw.rect(self.image, (self.red, self.green, self.blue), (0,0,energyx,Bar.height))
               pygame.draw.rect(self.image, (255,255,255),(0,0,Bar.length, Bar.height),1) # border
               # dark line at minimum energy for bullet
               pygame.draw.line(self.image, (10,10,10),(self.bulletx,0),(self.bulletx,Bar.height),1) 
               # dark line at minimum for movement
               pygame.draw.line(self.image, (10,10,10),(self.movex,0),(self.movex,Bar.height),1) 
           
           elif self.barnumber == 2: # plus minus bar
               #print "bar..... ", self.boss.eplus, self.boss.eminus
               self.image.fill((0,0,0)) # fill transparent
               plus = min(self.boss.eplussum, Config.barmax) # cap gain at barmax
               self.boss.eplussum = 0 # reset after use
               pluspercent = plus * 1.0 / Config.barmax
               plusx = int(pluspercent * (Bar.length / 2.0))
               pygame.draw.rect( self.image, (0,255,0), (Bar.length/2, 0, plusx, Bar.height)) # green gain
               minus = min(self.boss.eminussum, Config.barmax) # cap loss at barmax
               self.boss.eminussum = 0 # reset after use
               minuspercent = minus * 1.0 / Config.barmax
               minusx = int(minuspercent * (minuspercent * (Bar.length / 2.0)))
               pygame.draw.rect( self.image, (255,0,0), (Bar.length / 2 - minusx, 0 , minusx, Bar.height)) # red loss
               pygame.draw.line(self.image, (10,10,10),(Bar.length / 2, 0), (Bar.length/2, Bar.height),1) # black middle line
               pygame.draw.rect(self.image, (255,255,255),(0,0,Bar.length, Bar.height),1) # border
           
           elif self.barnumber == 3: # pausebar
               percent = min(5,self.boss.pause) * 1.0 / 5 # 5 seconds max pause for bar
               pausex = int(Bar.length * 1.0 * percent)
               self.image.fill((0,0,0)) # fill transparent
               pygame.draw.rect(self.image, (self.red,self.green,self.blue), (0,0,pausex,Bar.height))
               pygame.draw.rect(self.image, (255,255,255),(0,0,Bar.length, Bar.height),1) # border
               
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
        self.hitpoints = Config.bullethitpoints
        self.color = self.boss.color
        self.calculate_heading() # !!!!!!!!!!!!!!!!!!!
        self.book = {}
        self.value = 255
        self.dx += self.boss.dx
        self.maxlifetime = Bullet.maxlifetime
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
        pygame.draw.rect(image, self.color, (0,0,int(Bullet.side * 1.5), Bullet.side)) # rectangle 1.5 length
        pygame.draw.circle(image, self.color, (int(self.side *1.5) ,self.side/2), self.side/2) #  circle
        pygame.draw.rect(image, (255,0,0), (0,0,int(Bullet.side * 1.5), Bullet.side),3) # rectangle 1.5 length
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
        if self.hitpoints <= 0:
            self.kill()
        self.lifetime += seconds
        if self.lifetime > self.maxlifetime:
            self.kill()
        # ------ calculate movement --------
        self.pos[0] += self.dx * seconds
        self.pos[1] += self.dy * seconds
        # ----- kill if out of screen
        if self.pos[0] < 0:
            self.kill()
        elif self.pos[0] > Config.width:
            self.kill()
        # bounce only from  upper  border
        #if self.pos[1] < 0 or self.pos[1] > Config.height:
        if  self.pos[1] < 0:
            #print self.angle
            self.pos[1] = max(0, self.pos[1])
            self.pos[1] = min(Config.height, self.pos[1])
            self.dy *= -1
            self.rotate_toward_moving()            
        elif self.pos[1] > Config.height:
            self.kill()
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
    maxlifetime = 1.5 # seconds
    def __init__(self, boss, turret=False):
        self.turret = turret
        Bullet.__init__(self,boss ) # this line is important 
        self.value = 16
        self.maxlifetime = Tracer.maxlifetime
        self.mass = Tracer.mass
        
    def calculate_heading(self):
        """overwriting the method because there are some differences 
           between a tracer and a main gun bullet"""
        self.radius = Tracer.side / 2 # for collision detection
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
        if self.turret:    # turret mg
            self.dx = math.cos(degrees_to_radians(self.boss.turretAngle)) * self.vel
            self.dy = math.sin(degrees_to_radians(-self.boss.turretAngle)) * self.vel
        else:    # bow mg
            self.dx = math.cos(degrees_to_radians(self.boss.tankAngle)) * self.vel
            self.dy = math.sin(degrees_to_radians(-self.boss.tankAngle)) * self.vel

    def calculate_origin(self):
        """overwriting because another point of origin is needed"""
        if self.turret:  # - spawn bullet at end of machine gun muzzle (bow or turret)
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
    book = {} # a book of tanks to store all tanks
    number = 0 # each tank gets his own number
    # keys for tank control, expand if you need more tanks
    #          player1,        player2    etc
    firekey = (pygame.K_LSHIFT, pygame.K_RCTRL)
    turretLeftkey = (pygame.K_a, pygame.K_LEFT)
    turretRightkey = (pygame.K_d, pygame.K_RIGHT)
    forwardkey = (pygame.K_w, pygame.K_UP)
    backwardkey = (pygame.K_s, pygame.K_DOWN)
    color = ((255,255,255), (0,0,0))
          
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
        self.mgammo = 500 # machinge gun
        self.energy = 550 # a bit more than 50%
        self.eplus = 0
        self.eminus = 0
        self.eminussum = 0
        self.eplussum = 0
        self.pause = 0.0 # after a turret hit, the tank is immobile for some time        
        self.turretAngle = turretangle #turret facing
        self.tankAngle = tankangle # tank facing

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
            self.color = (0,200,0) # dark green
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
        self.mg2firestatus = 0.0 # time until turret mg can fire again
        self.turndirection = 0    # for turret
        self.tankturndirection = 0
        self.movespeed = Tank.movespeed
        self.turretTurnSpeed = Tank.turretTurnSpeed
        self.tankTurnSpeed = Tank.tankTurnSpeed
        Turret(self) # create a Turret for this tank
        if self.number > 1: # neutral tanks
            self.dx = 0   # make speed between 1/4 and 1/2 of player speed with random direction
            self.dy = (Tank.movespeed * 0.25 + random.random() * Tank.movespeed * 0.25) * random.choice((-1,1))
            self.targetplayer = random.choice((0,1))
            
    def update(self, seconds):   # no need for seconds but the other sprites need it
        if self.firestatus > 0:
            self.firestatus -= seconds # cannon will soon be ready again
            if self.firestatus <0:
                self.firestatus = 0 #avoid negative numbers
        if self.pause > 0:  # immoble, pause ?
            self.pause -= seconds
            self.eminus += Config.repairloss
            if self.pause < 0:
                self.pause = 0

        if self.number > 1: # +-------- neutral tanks ------------
             #if self.pause >= Config.maxpause / 2:
                # do not rotate turret if hit by shell
             self.aim_at_player(self.targetplayer)
             if self.pause > 0:
                 self.forward = 0
             else:
                 self.forward = 1
             self.pos[0] += self.dx * seconds * self.forward
             self.pos[1] += self.dy * seconds * self.forward
        else: # ------------------------player tanks ------------------
            #-------- reloading, firestatus----------
            if self.mg2firestatus > 0:
                self.mg2firestatus -= seconds # turret mg will soon be ready again
                self.mg2firestatus = max(0, self.mg2firestatus)
            # ------------ keyboard --------------
            pressedkeys = pygame.key.get_pressed()
            # -------- turret manual rotate ----------
            self.turndirection = 0    #  left / right turret rotation
            if self.number > 1:   # only for tank2
                self.aim_at_player()       # default aim at player0
            else:
                if pressedkeys[self.turretLeftkey]:
                    self.turndirection += 1
                    self.eminus += Config.erotateloss * seconds
                if pressedkeys[self.turretRightkey]:
                    self.turndirection -= 1
                    self.eminus += Config.erotateloss * seconds
            #---------- tank rotation ---------
            self.tankturndirection = 0 # reset left/right rotation
            # ---------- fire cannon -----------
            #if (self.firestatus ==0) and (self.ammo > 0):
            if (self.firestatus ==0) :
                if pressedkeys[self.firekey]:
                    if (self.energy > Config.ebulletloss):
                        self.firestatus = Tank.recoiltime # seconds until tank can fire again
                        self.eminus += Config.ebulletloss
                        if self.number == 0:
                            Config.schuss2.play()
                        elif self.number == 1:
                            Config.schuss3.play()
                        Bullet(self) 
                    elif (self.energy > Config.etracerloss) and self.mg2firestatus == 0:
                        self.mg2firestatus = Tank.mgrecoiltime
                        self.eminus += Config.etracerloss
                        Config.mg1.play()
                        Tracer(self, True)

            self.dx = 0
            self.dy = 0
            self.forward = 0 # movement calculator
            if pressedkeys[self.forwardkey] and self.pause == 0 and  self.energy > Config.emoveloss:
                self.forward += 1
            if pressedkeys[self.backwardkey] and self.pause == 0 and self.energy > Config.emoveloss:
                self.forward -= 1
            # if both are pressed togehter, self.forward becomes 0
            if self.forward == 1:
                self.eminus += Config.emoveloss * seconds
                self.dx =  math.cos(degrees_to_radians(self.tankAngle)) * self.movespeed
                self.dy =  -math.sin(degrees_to_radians(self.tankAngle)) * self.movespeed
            if self.forward == -1:
                self.eminus += Config.emoveloss * seconds
                self.dx =  -math.cos(degrees_to_radians(self.tankAngle)) * self.movespeed
                self.dy =  math.sin(degrees_to_radians(self.tankAngle)) * self.movespeed
            # ----- energy sum ---
            self.energy += self.eplus
            self.energy -= self.eminus
            # --- automatic rocket launch if 100% energy ---
            
            self.eplussum = self.eplus
            self.eminussum = self.eminus
            self.eplus = 0
            self.eminus = 0
            #print " === ", self.eminussum, self.eminus
            self.eplus += Config.ebasegain * seconds
            if self.energy < 0:
                self.energy = 0
            elif self.energy > Config.emax:
                self.energy = Config.emax
            # --- automatic rocket launch if 100% energy ---
            if self.energy == Config.emax:
                self.energy -= Config.erocketlaunch
                Rocket(self)
            # ------------- check border collision ---------------------
            self.pos[0] += self.dx * seconds
            self.pos[1] += self.dy * seconds
        # ---- check norht / south border. rotate tank if touching border and moving
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
            Config.schuss1.play()
            Bullet(self)
            if self.targetplayer == 0:
                self.targetplayer = 1
            else:
                self.targetplayer = 0
        elif diff > 180:
              #if self.pause <= Config.maxpause / 2:
                    self.turndirection = 1
        else:
              #if self.pause <= Config.maxpause / 2:
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
                Config.convert1.play()
                Field.blacksum += 1
                sparks = 10 
                Tank.book[1].eplus += Config.egridconvert # player1
            elif self.value == 255:
                self.white = True
                Config.convert2.play()
                Field.whitesum += 1
                sparks = 10
                Tank.book[0].eplus += Config.egridconvert # player0
            if amount < 0:   # field becomes more black
                offset = 0  
                color = (0,255,0) 
                Tank.book[1].eplus += Config.egridgain 
            else:
                offset = math.pi/4.0    # field becomes more white
                color = (255,0,0)
                Tank.book[0].eplus += Config.egridgain
            for x in range(sparks):
                Spark(self.rect.center,color, offset + (x+1) *(2*math.pi/sparks), sparks * 0.1)
                
#------------ defs ------------------


def load_sound(file):
    if not pygame.mixer: 
        return Dummysound()
    file = os.path.join('data', file)
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print 'Warning, unable to load,', file
    return Dummysound()

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




def game(greentanks=3, fieldsx=16, fieldsy=8, x=1024,y=800):
    Config.neutraltanks = greentanks
    Config.xtiles = fieldsx
    Config.ytiles = fieldsy
    Config.width = x
    Config.height = y
    
    pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
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
    
    #--sounds--
    Config.convert1 = load_sound('blip1.ogg')  #load sound
    Config.convert2 = load_sound("blip2.ogg")
    Config.convert3 = load_sound("convert1.ogg")
    Config.convert4 = load_sound("convert2.ogg")
    Config.explo1 = load_sound("explo3.ogg")
    Config.explo2 = load_sound("explo4.ogg")
    Config.explo3 = load_sound("explo5.ogg")
    Config.mg1 = load_sound("mg1.ogg")
    Config.slurp = load_sound("hit2.ogg")
    Config.schuss1 = load_sound("schuss1.ogg")
    Config.schuss2 = load_sound("schuss2.ogg")
    Config.schuss3 = load_sound("schuss3.ogg")
    Config.gameover = load_sound("gameover.ogg")
    Config.vampir1 = load_sound("vampir1.ogg")



    screen.blit(background, (0,0)) # delete all
    clock = pygame.time.Clock() #create pygame clock object
    mainloop = True
    FPS = Config.fps         # desired max. framerate in frames per second. 
    playtime = 0
    
    tankgroup = pygame.sprite.Group()
    bulletgroup = pygame.sprite.Group()
    convertgroup = pygame.sprite.Group() # Tracer and bullets
    fieldgroup = pygame.sprite.Group()
    obstaclegroup = pygame.sprite.Group()
    rocketgroup = pygame.sprite.Group()
    tracergroup = pygame.sprite.Group()
    allgroup = pygame.sprite.LayeredUpdates()
    
    
    Tank._layer = 5
    Bullet._layer = 8
    Turret._layer = 7
    Field._layer = 2
    Obstacle._layer = 6
    Spark._layer = 2
    Text._layer = 4
    Bar._layer = 2
    Rocket._layer = 9
 
    #assign default groups to each sprite class
    Tank.groups = tankgroup, allgroup
    Field.groups = allgroup, fieldgroup
    Turret.groups = allgroup
    Spark.groups = allgroup
    Tracer.groups = allgroup, tracergroup, convertgroup
    Bullet.groups = bulletgroup, allgroup, convertgroup
    Text.groups = allgroup
    Obstacle.groups = allgroup, obstaclegroup
    Bar.groups = allgroup
    Rocket.groups = allgroup, rocketgroup
    
    # ---- create Tanks ------
    #         Tank(pos, turretAngle, tankAngle)
    # !! if you out-comment the next 2 lines, try starting the game twice via the menu...second thime you will see some strange effect
    Tank.book = {}
    Tank.number = 0
    player1 = Tank((Tank.side/2, Config.height/2 ), 0, 90)#
    player2 = Tank((Config.width - Tank.side/2,Config.height/2),180,90)
    
    # ---- place obstacles ---
    Obstacle(Tank.side/2, Tank.side, False) # upper left horizontal
    Obstacle(Config.width - Tank.side/2, Tank.side, False) # upper right, horizontal
    #Obstacle(Config.width / 2, Tank.side/2, True) # upper border, vertical
    Obstacle(Config.width / 2, Config.height - Tank.side/2, True) #lower border, vertical
    #Obstacle(Config.width/ 2 , Config.height - Tank.side, False) # lower border, center, horizontal
    Obstacle(Config.width/ 2 - Tank.side/2, Config.height - Tank.side, False) # lower border, left of center, horizontal
    Obstacle(Config.width/ 2 + Tank.side/2, Config.height - Tank.side, False) # lower border, left of center, horizontal
    # sliding obstacles
    Obstacle(Config.width / 2 , Config.height - Tank.side , False, True) # horizontal sliding
    #Obstacle(Config.width / 2 + 100, Config.height - Tank.side , False, True)
    Obstacle(Config.width / 2, Config.height / 2, True, True) # vertical sliding
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
    lefttext = Text((Config.width/4,10),"press w,a,s,d + LSHIFT", 24)
    righttext = Text((Config.width - 250,10),"press cursor + RCTRL", 24)
    el0 = Text((45,10),"Energy",24)  #-------------- left player
    el1 = Text((45,30),"reserve:",24)
    ebl1 = Bar((Config.width/4,30),player1,1)  # reserve bar. pos, boss, barnumber
    el2 = Text((50,50),"+ / -:",24)
    ebl2 = Bar((Config.width/4, 50), player1, 2) # +/- bar
    el4 = Text((50,70),"immobile: %.1f" % player1.pause,24)
    pb1  = Bar((Config.width/4,70),player1,3) # pause bar
    
    er0 = Text((Config.width  - 45,10),"Energy",24) #-------------- right player
    er1 = Text((Config.width -  45,30),"reserve",24)
    ebr1 = Bar((Config.width - Config.width/4,30),player2,1)  # reserve bar. pos, boss, barnumber
    er2 = Text((Config.width - 50,50),"+ / -:",24)
    ebr2 = Bar((Config.width - Config.width/4, 50), player2, 2) # +/- bar
    er4 = Text((Config.width - 50,70),"immobile: %.1f sec" % player2.pause,24)
    pbr  = Bar((Config.width - Config.width/4,70),player2,3) # pause bar
    msg = "quit by user" # leace msg
    # ---- create neutral green tanks -----
    neutralx = Config.neutraltanks * Tank.side
    spaces = Config.neutraltanks + 1 # space and tank and space
    spacex = (lengthx - neutralx) / spaces
    for neutralnumber in xrange(Config.neutraltanks):
         Tank((Tank.side + (neutralnumber+1) * spacex + (neutralnumber + 1) * Tank.side - Tank.side/2,
              Config.height/2), 90, 90)

    print "starting mainloop", mainloop       
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
                #if event.key == pygame.K_r:
                #    Rocket(player1)
                #if event.key == pygame.K_t:
                #    Rocket(player2)

        for tracy in tracergroup: # tracer shot bullet down ?
            crashgroup = pygame.sprite.spritecollide(tracy, bulletgroup, False, pygame.sprite.collide_circle) 
            for hitbullet in crashgroup:
                if hitbullet.boss.number != tracy.boss.number:
                    hitbullet.hitpoints -= Config.tracerdamage
                    elastic_collision(hitbullet, tracy)
                    tracy.kill()
            crashgroup = pygame.sprite.spritecollide(tracy, rocketgroup, False)
            for hitrocket in crashgroup:
                if hitrocket.boss.number != tracy.boss.number:
                    hitrocket.hitpoints -= Config.tracerdamage
                    if hitrocket.hitpoints < 1: # energy win for shooting down rocket
                        Config.explo3.play()
                        tracy.boss.energy += Config.erocketlaunch * 0.75
                        for r in range(10): # 360° arc of sparks 
                            Spark(hitrocket.pos, hitrocket.boss.color, r * (2 * math.pi) / 10.0 , 0.7)
                    #elastic_collision(hitrocket, tracy)
                    tracy.kill()

               
                    

        for bull in convertgroup:  
            crashgroup = pygame.sprite.spritecollide(bull, fieldgroup, False )      #pygame.sprite.collide_circle
            for crashfield in crashgroup:
                if not bull.book.has_key(crashfield.number):
                    if getclassname(bull) == "Bullet":
                        convert_value = Config.bulletconvert
                    elif getclassname(bull) == "Tracer":
                        convert_value = Config.tracerconvert
                    else:
                        convert_value = 0
                        print "error, unknow bullet"
                    #if bull.boss.border == "left":
                    if bull.boss.number == 0: # left player
                        crashfield.changevalue(convert_value)
                    #elif bull.boss.border == "right":
                    elif bull.boss.number ==1: # right player
                        crashfield.changevalue(-1 * convert_value)
                    bull.value -= 4
                    bull.book[crashfield.number] = True
                    #Spark(bull.pos, crashfield.value)
                    
        for tank in tankgroup:
            crashgroup = pygame.sprite.spritecollide(tank, bulletgroup, False, pygame.sprite.collide_circle) # bullet bounce from Turret
            for bouncebullet in crashgroup:
                if tank.number != bouncebullet.boss.number:
                    tank.damage += 1 # damage model is not coded yet
                    tank.pause += Config.maxpause # tank will become immobile after a direct hit.
                if tank.number > 1: # neutral tank
                    if bouncebullet.boss.number < 2: # bullet come from player
                        Config.explo3.play()
                        tank.targetplayer = bouncebullet.boss.number
                        bouncebullet.boss.eplus += Config.eturrethitgain
                elif tank.number == 1 and bouncebullet.boss.number == 0:
                    Config.explo2.play()
                    player1.eplus += Config.eturrethitgain
                    player2.eminus += Config.eturrethitloss
                elif tank.number == 0 and bouncebullet.boss.number == 1:
                    Config.explo1.play()
                    player2.eplus += Config.eturrethitgain
                    player1.eminus += Config.eturrethitloss
                elif tank.number < 2 and bouncebullet.boss.number > 1:
                    Config.explo3.play()
                    tank.eminus += Config.eturrethitloss
                elastic_collision(bouncebullet, tank)
        
        for rocket in rocketgroup:
            crashgroup = pygame.sprite.spritecollide(rocket, tankgroup, False, pygame.sprite.collide_circle)
            for crashtank in crashgroup:
                if crashtank.number != rocket.boss.number and crashtank.number <2:
                    if rocket.boss.number == 0: # player1 has scored a hit
                        Config.vampir1.play()
                        player1.energy += player2.energy
                        player2.energy = 0
                    else: # player2 has scored a hit
                        Config.vampir1.play() # need to add another vampir sound
                        player2.energy += player1.energy
                        player1.energy = 0
                    rocket.kill()
            
        for obst in obstaclegroup: # kill bullets in obstacles
            crashgroup = pygame.sprite.spritecollide(obst, convertgroup, False) 
            for slurpbullet in crashgroup:
                if slurpbullet.boss.number < 2: # only slurp for player bullets
                    Config.slurp.play()
                slurpbullet.kill()
                    
        score.changemsg("%.1f %%  vs. %.1f %%" % (Field.whitesum *1.0 / Field.fields * 100 , Field.blacksum *1.0 / Field.fields *100 ))
        el4.changemsg("immobile: %.1f" % player1.pause)
        er4.changemsg("immobile: %.1f" % player2.pause)
        pygame.display.set_caption("FPS: %.2f press ESC to quit " % clock.get_fps())
        # ------------ textdisplays ---------------
        
        # ------------ win ------- 
        if Field.blacksum > Field.fields / 2:
            msg = "black player wins (%.1f %% vs %.1f %%)" % (Field.blacksum *1.0 / Field.fields * 100 , Field.whitesum *1.0 / Field.fields *100 )
            mainloop = False
        elif Field.whitesum > Field.fields / 2:
            msg=  "white player wins (%.1f %% vs %.1f %%)" % (Field.whitesum *1.0 / Field.fields * 100 , Field.blacksum *1.0 / Field.fields *100 )
            mainloop = False
        allgroup.clear(screen, background) # funny effect if you outcomment this line
        allgroup.update(seconds)
        allgroup.draw(screen)
        pygame.display.flip() # flip the screen 30 times a second
    #pygame.quit()
    # kill all sprites:
    for thing in allgroup:
        thing.kill()
    return msg
    


        
if __name__ == '__main__':
    game()
    #menu()
    #print game()

