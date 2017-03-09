__author__ = 'Matt Cordoba'
from enum import Enum
import MySQLdb

P1_HIT = 1
P1_MISS = 2
P2_HIT = 3
P2_MISS = 4
class PlayerType(Enum):
    p1 = 1
    p2 = 2
class Player():
    def __init__(self,pType,name='Player 1',prevGameStats = None):
        self.pType = pType
        self.name = name
        self.cupsRemaining = 6
        self.turnsTaken = 0
        self.explosionsPerTurn = 0
        self.redemptionsHit = 0
        self.redemptionsRequired = 0
        self.redemptionPressureHit = 0
        self.lastCupShots = 0
        self.lastCupHits = 0
        self.shotsTaken = 0
        self.shotsHit = 0
        if prevGameStats is not None:
            self.loadPrevGameStats(prevGameStats)
    def loadPrevGameStats(self,prevGameStats):
        pass
    def getRedemptionsRequired(self):
        return self.redemptionsRequired
    def getRedemptionsHit(self):
        return self.redemptionsHit
    def getRedemtionPressureHit(self):
        return self.redemptionPressureHit
    def handleLossCups(self,cupCount):
        self.cupsRemaining -= cupCount
        if(self.cupsRemaining <= 0):
            if(self.redemptionsRequired == 0):
                self.redemptionsRequired = abs(self.cupsRemaining - 1)
            else:
                #stack redemptions
                self.redemptionsRequired += cupCount
            self.cupsRemaining = 1
        return self.redemptionsRequired
    def getName(self):
        return self.name
    def getCupsRemaining(self):
        return self.cupsRemaining
    def getLastCupsHit(self):
        if(self.lastCupShots == 0):
            return None
        return self.lastCupHits * 100.0 / self.lastCupShots
    def takePlayerTurn(self,p2):
        gameOver = False
        onRedemption = False
        print('It is ' + str(self.getName()) + "'s turn to shoot")
        if(self.getRedemptionsRequired() != 0):
            onRedemption = True
            print(self.getName() + ' is on redemption. They must hit ' + str(self.getRedemptionsRequired()) + ' this turn to stay alive!')
        #00 = double miss, 10/01 = one hit one miss, 11 = double hit, 111 = explosion
        command = str(raw_input('input shot status: '))
        #add to player shot status
        self.shotsTaken += 2
        self.turnsTaken += 1
        if(p2.cupsRemaining == 1):
            self.lastCupShots += 2
        reShot = False
        cupsThisTurn = 0
        if('i' in command): #handle different island scenarios
            if(command == 'i11'):
                #island + 1 random (no explosion)
                cupsThisTurn = 3
                self.shotsHit += 1
                reShot = True
            elif(command == 'i01' or command == 'i10'):
                #island + 1 miss
                self.shotsHit += 1
                cupsThisTurn = 2
            elif(command == 'i111'):
                #island + explosion
                if(not onRedemption):
                    self.explosionsPerTurn += 1
                    cupsThisTurn = 4
                else:
                    cupsThisTurn = 3

                self.shotsHit += 2
                reShot = True

        elif command == '111':
            if(not onRedemption and p2.cupsRemaining != 1):
                #explosion hit not redemption
                self.explosionsPerTurn += 1
                cupsThisTurn = 3
                self.shotsHit += 2
                reShot = True
            else:
                cupsThisTurn = 2
                self.shotsHit += 2
                reShot = True
            if(p2.cupsRemaining == 1):
                self.lastCupHits += 2
        elif command == '11':
            cupsThisTurn = 2
            self.shotsHit += 2
            reShot = True
            if(p2.cupsRemaining == 1):
                self.lastCupHits += 2
        elif command == '10' or command == '01':
            cupsThisTurn = 1
            self.shotsHit += 1
            if(p2.cupsRemaining == 1):
                self.lastCupHits += 1

        if not onRedemption:
            redemptionsRequired = p2.handleLossCups(cupsThisTurn)
            if(redemptionsRequired != 0 and not reShot):
                self.redemptionPressureHit += 1

        #handle a player being on redemption
        if(onRedemption):
            cupDifference = self.getRedemptionsRequired() - cupsThisTurn
            if(cupDifference <= 0):
                #redemption hit, continue the game
                print('player has hit redemptions... continuing')
                self.redemptionsHit += 1
                self.redemptionsRequired = 0
                if(cupDifference < 0):
                    #subtract additional cups from other player in difference
                    p2.handleLossCups(abs(cupDifference))
                if(reShot):
                    self.takePlayerTurn(p2)
            else:
                if(not reShot):
                    #redemptions done, game is over
                    self.redemptionsRequired -= cupDifference
                    gameOver = True
                else:
                    #more redemptions still need to be hit, but player has balls back
                    self.redemptionsRequired -= cupsThisTurn
                    self.takePlayerTurn(p2)
                    pass
        elif(reShot):#balls back scenario with no redemption
            self.takePlayerTurn(p2)

        return gameOver

    def handleOpponentTurn(self,oppponentShotStatus):
        pass
    def getStatus(self):
        d = {}
        d['NAME'] = self.getName()
        d['CUPS_REMAINING'] = self.getCupsRemaining()
        d['EXPLOSIONS_PER_TURN'] = self.getExplosionsPerTurn()
        d['LAST_CUP_HITS'] = self.getLastCupsHit()
        d['SHOT_PERCENTAGE'] = self.getShotPercentage()
        d['REDEMPTIONS_REQUIRED'] = self.getRedemptionsRequired()
        d['REDEMPTIONS_HIT'] = self.getRedemptionsHit()
        d['REDEMPTION_PRESSURE_HIT'] = self.getRedemtionPressureHit()
        return d
    def getCupsRemaining(self):
        return self.cupsRemaining
    def getExplosionsPerTurn(self):
        if(self.turnsTaken == 0):
            return None
        return self.explosionsPerTurn * 100.0 / self.turnsTaken
    def getShotPercentage(self):
        if(self.shotsTaken  == 0):
            return None
        return self.shotsHit * 100.0 / self.shotsTaken
class Database():
    def __init__(self):
        pass
    def _connect(self):
        self.db = MySQLdb.connect(host="pongstatsdb2.clvjtmowubkf.us-west-2.rds.amazonaws.com",    # your host, usually localhost
                     user="",         # your username
                     passwd="",  # your password
                     db="pongstatsdb2")        # name of the data base

        # you must create a Cursor object. It will let
        #  you execute all the queries you need
        self.cur = self.db.cursor()
        pass
    def _disconnect(self):
        pass
    def startSet(self,player1Key,player1Name,player2Key,player2Name):
        pass
    def startGame(self):
        pass
    def upsertPlayer(self,playerName,pNumber):
        playerName = playerName.split(" ")
        args = (playerName[0],playerName[1])
        query = "SELECT id FROM pongstatsdb2.spot_fm_player WHERE firstName = '%s' and lastName = '%s';"
        self.cur.execute(query,args)
        rows = self.cur.fetchall()
        if(len(rows) == 0):
            #insert new player
            query = "INSERT INTO pongstatsdb2.spot_fm_player (firstName, lastName) VALUES ('%s', '%s');"
            self.cur.execute(query,args)
            playerId = self.cur.lastrowid
            self.db.commit()
        else:
            #get player id
            playerId = rows[0][0]
        if(pNumber == 1):
            self.player1ID = playerId
        elif(pNumber == 2):
            self.player2ID = playerId
        else:
            raise AttributeError
    def updateGameStats(self,stats):
        pass
    def updateSetStats(self,stats):
        pass
    def endSet(self):
        pass
class Game():
    def __init__(self,player1Name,player2Name):
        self.p1 = Player(PlayerType.p1,player1Name)
        self.p2 = Player(PlayerType.p2,player2Name)
    def _waitForPlayerStart(self):
        startPlayerChosen = False
        command = None
        while not startPlayerChosen:
            command = input('press 1 to indincate p1 starting, 2 to indicate p2 starting: ')
            command = int(command)
            if(command == 1 or command == 2):
                startPlayerChosen = True
        playerChosen = None
        if(command == 1):
            #player 1 is going first
            playerChosen = PlayerType.p1
        else:
            playerChosen = PlayerType.p2
        return playerChosen
    def _initGameboard(self):
        pass
    def updatePlayerStatus(self):
        print(self.p1.getStatus())
        print(self.p2.getStatus())
    def playGame(self):
        #init the gameboard
        self._initGameboard()
        #start the game
        playerChosen = self._waitForPlayerStart()
        gameOver = False
        while not gameOver:
            if(playerChosen == PlayerType.p1):
                #take P1 go first
                gameOver = self.p1.takePlayerTurn(self.p2)
                self.updatePlayerStatus()
                gameOver = self.p2.takePlayerTurn(self.p1)
                self.updatePlayerStatus()

            else:
                #take P2 turn
                gameOver = self.p2.takePlayerTurn(self.p1)
                self.updatePlayerStatus()
                gameOver = self.p1.takePlayerTurn(self.p2)
                self.updatePlayerStatus()
        print('game is over!')
        print('final stats:')
        print(self.p1.getStatus())
        print(self.p2.getStatus())
player1Name = 'Matt Cordoba'
player2Name = 'Ben Mattison'
g = Game(player1Name,player2Name)
g.playGame()
