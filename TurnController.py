### This tells you whose turn it is and controls 

import pygame
import sprites
from sprites import AnimatedSprite, Actor
import GameBoard
from GameBoard import Board
import collision
from collision import PopBestPath, PathList

import AutoTurn
from AutoTurn import TurnAI, PortalAI, actorDist, dist

ATTACK="Attack"
MOVE="Move"
SPECIAL="Special"
AOE="AOE"

#alignments
FRIENDLY='Friendly'
HOSTILE='Hostile'
NEUTRAL = 'Neutral'

class Turn(object):
    def __init__(self, board):

        self._canAttack=True
        self._canMove=True
        self._canSpecial1 = True
        self._canSpecial2 = True
        self._mode=[]#Modes include 'Attack', 'Move'
        self._characters= board.Characters()
        self._board=board
        
        self._initiativeThreshold=50#make this large, relative to speed.

        self._currentSprite=[]
        self._moves=[]#moves generated by CollisionFinder
        self._path=[]#path from the moves
        self._targetList=[]

        #these two are used to string together actions.
        self._MidAction = 0
        self._actionQueue = []

        ##Load UsefulSprite/Images
        self._DeathImageSet=sprites.load_sliced_sprites(64,64,'images/skeleton_death.png')
        self._SkeletonImageSet = sprites.load_sliced_sprites(64, 64, 'images/skeleton/skeleton_walk.png')
        self._SkeletonAttackImageSet = sprites.load_sliced_sprites(64, 64, 'images/skeleton/skeleton_attack.png')
        self._PigImageSet = sprites.load_sliced_sprites(64, 64, 'images/pigman_walkcycle.png')
        self._PortalImageSet = sprites.load_sliced_sprites(64,64,'images/base_assets/male_spellcast.png')
        print(len(self._PortalImageSet))

        
    def Mode(self):
        return self._mode
    def AttackMode(self):
        if self._currentSprite._path ==[] and self._currentSprite._MidAnimation ==0 and self._canAttack:
            self._mode = ATTACK
            self.TargetList(1,1)#we do this for now
    def TargetList(self, rangeMin, rangeMax):
        #print("targetlist called")
        targetlist=[]
        self._mode = ATTACK
        tile_x=self._currentSprite.tile_x
        tile_y=self._currentSprite.tile_y
        for actor in self._characters:
            actor_distance=abs(actor.tile_x-tile_x)+abs(actor.tile_y-tile_y)
            if actor_distance>=rangeMin and actor_distance <=rangeMax:
                self._board.HighlightTile(actor.tile_x, actor.tile_y, "images/blue_box.png")
                #print("highlighted", actor)
                targetlist.append(actor)
        self._targetList = targetlist
                
    def MoveMode(self):
        if self._canMove:
            self._mode = MOVE
            self._moves = PathList(self._board, self._currentSprite.tile_x,self._currentSprite.tile_y, self._currentSprite._Movement)
            #print(self._moves)
            self._board.DrawPossibleMoves(self._moves)


        
    def CancelMode(self):
        self._board.ClearLayer(self._board._shadowLayer)#clears off any shadow junk
        self._board.HighlightTile(self._currentSprite.tile_x, self._currentSprite.tile_y, "images/ActiveShadow.png")
        self.Board().ChangeCursor("images/blue_box.png", 0, 0)
        self._moves=[]
        self._path=[]
        self._targetList=[]
        self._mode=[]
        
    def EndTurn(self):
        self._board.ClearLayer(self._board._shadowLayer)#clears off any shadow junk
        self.Board().ChangeCursor("images/blue_box.png", 0, 0)
        self._currentSprite._Initiative=0
        self._currentSprite=[]
        self._canAttack=True
        self._canMove=True
        self._canSpecial1 = True
        self._canSpecial2 = True
        self._mode=[]
        self._moves=[]#moves generated by CollisionFinder
        self._path=[]#path from the moves
        self._targetlist=[]
        self.Next()
        
        
        
    def Next(self):#When a player ends their turn it finds the next player up and returns that value
        #print("Next Called")
        if self.CurrentSprite() !=[]:
            self.CurrentSprite()._Initiative=0 #resets initiative
        self._currentSprite=[]
        highestInitiative=0
        highestActor=[]#we could just use _currentSprite but this is nicer

        #first checks if anyone has a high enough initiative to go
        for actor in self._characters:      
            if actor._Initiative>highestInitiative:
                highestInitiative= actor._Initiative
                highestActor=actor
        #if not one has high enough initiative it adds speed to everyones initiative
        while highestInitiative < self._initiativeThreshold:
            #first add a little to everyones initiative
            for actor in self._characters:
                actor.Wait()
                #print(actor.Name(),'initiative increased to', actor.Initiative())
            #then find the highest
            for actor in self._characters:      
                if actor._Initiative>highestInitiative:
                    highestInitiative= actor._Initiative
                    highestActor=actor
        self._currentSprite=highestActor
        self._board.PanCamera((self._currentSprite.tile_x + self._board._screenTileOffset_x)*self._board._tileSize, \
            (self._currentSprite.tile_y+ self._board._screenTileOffset_y)*self._board._tileSize) 

        self._board.ClearLayer(self._board._shadowLayer)#clears off any shadow junk
        self._board.HighlightTile(self._currentSprite.tile_x, self._currentSprite.tile_y, "images/ActiveShadow.png")

        if self._currentSprite.Alignment() == 'Friendly':

            #TurnAI(self)#only do this if you want them to fight each other
            return self.CurrentSprite()
        
        elif self.CurrentSprite().Name()=='Portal':
            PortalAI(self)
            return self.CurrentSprite()
        else:
            #print('Found a hostile')
            TurnAI(self)
            return self.CurrentSprite()


    def Attack(self,target):
        self._board.ClearLayer(self._board._shadowLayer)#clears off any shadow junk
        self._board.HighlightTile(self._currentSprite.tile_x, self._currentSprite.tile_y, "images/ActiveShadow.png")
        self._currentSprite.Attack(target, self.CurrentSprite().Power())
        
        #print(self._currentSprite._Name, "attacked", target._Name)
        self._canAttack=False
        self._mode=[]
        #blot out the UI somehow


    
    def Move(self, tile_x, tile_y):
        #print("looking for a way to", tile_x, tile_y)
        if self._moves !=[]:
            self._path = PopBestPath(tile_x, tile_y, self._moves)
        #print(self._moves)
        
        
        if self._path == []:
            pass
        elif self._canMove==True: #player has selected a possible path
            
            self._board.ClearLayer(self._board._shadowLayer)
            self._currentSprite.MultiMove(self._path)
            self._board.HighlightTile(tile_x, tile_y, "images/ActiveShadow.png")
            self._canMove=False
            self._path=[]#just in case we reset
            self._moves=[]#again, just in case.
            self._mode=[]
        

    def CurrentSprite(self):
        return self._currentSprite
    def Characters(self):
        return self._characters
    def Board(self):
        return self._board

    def addQueue(self, actionName, closeOpponent ,Move):   #something like addQueue("Attack", ) would tell the currentSprite to attack the Actor in (5,13) 
        self._actionQueue.append((actionName,closeOpponent,Move))
    def Queue(self):
        return self._actionQueue
        

    def update(self):  #mostly for the AI turns.  checks if the character is animating
        if self.CurrentSprite().Animating():
            pass
        elif self.Queue() !=[]:
            
            self.Queue().reverse()
            nextMove=self.Queue().pop()
            self.Queue().reverse()
            #print(nextMove, 'is begin performed')
            self.Action(nextMove)

    def Action(self, action):
        print('Action is Called')
        #an action is a list =('Attack' or 'Move' or 'Wait', a possible target (actor), and a move)
        #this is how the AI tells NPCs what to do.
        actiontype=action[0]
        actiontarget=action[1]
        actionmove=action[2]
        if actiontype=='Attack':
            self.TargetList(1,1)#we do this for now
            self.CurrentSprite().Attack(actiontarget,self.CurrentSprite().Power())
        elif actiontype=='Move':
            #print(actionmove[3])
            self._board.ClearLayer(self._board._shadowLayer)
            self._path = PopBestPath(actionmove[0],actionmove[1], [actionmove])
            self._currentSprite.MultiMove(self._path)
        elif actiontype=='Wait':
            #print(self.CurrentSprite().Name(), 'is done with turn!')
            self.EndTurn()
        else:
            print('You should not be here. An action called', actiontype, 'was called.')
        
        

##Special Moves##
#these are all the special attacks mode are in two parts.
#The player enters a mode, i.e. "AOEmode" for an AOE attack which shades the targetable tiles and changed the cursor.
#the player then can make the attack

    def AOEMode(self):
        if self._canAttack:
            self._mode=AOE
            specialRange=4
            self._board.HighlightArea(self._currentSprite.tile_x, self._currentSprite.tile_y, specialRange,'images/blue_box.png')            
            self.Board().ChangeCursor("images/area01.png", -1, -1)
            
    def AOEAttack(self,tile_x,tile_y):#This is also known as Fire Lion!
        board_x, board_y =tile_x+self.Board()._camTile_x, tile_y+self.Board()._camTile_y
        if dist(self.CurrentSprite().tile_x,self.CurrentSprite().tile_y, board_x,board_y)<=3:
            
            #print(tile_x+self.Board()._camTile_x,tile_y+self.Board()._camTile_y)
            HitAnyone=False
            for actor in self.Characters():
                #print(actor.tile_x,actor.tile_y)
                if dist(actor.tile_x, actor.tile_y, board_x, board_y) <=1:
                    HitAnyone=True
                    self._currentSprite.Attack(actor,self.CurrentSprite().Power())
                    print(self._currentSprite._Name, "attacked", actor._Name, 'with', AOE)
            if HitAnyone:#check if anyone was damaged, if not then don't do anything
                self._board.ClearLayer(self._board._shadowLayer)
                AttackSound = pygame.mixer.Sound("sound/explosion.wav")
                AttackSound.play()
                self.Board().AnimatedParticleEffect(128,128,'images/magic/AOE_firelion.png',board_x, board_y)
                self._canAttack=False
                self.CancelMode()
                
        else:
            print("Target Tile is out of Range.")

    def SpawnSkeleton(self, board_x, board_y):#since this should only happen with the bad guys we will not have a mode

        SkeletonSprite = Actor((board_x-.5)*self.Board()._tileSize, (board_y-1)*self.Board()._tileSize, \
            self._SkeletonImageSet[0], self._SkeletonImageSet[1], self._SkeletonImageSet[2], self._SkeletonImageSet[3], \
            self._DeathImageSet[0], self._SkeletonAttackImageSet[0], self._SkeletonAttackImageSet[1], self._SkeletonAttackImageSet[2], self._SkeletonAttackImageSet[3], \
            "Skeleton", HOSTILE ,4, 0, 2, 6, 8)
        SkeletonSprite.RegisterAction("Slash","The skeleton lashes out at the target", self.Attack, self._SkeletonImageSet[3])
        self.Characters().add(SkeletonSprite)


    def SpawnPortal(self, board_x, board_y):
        PortalSprite = Actor((board_x-.5)*self.Board()._tileSize, (board_y-1)*self.Board()._tileSize, \
            self._PortalImageSet[0], self._PortalImageSet[1], self._PortalImageSet[2], self._PortalImageSet[3], \
            self._PortalImageSet[0], self._PortalImageSet[0], self._PortalImageSet[1], self._PortalImageSet[2], self._PortalImageSet[3], \
            "Portal", HOSTILE ,1, 3, 2, 6, 20)
        PortalSprite.RegisterAction("Spawn","Spawn a skeleton from the Abyss", [],[])
        self.Characters().add(PortalSprite)
#def VampiricStrike(actor,target):# a special attack that also heals you.

#def Heal(actor, target):#heals a certain target

#def PassiveHeal(actor):


    
    
#def WhirlWind(actor):#attacks all players (hostile or friendly) in adjacent spa


#def Cripple(actor): decreases initiative.


