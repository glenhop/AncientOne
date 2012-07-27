import sys
import os
#import array
import pygame

import collision
from collision import PopBestPath, PathList

import ui
from ui import Menu, CharacterInfo, LevelUpScreen

from pygame.locals import*

import sprites
from sprites import AnimatedSprite, Actor

import tiledtmxloader #this reads .tmx files
import GameBoard
from GameBoard import Board

import TurnController
from TurnController import Turn

import AutoTurn
from AutoTurn import TurnAI

MAP="images/map03.tmx"

#alignments
FRIENDLY='Friendly'
HOSTILE='Hostile'
NEUTRAL = 'Neutral'

#other forms of attack

ATTACK="Attack"
RANGED="Ranged"
SPECIAL="Special"
AOE="Fire Lion"
MOVE="Move"
CANCEL="Cancel"

actionList=[ATTACK, RANGED,SPECIAL,AOE,  MOVE,CANCEL]

tileSize=32

def main():
    """
    Main method.
    """
    args = sys.argv[1:]
    if len(args) < 1:
        path_to_map = os.path.join("", MAP) #Loads the map path
        #print(("usage: python %s your_map.tmx\n\nUsing default map '%s'\n" % \
        #    (os.path.basename(__file__), path_to_map)))
    else:
        path_to_map = args[0]

    main_pygame(path_to_map)

def main_pygame(file_name):

    

    pygame.init()

    print(" z/x/c/v = atttack/move/wait/cancel, wasd=camera movement, '[]' control the volume of the background music")


    myfont = pygame.font.Font("petme/PetMe128.ttf", 10)


    
    worldMap = tiledtmxloader.tmxreader.TileMapParser().parse_decode(file_name)
    assert worldMap.orientation == "orthogonal"
    screen_width = min(1024, worldMap.pixel_width)
    screen_height = min(768, worldMap.pixel_height)
    screen = pygame.display.set_mode((screen_width, screen_height))
    Characters = pygame.sprite.RenderUpdates()
    
    GameBoard = Board(worldMap, Characters, tileSize, screen)
    pygame.display.set_caption("Ancient Juan")


    #UI sprite container
    #UImenu = pygame.sprite.RenderUpdates()
    menuItems = ["Attack", "Move" ,"Wait", "Cancel"]
    myMenu = Menu("Action:", menuItems, myfont, 50, 150, 200, 200)
    

    #CHARACTERS!

    DeathImageSet=sprites.load_sliced_sprites(64,64,'images/skeleton_death.png')
    
    '''
    #Obligatory Female Supporting Character (with sassyness!)
    PrincessImageSet = sprites.load_sliced_sprites(64,64,'images/princess.png')
    PrincessSprite = Actor((23-.5)*tileSize, (21-1)*tileSize,PrincessImageSet[1], PrincessImageSet[0], PrincessImageSet[2], PrincessImageSet[3], \
                               'Peach', FRIENDLY, 3, 0, 2, 6, 1, DeathImages=DeathImageSet[0])
    Characters.add(PrincessSprite)

    #Bebop's Legacy
    PigImageSet = sprites.load_sliced_sprites(64, 64, 'images/pigman_walkcycle.png')
    PigSprite = Actor((24-.5)*tileSize, (21-1)*tileSize, PigImageSet[1], PigImageSet[0], PigImageSet[2], PigImageSet[3], 'Bebop',HOSTILE, 2, 0, 5, 5, 60 ,DeathImages=PrincessImageSet[1])
    Characters.add(PigSprite)
    
    #Solider of Fortune
    SoldierImageSet = sprites.load_sliced_sprites(64, 64, 'images/base_assets/soldier.png')
    SoldierSprite = Actor((25-.5)*tileSize, (21-1)*tileSize, SoldierImageSet[1], SoldierImageSet[0], SoldierImageSet[2], SoldierImageSet[3], "Bald Cloud", FRIENDLY ,3, 0, 3, 0, 1, DeathImages=DeathImageSet[0])
    Characters.add(SoldierSprite)

    #www.whoisthemask.com
    MaskImageSet = sprites.load_sliced_sprites(64, 64, 'images/maskman.png')
    MaskSprite = Actor((26-.5)*tileSize, (21-1)*tileSize, MaskImageSet[1], MaskImageSet[0], MaskImageSet[2], MaskImageSet[3],"Tuxedo Mask" ,HOSTILE,2, 2, 5, 5, 75, DeathImages=DeathImageSet[0])
    Characters.add(MaskSprite)
    '''


    SuitImageSet = sprites.load_sliced_sprites(64, 64, 'images/Suit/Suit_walk.png')
    SuitAttackImageSet = sprites.load_sliced_sprites(64, 64, 'images/Suit/Suit_attack.png')
    SuitSprite = Actor((14-.5)*tileSize, (4-1)*tileSize, SuitImageSet[0], SuitImageSet[1], SuitImageSet[2], SuitImageSet[3], \
        DeathImageSet[0], SuitAttackImageSet[0], SuitAttackImageSet[1], SuitAttackImageSet[2], SuitAttackImageSet[3], \
        "Tommy Lee Jones", FRIENDLY ,8, 0, 3, 6, 10)
    #SuitSprite.RegisterAction(AOEAttack, 'The character conjures Feline Flames!', [],[])
    SuitSprite.RegisterAction(ATTACK, 'The character hits an adjacent target with the butt of his pistol',[],[])
    Characters.add(SuitSprite)

    ArcherDeathImageSet=sprites.load_sliced_sprites(64,64,'images/archer/archer_death.png')    
    ArcherImageSet = sprites.load_sliced_sprites(64, 64, 'images/archer/archer_walk.png')
    ArcherAttackImageSet = sprites.load_sliced_sprites(64, 64, 'images/archer/archer_attack.png')
    ArcherSprite = Actor((15-.5)*tileSize, (4-1)*tileSize, ArcherImageSet[0], ArcherImageSet[1], ArcherImageSet[2], ArcherImageSet[3], \
        DeathImageSet[0], ArcherAttackImageSet[0], ArcherAttackImageSet[1], ArcherAttackImageSet[2], ArcherAttackImageSet[3], \
        "Presto", FRIENDLY ,6, 3, 4, 7, 8)
    #ArcherSprite.RegisterAction(ATTACK, 'The character hits an adjacent target with the butt of his pistol',[],[])
    ArcherSprite.RegisterAction(RANGED, 'The character releases a quick bolt!', [],[])
    Characters.add(ArcherSprite)
    
    MageDeathImageSet=sprites.load_sliced_sprites(64,64,'images/mage/mage_death.png')
    MageImageSet = sprites.load_sliced_sprites(64, 64, 'images/mage/mage_walk.png')
    MageAttackImageSet = sprites.load_sliced_sprites(64, 64, 'images/mage/mage_spell.png')
    MageSprite = Actor((16-.5)*tileSize, (4-1)*tileSize, MageImageSet[0], MageImageSet[1], MageImageSet[2], MageImageSet[3], \
        DeathImageSet[0], MageAttackImageSet[0], MageAttackImageSet[1], MageAttackImageSet[2], MageAttackImageSet[3], \
        "Presto", FRIENDLY ,2, 2, 3, 6, 8)
    #MageSprite.RegisterAction(ATTACK, 'The character hits an adjacent target with the butt of his pistol',[],[])
    MageSprite.RegisterAction(AOE, 'The character conjures Feline Flames!', [],[])
    Characters.add(MageSprite)
    
    

    # mainloop variables for gameplay
    frames_per_sec = 60.0
    clock = pygame.time.Clock()
    running = True
    paused=False
    grid=False #Debugging boolean to draw a grid

    #Game Turns Controller
    PlayTurn=Turn(GameBoard)

    #the Bad gusys
    PlayTurn.SpawnSkeleton(16,7)
    PlayTurn.SpawnPortal(2,6)
    
    #Picks the first character
    CurrentSprite=PlayTurn.Next()
    CurrentSpriteInfo = CharacterInfo(PlayTurn.CurrentSprite(), myfont, screen_height)
    myMenu = Menu("Action:", PlayTurn.CurrentSprite().GetActions(), myfont, 50, 150, 200, 200)


    #Music
    BGvolume=.05 #this is a number between 0 and 1
    BackgroundMusic =pygame.mixer.Sound("sound/wandering_around.wav")
    BackgroundMusic.play(loops=-1)
    BackgroundMusic.set_volume(BGvolume)


    ##The Main Game Loop 
    while running:
        clock.tick(frames_per_sec)
        time = pygame.time.get_ticks()

        #checks for levelups,
        if CurrentSprite != PlayTurn.CurrentSprite() and paused==False:# we are between turns
            for actor in Characters:
                if actor.LevelUp():
                    print 'levelup!'
                    paused=True
                    LevelUpWindow = LevelUpScreen(actor, actor.Name()+'has gained a level!', myfont, 100,100,100,100)
                    continue
                    

        #update the UI
        if CurrentSprite != PlayTurn.CurrentSprite() and PlayTurn.CurrentSprite !=[]:
            CurrentSprite = PlayTurn.CurrentSprite()
            myMenu = Menu("Action:", CurrentSprite.GetActions(), myfont, 50, 150, 200, 200)
            CurrentSpriteInfo = CharacterInfo(CurrentSprite, myfont, screen_height)
        
        #Move the camera manually with "wasd"


        #used these if you want to be able to hold down the mouse/keys
        pressedKeys=pygame.key.get_pressed() #actions that come from the keyboard This is for holding down
        pressedMouse = pygame.mouse.get_pressed() # mouse pressed event 3 booleans [button1, button2, button3]

        mouse_pos_x, mouse_pos_y = pygame.mouse.get_pos() #mouse coordinates
        tile_x, tile_y = mouse_pos_x// tileSize, mouse_pos_y // tileSize #note the board translates coordinates depending on the location of the camera
        for event in pygame.event.get():       
 
            if event.type == QUIT or event.type == pygame.QUIT or (pressedKeys[K_w] and pressedKeys[K_LMETA]):
                running = False
                pygame.quit()
                sys.exit()

            action = myMenu.input(event) #actions that come from the menu
            if not (hasattr(event, 'key') or event.type==KEYDOWN or hasattr(event, 'button') or event.type==MOUSEBUTTONUP): continue
            #print(action)
            
            #UI or turn events
            if PlayTurn.CurrentSprite().Alignment() == HOSTILE:#if it is the enemy turn then turn off the inputs
                pass

                
            elif (action == 'Move' or pressedKeys[K_x]) and PlayTurn.Mode()==[]:
                PlayTurn.MoveMode()

            elif (action == 'Wait' or pressedKeys[K_c]): #note right now this overrides whatever mode you were in, a back button might be nice 
                PlayTurn.EndTurn()
            elif(action == "Cancel" or pressedKeys[K_v]):
                PlayTurn.CancelMode()
            elif (action in actionList or pressedKeys[K_z]) and PlayTurn.Mode()==[]:#right now it brings up a target list
                PlayTurn.ActionMode(action)


            #elif (action == AOEAttack and PlayTurn.Mode()==[]):
            #    PlayTurn.AOEMode()
            '''
            #single keystroke type inputs
            if event.key ==K_RIGHT: pygame.mouse.set_pos([mouse_pos_x+tileSize, mouse_pos_y])
            elif event.key == K_LEFT: pygame.mouse.set_pos([mouse_pos_x-tileSize, mouse_pos_y])
            elif event.key == K_UP: pygame.mouse.set_pos([mouse_pos_x, mouse_pos_y-tileSize])
            elif event.key == K_DOWN: pygame.mouse.set_pos([mouse_pos_x, mouse_pos_y+tileSize])
            '''
            #Debug
            if pressedKeys[K_g]: grid= not grid #DEBUG: this toggles the grid
            
        if pressedKeys[K_d]: GameBoard.MoveCamera(tileSize,0, relative=True) #right
        elif pressedKeys[K_a]: GameBoard.MoveCamera(-tileSize,0, relative=True)#left
        elif pressedKeys[K_w]: GameBoard.MoveCamera(0,-tileSize, relative=True) #up
        elif pressedKeys[K_s]: GameBoard.MoveCamera(0,tileSize, relative=True) #down

        elif pressedKeys[K_RIGHTBRACKET]:
            if BGvolume<1:
                BGvolume+=.05
        elif pressedKeys[K_LEFTBRACKET]:
            if BGvolume>0:
                BGvolume-=.05
        BackgroundMusic.set_volume(BGvolume)

        
        if pressedMouse[0]:
            #print(GameBoard.getTile(mouse_pos_x, mouse_pos_y))
            #Seed what you clicked on and what turn mode you are in, then determins what to do
            if PlayTurn.Mode()==ATTACK and GameBoard.getTile(mouse_pos_x, mouse_pos_y)[0]=="Actor":
                PlayTurn.Attack(GameBoard.getTile(mouse_pos_x, mouse_pos_y)[1])
                #CurrentSprite.Attack(GameBoard.getTile(mouse_pos_x, mouse_pos_y)[1])
                
            elif PlayTurn.Mode()==MOVE: #asks the game controller if the CurrentSprite can move there
                PlayTurn.Move(GameBoard.getTile(mouse_pos_x, mouse_pos_y)[2][0],GameBoard.getTile(mouse_pos_x, mouse_pos_y)[2][1] )
            elif PlayTurn.Mode()==AOE:
                PlayTurn.AOEAttack(tile_x, tile_y)
                    
                    
        '''
            #Debugging Spawn a PigMan
            #Bebop's Brood
            elif event.key == K_1: 
                NewPigSprite = Actor((20-.5)*tileSize, (20-1)*tileSize, PigImageSet[1], PigImageSet[0], PigImageSet[2], PigImageSet[3],"Pig Spawn" ,2, 2, 5, 5, 60)
                Characters.add(NewPigSprite)                  
                sprite_layers[objectlayer].add_sprites(Characters)
            elif event.key == K_2:
                Characters.remove(NewPigSprite)
                sprite_layers[objectlayer].remove_sprite(NewPigSprite)
        '''
        
        Characters.update(time)  
        GameBoard.update(time)
        if GameBoard.Animating() and paused:
            print('Gameboard is animating! Please be patient!')
            pass
        else:
            PlayTurn.update()


        #DEBUGGING: Grid
        if grid:#on a press of "g" the grid will be toggled
            for i in range(GameBoard._tileWidth):#draw vertical lines
                pygame.draw.line(screen, (0,0,0), (i*tileSize,0),(i*tileSize,GameBoard._width))
            for j in range(GameBoard._tileHeight):#draw horizontal lines
                pygame.draw.line(screen, (20,0,20), (0,j*tileSize),(GameBoard._height,j*tileSize))

        #moves the menu to the right if the camera is to the far left.
        if GameBoard.camTile()[0] < (myMenu.rect[0]+myMenu.rect[2])// tileSize:
            myMenu.rect[0]=screen_width-myMenu.rect[2]-50
            CurrentSpriteInfo.rect[0]=screen_width-CurrentSpriteInfo.rect[2]
        else:
            myMenu.rect[0]=50
            CurrentSpriteInfo.rect[0]=0
        if PlayTurn.CurrentSprite().Alignment()==FRIENDLY:
            screen.blit(myMenu.surface, myMenu.rect)
            
        screen.blit(CurrentSpriteInfo.surface, CurrentSpriteInfo.rect)
        
        pygame.display.flip()

#  -----------------------------------------------------------------------------


    


#  -----------------------------------------------------------------------------
#  -----------------------------------------------------------------------------
if __name__ == '__main__':

    main()
