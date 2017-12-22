import time
import curses
import random
import math

stdscr = curses.initscr()
curses.start_color()
stdscr.nodelay(1)
#Colors
curses.init_color(30, 165, 42, 42) #Brown
curses.init_color(20, 0, 0, 0) #Pure Black
#Color Pairs
curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK) #Player
curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK) #Zombies
curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK) #Aliens
curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_GREEN) #Gravestones Active
curses.init_pair(5, curses.COLOR_WHITE, 30) #Gravestones Dug Up
curses.init_pair(6, 20, curses.COLOR_BLACK) #Bullet Color
curses.init_pair(7, curses.COLOR_RED, curses.COLOR_WHITE) #Health Packs
curses.init_pair(8, 20, curses.COLOR_RED)
curses.init_pair(9, 30, curses.COLOR_BLACK) #Health Packs
GameRunning = True
maxX = 0
maxY = 0
maxY, maxX = stdscr.getmaxyx()
playerX = 1
playerY = 1
playerLastY = 1
playerLastX = 1
nullObjectsX = []
nullObjectsY = []
difficultyLevel = 0

#Developer Vars
devel = False
noKill = False

#Stats
enemiesKilled = 0
score = 0
stage = 0

#Grenade Vars
grenadeActive = False
grenades = 0
grenadeDirX = 0
grenadeDirY = 0
grenadeX = 0
grenadeY = 0
grenadeTick = 0
grenadeType = "Frag"

#Weapon Vars
weaponType = "Pistol"
fireRate = 5
maximumBulletTravel = 30
bulletTexture = ['-', '|', '\\', '/']
weaponClass = "gun"
ammoConsumption = 1
ammo = 25
weaponDammage = 50
weaponAccuracy = 4
#: texture, weaponClass, fireDistance, ammoConsumptionPerShot, fireRateInTicks, weaponMaxDammage, weaponAccuracy
# Texture map for mele: list of posible textures chosen randomly, Texture map for guns: horrizontal, virtical, upToLeft, upToRight
weaponsCatalog = {'Combat Knife': [['/', '\\'], 'mele', 2, 0, 1, 50, 1], 'Katana': [['/', '\\'], 'mele', 3, 0, 2, 75, 1], 'Spear': [['/', '\\'], 'mele', 4, 0, 5, 75, 1], 'Pistol': [['-', '|', '\\', '/'], 'gun', 30, 1, 5, 50, 4], 'Assault Rifle': [['-', '|', '\\', '/'], 'gun', 30, 3, 2, 100, 3], 'Sniper': [['-', '|', '\\', '/'], 'gun', 1000, 3, 20, 1000, 1], 'Shotgun': [['-', '|', '\\', '/'], 'gun', 10, 3, 10, 200, 6], 'SMG': [['-', '|', '\\', '/'], 'gun', 20, 1, 1, 25, 3]}


inventorySpace = 0
weaponInventory = ['Pistol', 'Combat Knife']

#Player Vars
playerXSpeed = 0
playerYSpeed = 0

#Player Stats
playerHealth = 100
playerArmor = 0

#View Vars
currentWallData = {}

#Zombie Vars
zombies = []
zombieRemovalNeeded = False

#Zombie Stats
zombieDammage = 5
zombieTexture = 'z'
zombieColor = 2
zombieBaseHealth = 100
graveColorDug = 5
graveColorNew = 4

#Spawn Type Vars
cryptSpawnPoints = [[-1, 5], [-1, 6], [-1, 7], [5, 5], [5, 6], [5, 7]]
zombieSpawns = []

#Item VarsbulletY
drops = ['Medkit', 'Ammo', 'Grenades']
itemsLocation = {}

#Texture Vars
cryptTexture = ['----+++----', '|##__|__##|', '|####|####|', '|####|####|', '----+++----']
graveTexture = 't'
graveTextureDug = 't'

def initCurses():
	curses.noecho()
	curses.cbreak()
	stdscr.keypad(True)
	curses.curs_set(0)

def stopCurses():
	curses.nocbreak()
	stdscr.keypad(False)
	curses.curs_set(1)
	curses.echo()
	curses.endwin()

def drawBorder():
	global tick
	#draws top
	stdscr.addstr(0, 0, (" " * maxX), curses.A_REVERSE)
	#draws bottom
	stdscr.addstr((maxY - 2), 0, (" " * maxX), curses.A_REVERSE)
	i = 1
	while i < (maxY - 1):
		stdscr.addstr(i, 0, " ", curses.A_REVERSE)

		stdscr.addstr(i, (maxX - 1), " ", curses.A_REVERSE)
		i += 1

def cleanScreen():
	cs = 1
	while cs < (maxY - 2):
		stdscr.addstr(cs, 1, (" " * (maxX - 1)))
		cs += 1

def calculateDistance(x1,y1,x2,y2):  
	dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
	return dist

def populateWalls():
	global currentWallData
	currentWallData = {}
	cleanScreen()
	w = 1
	while w < ((maxX * maxY)/100):
		wallX = random.randint(1, (maxX - 2))
		wallY = random.randint(1, (maxY - 4))
		stdscr.addstr(wallY, wallX, "#", curses.A_REVERSE)
		id = findXYId(wallY, wallX)
		currentWallData.update({id: True})
		w += 1

def addEnemySpawnPoints():
	global zombies
	global zombieSpawns
	zombies = []
	zombieSpawns = []
	centerX = (maxX / 2)
	centerY = (maxY / 2)
	#Check if needed and add crypt
	if difficultyLevel > 9:
		x = round((centerX + random.randint(-20, 20)))
		y = round((centerY + random.randint(-10, 10)))
		createZombieSpawn(y, x, 'crypt', cryptTexture)

	#Add Gravestones
	numberOfGraves = (round(30 / (1 + (3 * (math.pow(1.2, -difficultyLevel))))) - 2)
	for number in range(numberOfGraves):
		Gx = random.randint(2, (maxX - 3))
		Gy = random.randint(2, (maxY - 5))
		createZombieSpawn(Gy, Gx, 'grave', graveTexture)

def addItems():
	itemsLocation = {}
	x = random.randint(1, (maxX - 2))
	y = random.randint(1, (maxY - 4))
	id = findXYId(y, x)
	itemsLocation.update({id: ['chest', y, x]})
	stdscr.addstr(y, x, "C", curses.color_pair(9))

def switchToAliens():
	global difficultyLevel
	global zombieColor
	global zombieTexture
	global zombieBaseHealth
	global zombieDammage

	global graveTextureDug
	global graveTexture
	global graveColorDug

	difficultyLevel = 1

	zombieBaseHealth = 200
	zombieTexture = 'a'
	zombieColor = 3
	zombieDammage = 10

	graveTextureDug = '&'
	graveTexture = '$'
	graveColorDug = graveColorNew



def generateNewChunk(chunkChange):
	global difficultyLevel
	global stage
	difficultyLevel += 1
	stage += 1
	if difficultyLevel == 27:
		switchToAliens()
	populateWalls()
	addEnemySpawnPoints()
	addItems()

def getChestItem():
	global ammo
	global playerHealth
	global grenades
	chance = random.randint(1, 4)
	if chance == 1:
		weapon = random.choice(list(weaponsCatalog.keys()))
		if weapon in weaponInventory:
			ammo += 20
		else:
			weaponInventory.append(weapon)
			updateWeaponConfigs(weapon)
			ammo += 10
	elif chance == 2:
		ammo += 10
	elif chance == 3:
		playerHealth += 20
	elif chance == 4:
		grenades += 5



def updatePlayer():
	global playerY
	global playerX
	global playerLastX
	global playerLastY
	global playerHealth
	global ammo
	global grenades
	if playerX == (maxX - 1) and ((playerY > 0 and playerY < (maxY-2)) or devel):
		generateNewChunk([0, 1])
		playerX = abs(playerX - (maxX - 2))

	idS = findXYId(playerY, playerX)

	if idS in currentWallData or playerY == 0 or playerY == (maxY - 2) or playerX == 0 or playerX == (maxX - 1):
		playerY = playerLastY
		playerX = playerLastX

	ed = 0
	while ed < len(zombies):
		if playerY == zombies[ed].posY and playerX == zombies[ed].posX:
			playerY = playerLastY
			playerX = playerLastX
		ed += 1

	if idS in itemsLocation:
		itemAdd = itemsLocation[idS]

		if itemAdd[0] == 'medkit':
			playerHealth += 10
		elif itemAdd[0] == 'ammo':
			ammo += 5
		elif itemAdd[0] == 'grenade':
			grenades += 1
		elif itemAdd[0] == 'chest':
			getChestItem()

		del itemsLocation[idS]


	stdscr.addstr(playerLastY, playerLastX, " ")
	stdscr.addstr(playerY, playerX, "@", curses.color_pair(1))

def addPlayer():
	stdscr.addstr(1, 1, "@", curses.color_pair(1))

def clearNullObjects():
	global nullObjectsX
	global nullObjectsY
	no = 0
	while no < len(nullObjectsY):
		stdscr.addstr(nullObjectsY[no], nullObjectsX[no], " ")
		stdscr.addstr(nullObjectsY[no], nullObjectsX[no], " ")
		no += 1
	nullObjectsY = []
	nullObjectsX = []

def drawStats():
	#Draw Player Health
	stdscr.addstr((maxY - 2), (5), ("Player Health: " + str(playerHealth)), curses.A_REVERSE)
	#Draw Weapon Type
	stdscr.addstr((maxY - 2), (30), weaponType, curses.A_REVERSE)
	#Draw Ammo
	stdscr.addstr((maxY - 2), (50), ("Ammo: " + str(ammo)), curses.A_REVERSE)
	#Draw Grenades
	stdscr.addstr((maxY - 2), (65), ("Grenades: " + str(grenades)), curses.A_REVERSE)
	#Draw Stage
	stdscr.addstr((0), (5), ("Stage: " + str(stage)), curses.A_REVERSE)
	#Draw Score
	stdscr.addstr((0), (20), ("Score: " + str(score)), curses.A_REVERSE)

def drawItems():
	for item in itemsLocation:
		if itemsLocation[item][0] == 'medkit':
			stdscr.addstr(itemsLocation[item][1], itemsLocation[item][2], "+", curses.color_pair(7))
		elif itemsLocation[item][0] == 'ammo':
			stdscr.addstr(itemsLocation[item][1], itemsLocation[item][2], "=", curses.color_pair(6))
		elif itemsLocation[item][0] == 'grenade':
			stdscr.addstr(itemsLocation[item][1], itemsLocation[item][2], "%", curses.color_pair(2))
		else:
			stdscr.addstr(itemsLocation[item][1], itemsLocation[item][2], "C", curses.color_pair(9))


def explosion(centerPointY, centerPointX , size):
	global playerHealth
	for number in range(1, 10):
		for i in range(size):
			y = (i + (centerPointY -1))
			for r in range(size):
				x = (r + (centerPointX -1))
				stdscr.addstr(y, x, ('$'), curses.color_pair(8))
				eID = findXYId(y, x)
				if (eID) in currentWallData:
					del currentWallData[eID]

				if x == playerX and y == playerY:
					playerHealth -= 50

				for zombie in zombies:
					if zombie.posX == x and zombie.posY == y:
						zombie.health = 0
				nullObjectsY.extend([y])
				nullObjectsX.extend([x])

def checkIfInPlayerRadius(self, radius):
	if (calculateDistance(self.posX, self.posY, playerX, playerY) <= radius):
		return "direct"
	else:
		return "random"

def findXYId(y, x):
	number = (math.pow(2, y))*(math.pow(3, x))
	return number


class Zombie:
	def __init__(self, x, y, typeZ):
		self.zombieType = typeZ
		self.posX = x
		self.posY = y
		self.tick = 1
		self.health = (zombieBaseHealth+(random.randint(-25, 25)))


	def calculatePlayerDir(self):
		direction = [0, 0]
		if playerX > self.posX:
			direction[1] = 1
		elif playerX < self.posX:
			direction[1] = -1
		if playerY > self.posY:
			direction[0] = 1
		elif playerY < self.posY:
			direction[0] = -1

		return direction

	def update(self):
		global playerHealth
		global zombieRemovalNeeded

		stdscr.addstr(self.posY, self.posX, " ", curses.color_pair(2))
		lastPosY = self.posY
		lastPosX = self.posX
		if self.health > 0:
			movement = checkIfInPlayerRadius(self, 20)
			if self.tick >= 5 and movement == 'random':
				self.posY += random.randint(-1, 1)
				self.posX += random.randint(-1, 1)
				self.tick = 0
			elif self.tick >= 5:
				direction = self.calculatePlayerDir()
				self.posY += direction[0]
				self.posX += direction[1]
				if (calculateDistance(self.posX, self.posY, playerX, playerY) > 5) and (random.randint(1, 4) == 1):
					self.posY += random.randint(-1, 1)
					self.posX += random.randint(-1, 1)

				self.tick = 0

			LocationID = findXYId(self.posY, self.posX)
			if (LocationID in currentWallData) or self.posY == 0 or self.posY == (maxY - 2) or self.posX == 0 or self.posX == (maxX - 1):
				self.posY = lastPosY
				self.posX = lastPosX

			if (self.posY == playerY and self.posX == playerX):
				self.posY = lastPosY
				self.posX = lastPosX
				playerHealth -= zombieDammage
			stdscr.addstr(self.posY, self.posX, zombieTexture, curses.color_pair(zombieColor))
			self.tick += 1
		else:
			stdscr.addstr(self.posY, self.posX, zombieTexture)
			zombieRemovalNeeded = True
			self.death()

	def death(self):
		global enemiesKilled
		enemiesKilled += 1
		if (random.randint(1, 3) == 1):
			globals()['drop'+(random.choice(drops))](self)

def dropGrenades(self):
	id = findXYId(self.posY, self.posX)
	itemsLocation.update({id: ['grenade', self.posY, self.posX]})
	stdscr.addstr(self.posY, self.posX, "%", curses.color_pair(2))

def dropAmmo(self):
	id = findXYId(self.posY, self.posX)
	itemsLocation.update({id: ['ammo', self.posY, self.posX]})
	stdscr.addstr(self.posY, self.posX, "=", curses.color_pair(6))

def dropMedkit(self):
	id = findXYId(self.posY, self.posX)
	itemsLocation.update({id:['medkit', self.posY, self.posX]})
	stdscr.addstr(self.posY, self.posX, "+", curses.color_pair(7))

class ZombieSpawn:
	def __init__(self, x, y, type, texture):
		global wallDataX
		global wallDataY
		self.spawnPoints = [[-1, 5], [-1, 6], [-1, 7], [5, 5], [5, 6], [5, 7]]
		self.texture = texture
		self.type = type
		self.posX = x
		self.posY = y
		self.tick = 0
		self.active = True

		if type == 'crypt':
			count = 0
			for line in self.texture:
				stdscr.addstr((self.posY + count), (self.posX), self.texture[count])
				letCount = 0
				for letter in line:
					locationID = findXYId(self.posY, self.posX)
					currentWallData.update({locationID: True})
					letCount += 1
				count += 1

		else:
			locationID = findXYId(self.posY, self.posX)
			currentWallData.update({locationID: True})
			stdscr.addstr((self.posY), (self.posX), self.texture, curses.color_pair(graveColorNew))

	def update(self):
		if self.type == 'crypt':
			if self.tick == 60:
				change = (random.choice(self.spawnPoints))
				y = ((change[0]) + self.posY)
				x = ((change[1]) + self.posX)
				createZombie(y, x)
				self.tick = 0

			self.tick += 1
		elif self.active:
			if checkIfInPlayerRadius(self, 20) == 'direct':
				Gx = (self.posX + random.choice([-1, 1]))
				Gy = (self.posY + random.choice([-1, 1]))
				createZombie(Gy, Gx)
				self.active = False
				stdscr.addstr((self.posY), (self.posX), graveTextureDug, curses.color_pair(graveColorDug))

def updateZombies():
	global zombieRemovalNeeded
	global zombies

	for zombie in zombies:
		zombie.update()

	for zombieSpawn in zombieSpawns:
		zombieSpawn.update()

	if zombieRemovalNeeded:
		zombies = [zombie for zombie in zombies if zombie.health > 0]


def createZombie(y, x):
	global zombies
	typeZ = 'z'
	zombies.append(Zombie(x, y, typeZ))

def createZombieSpawn(y, x, type, texture):
	global zombieSpawns
	zombieSpawns.append(ZombieSpawn(x, y, type, texture))

def updateGrenade():
	global grenadeDirX
	global grenadeDirY
	global grenadeX
	global grenadeY
	global grenadeActive
	global grenadeTick

	#movement
	grenadeTick += 1
	if (grenadeTick % 2 == 0):
		stdscr.addstr(grenadeY, grenadeX, " ")
		grenadeY += grenadeDirY
		grenadeX += grenadeDirX

	#handle colision
	LocationID = findXYId(grenadeY, grenadeX)
	if (LocationID in currentWallData) or grenadeTick > 20 or grenadeY == 0 or grenadeY == (maxY - 2) or grenadeX == 0 or grenadeX == (maxX - 1):
		grenadeY -= grenadeDirY
		grenadeX -= grenadeDirX
		explosion(grenadeY, grenadeX, 3)
		grenadeActive = False
		grenadeTick = 0

	for zombie in zombies:
		if zombie.posX == grenadeX and zombie.posY == grenadeY:
			grenadeY -= grenadeDirY
			grenadeX -= grenadeDirX
			explosion(grenadeY, grenadeX, 3)
			grenadeActive = False
			grenadeTick = 0

	if grenadeActive:
		stdscr.addstr(grenadeY, grenadeX, "o")
	else:
		stdscr.addstr(grenadeY, grenadeX, " ", curses.A_REVERSE)

def updateWeaponConfigs(type):
	global weaponType
	global fireRate
	global maximumBulletTravel
	global bulletTexture
	global weaponClass
	global ammoConsumption
	global weaponDammage
	global weaponAccuracy
	weaponType = type
	bulletTexture = weaponsCatalog[type][0]
	weaponClass = weaponsCatalog[type][1]
	maximumBulletTravel = weaponsCatalog[type][2]
	ammoConsumption = weaponsCatalog[type][3]
	fireRate = weaponsCatalog[type][4]
	weaponDammage = weaponsCatalog[type][5]
	weaponAccuracy = weaponsCatalog[type][6]

def flipToNextInventoryItem():
	global inventorySpace
	if (inventorySpace+1) == (len(weaponInventory)):
		updateWeaponConfigs(weaponInventory[0])
		inventorySpace = 0
	else:
		inventorySpace += 1
		updateWeaponConfigs(weaponInventory[(inventorySpace)])



def grenadeThrow(lastY, lastX):
	global grenades
	global grenadeDirX
	global grenadeDirY
	global grenadeX
	global grenadeY
	global grenadeActive
	global nullObjectsY
	global nullObjectsX

	grenadeActive = True
	grenades -= 1
	grenadeX = (lastX + playerX)
	grenadeY = (lastY + playerY)
	grenadeDirY = lastY
	grenadeDirX = lastX
	stdscr.addstr(grenadeY, grenadeX, "o")

def fireWeapon(lastY, lastX):
	#Variables
	active = True
	bulletTick = 0
	global countVars
	global ammo
	bulletX = (playerX)
	bulletY = (playerY)
	ammo -= ammoConsumption

	newTexture = bulletTexture[0]
	newMaximumDistance = maximumBulletTravel

	if ((lastY != 0) and (lastX == 0) and weaponClass == "gun"):
		newTexture = bulletTexture[1]
		newMaximumDistance /= 2

	if ((((lastY > 0) and (lastX > 0)) or ((lastY < 0) and (lastX < 0))) and weaponClass == "gun"):
		newTexture = bulletTexture[2]
		newMaximumDistance /= 2
	elif ((lastY != 0) and (lastX != 0) and weaponClass == "gun"):
		newTexture = bulletTexture[3]
		newMaximumDistance /= 2

	if (weaponClass == "mele"):
		newTexture = random.choice(bulletTexture)

	while active:
		#Add XY
		bulletY += lastY
		bulletX += lastX
		bulletTick += 1

		#Check Colisions
		LocationID = findXYId(bulletY, bulletX)
		if (LocationID in currentWallData) or (newMaximumDistance <= bulletTick) or bulletY == 0 or bulletY == (maxY - 2) or bulletX == 0 or bulletX == (maxX - 1):
			active = False
			bulletY -= lastY
			bulletX -= lastX
			bulletTick = 0

		for zombie in zombies:
			if zombie.posX == bulletX and zombie.posY == bulletY:
				if random.randint(1, weaponAccuracy) == 1:
					zombie.health -= (weaponDammage)
				else:
					zombie.health -= weaponDammage/2
				bulletY -= lastY
				bulletX -= lastX
				active = False
				break

		stdscr.addstr(bulletY, bulletX, newTexture, curses.color_pair(6))
		nullObjectsY.extend([bulletY])
		nullObjectsX.extend([bulletX])




def mainLoop():
	#Globals
	global playerY
	global playerX
	global playerLastX
	global playerLastY
	global GameRunning
	global playerXSpeed
	global playerYSpeed
	global score

	#Vars
	lastDirY = -1
	lastDirX = 0
	tick = 0
	weaponTick = False

	while GameRunning:
		score = (stage * enemiesKilled)

		if weaponTick:
			tick += 1
			if tick == fireRate:
				weaponTick = False
				tick = 0

		if playerHealth <= 0 and noKill == False:
			GameRunning = False


		clearNullObjects()

		time.sleep(1.0/30.0)
		key = ''

		key = stdscr.getch()
		playerLastY = playerY
		playerLastX = playerX
		if key == curses.KEY_UP:
			playerY += -1
			lastDirY = -1
			lastDirX = 0
		elif key == curses.KEY_DOWN:
			playerY += 1
			lastDirY = 1
			lastDirX = 0
		elif key == curses.KEY_LEFT:
			playerX += -1
			lastDirX = -1
			lastDirY = 0
		elif key == curses.KEY_RIGHT:
			playerX += 1
			lastDirX = 1
			lastDirY = 0
		elif key == curses.KEY_HOME:
			playerY -= 1
			lastDirY = -1
			playerX -= 1
			lastDirX = -1
		elif key == curses.KEY_END:
			playerX -= 1
			lastDirX = -1
			playerY += 1
			lastDirY = 1
		elif key == curses.KEY_PPAGE:
			playerY -= 1
			lastDirY = -1
			playerX += 1
			lastDirX = 1
		elif key == curses.KEY_NPAGE:
			playerX += 1
			lastDirX = 1
			playerY += 1
			lastDirY = 1

		if key == ord("g"):
			if grenades >= 1 and (grenadeActive == False):
				grenadeThrow(lastDirY, lastDirX)
		if key == ord("f") or key == curses.KEY_B2:
			if weaponTick == False:
				if ammo >= (ammoConsumption) or weaponClass == 'mele':
					fireWeapon(lastDirY, lastDirX)
					weaponTick = True
		if key == ord('d'):
			flipToNextInventoryItem()
		if key == ord("q"):
			GameRunning = False

		if grenadeActive:
			updateGrenade()
		drawItems()
		updatePlayer()
		updateZombies()
		drawBorder()
		drawStats()
		stdscr.refresh()

def startGame(d, i):
	global devel
	global noKill
	if maxX < 85:
		print('''Error Code[23]\nPlease make your terminal larger before relaunching the game.''')
		stopCurses()
		exit()
	devel = d
	noKill = i
	initCurses()
	drawBorder()
	addPlayer()
	generateNewChunk([0,0])
	mainLoop()
	stdscr.refresh()
	stopCurses()
