schwarzweiss readme file

schwarzweiss is a German word maening "blackwhite". The schwarzweiss game is written in python (2.6) and pygame (1.9.1) and tested on Linux (Ubuntu 10.10) and Windows XP.

=== game homepage ===
http://thepythongamebook.com/en:resources:games:schwarzweiss

=== installation ===

install python2.6 from http://www.python.org for your Operation System. You can try out newer version of python at your own risk.

install pygame1.9.1 for python 2.6 from http://www.pygame.org for your Operation System. You can try out newer version of pygame at your own risk.

make sure you have the file schwarzweiss.py in your folder and in this folder the subfolder data with the soundfiles.

start the game by typing

python schwarzweiss_start.py 

or by launching it with another mehtod (double-clicking etc.)

Note for Ubuntu users:
=====================
you can install python and pygame using Software Center, synaptic or typing:
sudo apt-get install python 
sudo apt-get install python-pygame

Note for Windows users:
=======================
make sure you take python2.6 (and not pyhton2.7). make sure you install pygame correctly (inside c:\Pyhton26).
If you manage to open a terminal, you must type: 
C:\Python26\python.exe schwarzweiss_start.py
it is probably less complicated to open schwarzweiss_start.py with your python editor, or by double-clicking.
Also the readme file is not displayed correctly if you open it with notepad. Try to open it using a better text editor.

Note for Mac users:
===================
I can not test at the moment but usually if you manage to install python2.6 and pygame1.9.1 for python2.6 correctly you should be able to run the game. try double-clicking schwarzweiss.py , the MacOS should launch python or idle to start it.
Please report your findigs to:
horstjens@gmail.com
so that i can update this readme.


=== how to play ===

In the 2-player game "schwarzweiss", each player control a tank (white tank on the left border, black tank on the right border) and can move the tank up / down as well as rotate the tank turret (using keys).

Between the tanks is a big field created out of rectangular tiles (fields), each with a grey color. By shooting over those tiles, each tile will slowly change it's color to eithere black or white, depending who is shooting. 

The goal of the game is to switch more then 50% of all tiles to the color of the tank.

To make the game more interesting (and hopefully, a bit tactical), slow-moving neutral tanks roam over the playfield, reflecting all shots and shooting back.

energy management: 
  shooting, rotating and moving cost energy.
  waiting, hitting fields and hitting tanks gains energy.

Please see newest instructions, bug notices etc at the game hompepage:
http://thepythongamebook.com/en:resources:games:schwarzweiss

=== customizing ===

you can customzie the game by changing the values in the game menu or by changing values inside the class Config of the file schwarzweiss.py (inside the folder data). 


=== license ===

This game is GPL licensed and thus free to copy, distribute and modify. You can do whatever you want with it, as long as the game and the derived work remain free.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

the ezmenu from pymike is licensed under lgpl

=== author ===

Horst JENS
horstjens@spielend-programmieren.at
http://www.spielend-programmieren.at

Ezmenu form Pymike (http://pymike.aftermatheffect.com/home/)

=== download ===
you should find the latest information and download links at this site:
http://thepythongamebook.com/en:resources:games:schwarzweiss

=== support ===
I would be very pleased to hear your opinion about this game.

email: horstjen@gmail.com

You can also post your opinion about the game in ThePythonGameBook's facebook page:

https://www.facebook.com/ThePythonGameBook

If you want to send money, this game has it's own flattr button:

https://flattr.com/thing/163126/schwarzweiss-game

There is also a paypal button at the game's homepage.

==== note about reddit game jam ====
the schwarzweiss game was first developed for another gamejam in Vienna's Metalab (11/2010). Since 1-2011 the game was public on my site 
http://ThePythonGameBook.com
See the screenshots and background story at 
http://thepythongamebook.com/en:resources:games:schwarzweiss
for more information.



