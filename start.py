import os
import importlib
import time

start = True
helpGuide = ('''
Help Guide

Controls:
arrow keys: Movement (numpad for diagonal)
"q": Exit Game
"d": Switch Weapons
"f": Fire Weapon
"g": Throw Grenade

Game Play:
The goal of the game is to advance as many levels as you can while taking as little dammage as posible.
To advance to the next level move to the far right of the screen.
Pick up chests as you go marked as a "C". The chests contain useful suplies such as ammo, health, grenades and new weapons.

Back Story:
You awake one morning to find the world overun with zombies rising from graves. You grab a knife and your trusty pistol and
head out into the world to find some answers. You suspect the the zombies are rising because of a extraterrestrial force.
To find out you must push forward through increasing waves of zombies and find their source.

Note:
The larger your window size for this game the more enjoyable the experience.
''')
text = (''' 
 _____                _     _      _                       _     _   _ _                
/ _  / ___  _ __ ___ | |__ (_) ___( )__     __ _ _ __   __| |   /_\ | (_) ___ _ __  ___ 
\// / / _ \| '_ ` _ \| '_ \| |/ _ \/ __|   / _` | '_ \ / _` |  //_\\\\| | |/ _ \ '_ \/ __|
 / //\ (_) | | | | | | |_) | |  __/\__ \  | (_| | | | | (_| | /  _  \ | |  __/ | | \__ \\
/____/\___/|_| |_| |_|_.__/|_|\___||___/   \__,_|_| |_|\__,_| \_/ \_/_|_|\___|_| |_|___/
																						''')

deathText = ('''
                           _                 ___               _        
__/\__ /\_/\___  _   _    /_\  _ __ ___     /   \___  __ _  __| | __/\__
\    / \_ _/ _ \| | | |  //_\\\\| '__/ _ \   / /\ / _ \/ _` |/ _` | \    /
/_  _\  / \ (_) | |_| | /  _  \ | |  __/  / /_//  __/ (_| | (_| | /_  _\\
  \/    \_/\___/ \__,_| \_/ \_/_|  \___| /___,' \___|\__,_|\__,_|   \/  
                                                                        
''')

developerMode = False
invincibility = False

line = ''
reload = False

def refresh():
	os.system('cls' if os.name == 'nt' else "printf '\033c'")

def deathScreen():
	time.sleep(1)
	refresh()
	print(deathText)
	print('')
	print('''The harsh world has gotten the better of you.
Better luck next time.''')
	print('')
	print('Stats:')
	print('Enemies Vanquished: '+str(main.enemiesKilled))
	print('Furthest Stage: ' + str(main.difficultyLevel))
	print('Final Score: ' + str(main.score))
	print('')
	print('Press Enter To Return To The Main Menu')
	input()

while start:
	refresh()
	print(line)
	line = ''
	print(text)

	print('')
	print('Type "Help" for key bindings and how to play. Type "Quit" to exit.')
	print('Press Enter To Start The Game')
	var = input()

	if var.lower() == 'help' or var.lower() == 'h':
		refresh()
		print(helpGuide)
		print('')
		print('Press Enter To Return To Main Menu')
		input()
	elif var == '':
		refresh()
		if reload:
			main = importlib.reload(main)
		else:
			import main
		main.startGame(developerMode, invincibility)
		reload = True
		if main.playerHealth <= 0:
			deathScreen()
	elif var.lower() == 'quit' or var.lower() == 'q':
		refresh()
		start = False
	elif var.lower() == 'devel':
		developerMode = True
		line = ('Developer mode enabled.')
	elif var.lower() == 'invince':
		invincibility = True
		line = ('Invincibility enabled.')
