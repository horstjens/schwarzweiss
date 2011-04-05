#! /usr/bin/env python
# this game menu will start the schwarzweiss game. please make sure an Arial font is installed

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


# Ezmenu from Pymike
#########################################################################
#This is a simple demo for the EzMeNu library. This is obviously released
#to the public domain!
#########################################################################
#If you have any questions email me at <pymike93@gmail.com>
#Cheers! -pymike
#########################################################################

#import modules
#import sys
import pygame
import os
from data import ezmenu
from data import schwarzweiss


class Config(object):
    #geraet = "Joystick"
    greentanks = 3
    fieldsx = 16
    fieldsy = 8
    resolution = (1024,800)
    menu = None
    menuloop = True
    result = "no game played yet"
   
    
    
def makemenu(pos=0):
    """pos is the current menuitem"""
    Config.menu = ezmenu.EzMenu(
        ["Play a new game", option1],
        ["# of neutral (green) tanks: %i" % Config.greentanks, lambda: option2(Config.greentanks)],
        ["# of fields (x-axis): %i " % Config.fieldsx , lambda: option3(Config.fieldsx)],
        ["# of fields (y-axis): %i " % Config.fieldsy , lambda: option4(Config.fieldsy)],
        ["screen resolution: %i,%i" % (Config.resolution[0], Config.resolution[1]), lambda: option5(Config.resolution)],
        ["Quit Game", option6])
    
    Config.menu.center_at(320, 240)

    #Set the menu font (default is the pygame font)
    Config.menu.set_font(pygame.font.SysFont("Arial", 32))

    #Set the highlight color to green (default is red)
    Config.menu.set_highlight_color((255, 255, 0))

    #Set the normal color to white (default is black)
    Config.menu.set_normal_color((255, 255, 255))
    Config.menu.option = pos       

#Functions called when an option is selected
def option1():
    print "starting game with ", Config.resolution
    Config.result =  schwarzweiss.game(Config.greentanks, Config.fieldsx, Config.fieldsy, Config.resolution[0], Config.resolution[1])
    #from data import schwarzweiss # import again to avoid strange bug
    #if result == "quit by user":
    #    Config.menuloop = False
    screen = pygame.display.set_mode((640, 480))
    
    
def option2(argument):
    #print "Options > %s" % argument
    print "number of green tanks: ", argument
    if argument == 1:
        Config.greentanks = 2
    elif argument == 2:
        Config.greentanks = 3
    elif argument == 3:
        Config.greentanks = 4
    else:
        Config.greentanks = 1
    makemenu(1)
        
def option3(argument):
    print "number of fields x-axis %i" % argument
    #global geraet
    if argument == 4:
        Config.fieldsx = 8
    elif argument == 8:
        Config.fieldsx = 16
    elif argument == 16:
        Config.fieldsx = 32
    elif argument == 32:
        Config.fieldsx = 64
    else:
        Config.fieldsx = 4
    makemenu(2)

def option4(argument):
    print "number of fields y-axis %i" % argument
    #global geraet
    if argument == 2:
        Config.fieldsy = 4
    elif argument == 4:
        Config.fieldsy = 8
    elif argument == 8:
        Config.fieldsy = 16
    elif argument == 16:
        Config.fieldsy = 32
    else:
        Config.fieldsy = 2
    makemenu(3)

    
def option5(argument):
    print "resolution: %i,%i" % (argument[0], argument[1])
    if argument == (320,200):
        Config.resolution = (640,480)
    elif argument == (640,480):
        Config.resolution = (800,600)
    elif argument == (800,600):
        Config.resolution = (1024,800)
    elif argument == (1024,800):
        Config.resolution = (1280,960)
    else:
        Config.resolution = (320,200)
    makemenu(4)
    
def option6():
    Config.menuloop = False
    #pygame.quit()
    #print "nun kommt der sys.exit"
    #sys.exit()
    

#Main script
def main():

    #Set up pygame
    pygame.init()
    pygame.display.set_caption("EzMeNu Example")
    screen = pygame.display.set_mode((640,480))
    background = pygame.image.load(os.path.join("data", "menupic.png"))
    screen.blit(background, (0,0))
    makemenu(0)
    while Config.menuloop:
        pygame.display.set_caption("last game result: %s" % Config.result)
        #Get all the events called
        events = pygame.event.get()

        #...and update the menu which needs access to those events
        Config.menu.update(events)

  
        #Let's quit when the Quit button is pressed
        for e in events:
            if e.type == pygame.QUIT:
                Config.menuloop = False
                
            elif e.type == pygame.KEYDOWN:
                #print "keypress"
                if e.key == pygame.K_ESCAPE:
                     Config.menuloop = False
                     
        #Draw the scene!
        #screen.fill((0, 0, 255))
        screen.blit(background, (0,0))
        Config.menu.draw(screen)
        pygame.display.flip()
    # end of menuloop 
    #pygame.quit()
    #sys.exit()
    return                

#Run the script if executed
if __name__ == "__main__":
    main()
