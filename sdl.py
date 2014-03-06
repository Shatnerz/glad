import logging

import pygame

import glad

from util import Vector

import os

from util import cycleList

class App(object):
  """Basic application that handles OS events and provides a rendering
  surface"""
  
  def __init__(self):
    
    self.alive = True    #keep the app alive
    
    pygame.init()    
    
    self.screenSize = (800,600)
    self.screen = pygame.display.set_mode(self.screenSize,pygame.HWPALETTE,8) #set display to 8 bit so color cycling works
    
    self.simpleClock = pygame.time.Clock()
    self.inputInterface = InputInterface()   
    
    self.desiredFPS = 30.0
    self.actualFPS = 30.0
    
    #Color Cycling
    self.palette = glad.palette
    self.palette=[list(i) for i in self.palette]
    self.screen.set_palette(self.palette) #not sure why but avoids problem with colors
    self.cycleTime = 0.1
    self.cycleTimeLeft = self.cycleTime
    
  def getInputInterface(self):
    return self.inputInterface
    
  def getRenderingSurface(self):
    return self.screen
  
  def getTimeDelta(self):    
    #For now, just return 1/framerate for simplicity    
    return 1.0 / self.desiredFPS
  
  def isRunning(self):
    return self.alive
  
  def exit(self):
    self.alive = False
    
  def cycleColor(self):
    """Cycles all the needed colors on the display index"""
    colors = {'ORANGE'  : 224,
              'BLUE'    : 208}
    
    for x in colors:
      start = colors[x]
      self.palette[start:start+16] = cycleList(self.palette[start:start+16],-1)
    
    pygame.display.set_palette(self.palette)
    
  def updateColorCyling(self):
    
    time = self.getTimeDelta()
    
    self.cycleTimeLeft -= time
    
    while self.cycleTimeLeft <= 0:
      #print 'a'
      self.cycleColor()
      self.cycleTimeLeft += self.cycleTime
    
  def update(self):
        
    #check for an exit event
    for event in pygame.event.get():
    
      if event.type == pygame.QUIT:
        logging.info('pygame exit event detected')
        self.exit()   
      else:
        #update the state of keys, joysticks, etc...
        self.inputInterface.update(event) 
      
    #limit the game speed
    
    self.simpleClock.tick(self.desiredFPS)    
    self.actualFPS = self.simpleClock.get_fps()
    self.updateColorCyling()
    
class Camera(object):
  """Breaks the screen into windows we can draw to. Will be used
  for handling multiple players, and things like shaking the screen"""
  def __init__(self, windowRect=None, screen=None):
    
    self.windowRect = windowRect
    
    #For now, only show the top left of the world
    self.worldRect = windowRect[:]
    
    #must use an SDL rect for the subsurface
    self.screen = pygame.Surface.subsurface(screen,windowRect)
    
    #Don't follow anything in the beginning
    self.objectFollowed = None
    
    self.worldBoundingRect = None
    
    self.overlay = Overlay(self.screen)
    self.hud = HUD(self.screen, self)
    
    
    
  def update(self, world):
    """Update the camera's position. The 'world' argument is used
    so that the camera will not center when an object is near the edge"""
    
    if self.objectFollowed:
      
      rW = self.worldRect[2] - self.worldRect[0]
      rH = self.worldRect[3] - self.worldRect[1] 
      
      #get center of object
      ox,oy = self.objectFollowed.getPos()
      
      ax = ox - rW/2.0
      #bx = ox + rW/2.0
      
      ay = oy - rH/2.0
      #by = oy + rH/2.0
      
      br = world.getBoundingRect()      
      
      #TODO: what to do if the camera can view the entire
      # world at once
      if ax < br.x1 - 10: #Camera at left edge
        ax = br.x1 - 10
      elif ax > br.x2 - rW + 10: #Camera at right edge
        ax = br.x2 - rW + 10
        
      #print ax, br[2] - rW
        
      if ay < br.y1 - 10: #camera at top edge
        ay = br.y1 - 10
      elif ay > br.y2 - rH + 10: #Camera at bottom edge
        ay = br.y2 - rH + 10
      
      self.worldRect = (ax,
                        ay,
                        ax+rW,
                        ay+rH)
    
  
  def followObject(self, obj):
    self.objectFollowed = obj

  def setWorldBoundingRect(self, r):
    """In world coordinates, the bounding box for the world.
    The camera won't center an object if he is near
    the boundary, so that the player can see more"""
    
    self.worldBoundingRect = r    
    
    
class Overlay(object):
  
  def __init__(self, surface):
    
    self.fontFilename = pygame.font.get_default_font()
    self.fontSize = 12
    
    self.font = pygame.font.Font(self.fontFilename, self.fontSize)
    
    self.surface = surface
      
        
  def drawLineOfText(self, text, pos, antialias, color, background=None):
    
    newSurf = self.font.render(text, 
                               antialias, 
                               color, 
                               background)
    
    #don't draw the background pixels when we blit
    newSurf.set_colorkey(background)
    
    self.surface.blit(newSurf, pos)
    
    
  def drawText(self, text, pos):
    
    xPos, yPos = pos
    
    
    for line in text.split('\n'):
      self.drawLineOfText(line, (xPos,yPos),False,(255,255,255),(0,255,0))
      
      yPos += self.font.get_linesize()  
    
  def draw(self):    
    
    numObjects = len(glad.world.objectList)    
    
    fps = glad.app.actualFPS
    
    
    text = '# objects: %d' % numObjects
    text += '\nFPS: %0.2f' % fps
    
    
    self.drawText(text, (700,50))   
    
    
class HUD(Overlay):
  """Head's up display showing general info on the object being followed by the camera"""
  
  def __init__(self, surface, cam):
    Overlay.__init__(self,surface)
    #self.target = target #only keeps original target of none
    self.cam = cam
    
  def draw(self):
    text = 'HUD'
    text += '\n' + str( type(self.cam.objectFollowed) )
    
    object = self.cam.objectFollowed
    
    #Team
    text += '\nTeam: '
    if object.life:
      text += str(object.team)
    else:
      text += 'NA'
    text += '\n'
    #Life
    text += '\nLife: '
    if object.life:
      text += str(object.life)
    else:
      text += 'NA'
    #Mana
    text += '\nMana: '
    if object.life:
      text += str(object.mana)
    else:
      text += 'NA'
    
    self.drawText(text, (50,25))
    #text =+ 'Life: %l' % self.target.life

class InputInterface(object):
  """Records input from the keyboard"""
  
  def __init__(self):
    self.keysPressed = set()
    self.keysTapped = set() #keys just pressed and not being held yet
    
  def update(self, event):    

    self.keysTapped.clear()

    if event.type == pygame.KEYDOWN:
      self.keysPressed.add(event.key)
      
      #Quit if esc is pressed
      if event.key == pygame.K_ESCAPE:
        exit()
      
    elif event.type == pygame.KEYUP:
      #BUGFIX: use discard, because keys may be pressed at program start
      self.keysPressed.discard(event.key)
      
    self.keysTapped=self.keysPressed.copy()
    
  def isKeyPressed(self, key):
    return key in self.keysPressed

  def isKeyTapped(self, key):
    if key in self.keysTapped:
      self.keysTapped.remove(key)
      return True
    else: return False
    
class Renderer(object):
  """Handles drawing everything to the screen."""
  
  tileSize = (32,32)
  
  tileDict = {0: 'PIX_H_WALL1',
              1: 'PIX_GRASS1',
              2: 'PIX_WATER1',
              3: 'PIX_VOID1',
              4: 'PIX_WALL2',
              5: 'PIX_WALL3',
              6: 'PIX_FLOOR1',
              7: 'PIX_WALL4',
              8: 'PIX_WALL5',
              9: 'PIX_CARPET_LL',
              10: 'PIX_CARPET_L',
              11: 'PIX_CARPET_B',
              12: 'PIX_CARPET_LR',
              13: 'PIX_CARPET_UR',
              14: 'PIX_CARPET_U',
              15: 'PIX_CARPET_UL',
              16: 'PIX_GRASS2',
              17: 'PIX_GRASS3',
              18: 'PIX_GRASS4',
              19: 'PIX_WATER2',
              20: 'PIX_WATER3',
              21: 'PIX_PAVEMENT1',
              22: 'PIX_WALLSIDE1',
              23: 'PIX_WALLSIDE_L',
              24: 'PIX_WALLSIDE_R',
              25: 'PIX_WALLSIDE_C',
              26: 'PIX_WALL_LL',
              27: 'PIX_PAVESTEPS1',
              28: 'PIX_BRAZIER1',
              29: 'PIX_WATERGRASS_LL',
              30: 'PIX_WATERGRASS_LR',
              31: 'PIX_WATERGRASS_UL',
              32: 'PIX_WATERGRASS_UR',
              33: 'PIX_CARPET_M',
              34: 'PIX_CARPET_M2',
              35: 'PIX_PAVESTEPS2',
              36: 'PIX_PAVESTEPS2L',
              37: 'PIX_PAVESTEPS2R',
              38: 'PIX_WALLTOP_H',
              39: 'PIX_TORCH1',
              40: 'PIX_TORCH2',
              41: 'PIX_TORCH3',
              42: 'PIX_CARPET_R',
              43: 'PIX_FLOOR_PAVEL',
              44: 'PIX_FLOOR_PAVER',
              45: 'PIX_FLOOR_PAVEU',
              46: 'PIX_FLOOR_PAVED',
              47: 'PIX_GRASSWATER_LL',
              48: 'PIX_GRASSWATER_LR',
              49: 'PIX_GRASSWATER_UL',
              50: 'PIX_GRASSWATER_UR',
              51: 'PIX_PAVEMENT2',
              52: 'PIX_PAVEMENT3',
              53: 'PIX_COLUMN1',
              54: 'PIX_COLUMN2',
              55: 'PIX_TREE_B1',
              56: 'PIX_TREE_M1',
              57: 'PIX_TREE_T1',
              58: 'PIX_TREE_ML',
              59: 'PIX_DIRT_1',
              60: 'PIX_DIRTGRASS_UL1',
              61: 'PIX_DIRTGRASS_UR1',
              62: 'PIX_DIRTGRASS_LL1',
              63: 'PIX_DIRTGRASS_LR1',
              64: 'PIX_PATH_1',
              65: 'PIX_PATH_2',
              66: 'PIX_PATH_3',
              67: 'PIX_BOULDER_1',
              68: 'PIX_WATERGRASS_U',
              69: 'PIX_WATERGRASS_L',
              70: 'PIX_WATERGRASS_R',
              71: 'PIX_WATERGRASS_D',
              72: 'PIX_COBBLE_1',
              73: 'PIX_COBBLE_2',
              74: 'PIX_PATH_4',
              75: 'PIX_COBBLE_3',
              76: 'PIX_COBBLE_4',
              77: 'PIX_WALL_ARROW_GRASS',
              78: 'PIX_WALL_ARROW_FLOOR',
              79: 'PIX_GRASS1_DAMAGED',
              80: 'PIX_TREE_MR',
              81: 'PIX_TREE_MT',
              82: 'PIX_GRASS_DARK_1',
              83: 'PIX_GRASS_DARK_LL',
              84: 'PIX_GRASS_DARK_UR',
              85: 'PIX_GRASS_RUBBLE',
              86: 'PIX_GRASS_DARK_2',
              87: 'PIX_GRASS_DARK_3',
              88: 'PIX_GRASS_DARK_4',
              89: 'PIX_BOULDER_2',
              90: 'PIX_BOULDER_3',
              91: 'PIX_BOULDER_4',
              92: 'PIX_GRASS_DARK_B1',
              93: 'PIX_GRASS_DARK_B2',
              94: 'PIX_GRASS_DARK_BR',
              95: 'PIX_GRASS_DARK_R1',
              96: 'PIX_GRASS_DARK_R2',
              97: 'PIX_WALL_ARROW_GRASS_DARK',
              98: 'PIX_DIRTGRASS_DARK_UL1',
              99: 'PIX_DIRTGRASS_DARK_UR1',
              100: 'PIX_DIRTGRASS_DARK_LL1',
              101: 'PIX_DIRTGRASS_DARK_LR1',
              102: 'PIX_WALLSIDE_CRACK_C1',
              103: 'PIX_DIRT_DARK_1',
              104: 'PIX_GRASS_LIGHT_1',
              105: 'PIX_GRASS_LIGHT_TOP',
              106: 'PIX_GRASS_LIGHT_RIGHT_TOP',
              107: 'PIX_GRASS_LIGHT_RIGHT',
              108: 'PIX_GRASS_LIGHT_RIGHT_BOTTOM',
              109: 'PIX_GRASS_LIGHT_BOTTOM',
              110: 'PIX_GRASS_LIGHT_LEFT_BOTTOM',
              111: 'PIX_GRASS_LIGHT_LEFT',
              112: 'PIX_GRASS_LIGHT_LEFT_TOP',
              113: 'PIX_CLIFF_BOTTOM',
              114: 'PIX_CLIFF_TOP',
              115: 'PIX_CLIFF_LEFT',
              116: 'PIX_CLIFF_RIGHT',
              117: 'PIX_CLIFF_BACK_1',
              118: 'PIX_CLIFF_BACK_2',
              119: 'PIX_CLIFF_BACK_L',
              120: 'PIX_CLIFF_BACK_R',
              121: 'PIX_CLIFF_TOP_L',
              122: 'PIX_CLIFF_TOP_R',
              123: 'PIX_JAGGED_GROUND_1',
              124: 'PIX_JAGGED_GROUND_2',
              125: 'PIX_JAGGED_GROUND_3',
              126: 'PIX_JAGGED_GROUND_4',
              127: 'PIX_CARPET_SMALL_HOR',
              128: 'PIX_CARPET_SMALL_VER',
              129: 'PIX_CARPET_SMALL_CUP',
              130: 'PIX_CARPET_SMALL_CAP',
              131: 'PIX_CARPET_SMALL_LEFT',
              132: 'PIX_CARPET_SMALL_RIGHT',
              133: 'PIX_CARPET_SMALL_TINY'}
  
  def __init__(self):
    
    self.screen = pygame.display.get_surface()
    
    self.cameraList = []
    
    #For now, just setup 1 camera that occupies the whole screen
    
    #Set camera to origin, size of rendering surface
    w,h = self.screen.get_size()
    c = Camera(windowRect = (0,0,w,h),
               screen = self.screen)
    self.cameraList.append(c)
    
    
    self.bgSurface = None
    
  def draw(self, world):
    """Draw each of the camera windows onto the rendering surface"""
    
    for cam in self.cameraList:     
      
      #update the cameras
      cam.update(world)
      
      #first 2 coords are the pos
      offset = Vector(cam.worldRect[:2])
      offset *= -1      
      
      screen = cam.screen      
      
      #make bg green for debugging purposes
      screen.fill((0,255,0))
    
      #draw the world, offset by the camera position      
      #self.drawTiles(world.tileGrid, screen, offset)
      self.drawBg(world.tileGrid, screen, offset)

      #draw the objects in the world
      world.draw(screen, offset)        
      #draw the overlay on top of the world
      cam.overlay.draw()
      cam.hud.draw()
  
      #using double buffered display, so flip
      pygame.display.flip()
      
      
  def drawBg(self, tileGrid, screen, offset):
    
    #TODO: we should initialize somemplace else, like when the level loads, not
    # on the first time we draw the bg    
    if self.bgSurface is None:
      
      w, h = Renderer.tileSize
      
      self.bgSurface = pygame.Surface((w * len(tileGrid[0]),h*len(tileGrid))).convert()
      
      Renderer.drawTiles(tileGrid,self.bgSurface,(0,0))
      
    #TODO: increase speed by using area rect to draw only portion of source?
    screen.blit(self.bgSurface, offset)    
    
      
  @staticmethod
  def drawTiles(tileGrid, screen, offset):
         
    for row in range(len(tileGrid)):      
      for col in range(len(tileGrid[row])):       
        
        #convert the # into a resource name
        tileName = Renderer.tileDict[tileGrid[row][col]]
        
        #paint the resource onto the screen, offset by the
        # where the 'camera' is
        
        left = Renderer.tileSize[0] * col + offset[0]
        top = Renderer.tileSize[1] * row + offset[1]       
        
        tile = glad.resource.get(tileName)
        #tile = glad.resource.resourceDict['ANIM_FIRE_ELEM_TEAM_4_MOVERIGHT'].frameList[0] #testing
        
        screen.blit(tile, (left,top,
                          Renderer.tileSize[0],
                          Renderer.tileSize[1]))
        #Does not blit top line of black pixels
        #screen.blit(tile, (left,top),((0,1),
        #                              (Renderer.tileSize[0],
        #                               Renderer.tileSize[1])))
        


