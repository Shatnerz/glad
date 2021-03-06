
import os.path

import pygame

import glad

import animation

import copy #solves issues with copying list
  
class AbstractResource(object):
  """Abstract class used to keep resource specific subclasses organized"""
  
  def __init__(self, filename, **kwargs):
    self.data = None
    self.kwargs = kwargs
    self.filename = filename
  
  def load(self):
    raise NotImplementedError()
  
  def get(self):
    assert self.data is not None    
    return self.data
  
class ImageResource(AbstractResource):
  """Handles images and converts them to pygame surfaces"""  
  
  def load(self, tile = False, **kwargs):
    
    kwargs = self.kwargs
    filename = self.filename
    
    if tile:    
      w, h = kwargs['size']
    
    origSurface = pygame.image.load(filename).convert(8)
    
    #we have to get the subsurface because the first row is black pixels
    if tile:
      self.data = origSurface.subsurface(0,1,w,h)
    else:
      self.data = origSurface
        
class SoundResource(AbstractResource):
  """Handles sounds"""
  
  def load(self, **kwargs):
    
    kwargs = self.kwargs
    filename = self.filename
    
    sound = pygame.mixer.Sound(filename)
    
    self.data = sound
    
  def play(self, pos):
    """Play the sound"""
    glad.sound.play(self.data, pos)
    
class ResourceManager(object):
  """Keep track of all the images we need and whether or not they are
  loaded into memory"""
  
  def __init__(self):   
  
    self.resourceDict = {}
  
  def register(self, name, filename,tile = False, sound = False, **kwargs):
    
    if not sound:    
      #TODO assumes it's an image right now
      r = ImageResource(filename,**kwargs)    
      self.resourceDict[name] = r
      #TODO: for now just load immediately, this may change in the future
      r.load(tile, **kwargs)
    
    if sound:
      r = SoundResource(filename, **kwargs)
      self.resourceDict[name] = r
      r.load()
    
  def registerImage(self, name, filename, **kwargs):
    pass
  
  def registerTile(self, name, filename, **kwargs):
    """TODO: This is a hack, and should be removed in the future."""
    pass
  
  def registerAnimation(self, name, anim):
    self.resourceDict[name] = anim
  
  def get(self, name):
    return self.resourceDict[name].get()
   
  

class AnimationManager(object):
  
  def __init__(self):
    self.animationDict = {}       
      
      
def registerGladResources():
  """Convenience function that loads all gladiator resources """
  
  registerGladTiles()
  
  registerGladCharacters()
  
  registerGladProjectiles()
  
  registerGladImages()
  
  registerGladAnimations()
  
  registerGladSounds()


def registerGladAnimations():
  """Load all animations into game"""    
  #Projectiles
  createGladAnimations('meteor', 'METEOR', 8, 'proj')
  createGladAnimations('rock', 'ROCK', 12, 'proj')
  createGladAnimations('hammer', 'HAMMER', 12, 'proj')
  createGladAnimations('fire', 'FIREBALL', 8, 'proj')
  createGladAnimations('arrow', 'ARROW', 12, 'proj')
  createGladAnimations('boulder1', 'BOULDER', 1, 'proj', spin=True)
  createGladAnimations('farrow', 'FIRE_ARROW', 16, 'proj')
  createGladAnimations('bone1', 'BONE', numFrames=8, type='proj', spin=True)
  createGladAnimations('knife', 'KNIFE', 8, 'proj', spin=True)
  createGladAnimations('sparkle', 'SPARKLE', 12, 'proj', spin=True)
  #Team colored projectiles
  for teamNum in range(5):
    createGladAnimations('lightnin', 'LIGHTNING', 8, 'proj',team=teamNum)
    createGladAnimations('sl_ball', 'SLIME_BALL', 12, 'proj', slime=True,team=teamNum)
    
  #Characters
  #createGladAnimations('archer', 'ARCHER')
  #createGladAnimations('archmage', 'ARCHMAGE')
  #createGladAnimations('barby', 'BARBARIAN')
  #createGladAnimations('b_slime', 'BIG_SLIME', slime=6) #slime=x loads slime animation with x frames used to movement
  #createGladAnimations('cleric', 'CLERIC')
  #createGladAnimations('druid', 'DRUID')
  #createGladAnimations('elf', 'ELF')
  #createGladAnimations('faerie', 'FAERIE')
  for teamNum in range(5):
    createGladAnimations('firelem', 'FIRE_ELEM',team=teamNum)
    createGladAnimations('footman', 'SOLDIER', team=teamNum)
    
    #createGladAnimations('ghost', 'GHOST')
    #createGladAnimations('golem', 'GOLEM')
    #createGladAnimations('mage', 'MAGE')
    #createGladAnimations('m_slime', 'MEDIUM_SLIME', slime=12)
    #createGladAnimations('orc', 'ORC')
    #createGladAnimations('orc2', 'ORC_CAPTAIN')
    #createGladAnimations('skeleton', 'SKELETON')
    createGladAnimations('s_slime', 'SMALL_SLIME', slime=8, team=teamNum)
    #createGladAnimations('thief', 'THIEF')
  
  ##################################### NON ANIMATED IMAGES########################################
  #still need tree, bonepile, key, heart, portal, tent
  createGladAnimations('blood', 'BLOOD', 4, type='other', anim=False)
  createGladAnimations('bottle', 'POTION', 12, type='other', anim=False, names=['RED','GREEN','BLUE','YELLOW','PURPLE','CYAN',
                                                                                'BROWN','PINK','DARKGREEN','DARKPURPLE','YELLOWORANGE','LIGHTBLUE'])
                                                                                #These potions should be named better
  createGladAnimations('bar1', 'BAR', 2, type='other', anim=False, names=['GOLD', 'SILVER'])
  createGladAnimations('food1', 'FOOD', 1, type='other', anim=False)
  ################################################################################################
  
def registerGladSounds():
  """Load all sounds into the game"""
  
  titleFolder = 'resources/sound'
  
  soundList = ['blast1',
               'bolt1',
               'boom',
               'charge',
               'clang',
               'die1',
               'die2',
               'eat',
               'explode1',
               'faerie1',
               'fwip',
               'heal1',
               'money',
               'roar',
               'teleport',
               'twang',
               'yo']
  
  for name in soundList: 
    fullname = os.path.join(titleFolder, name+'.wav')
    glad.resource.register(name, fullname, sound=True)  
    #glad.resource.resourceDict[name].data.play()

def createGladAnimations(name, name2, numFrames=0, type='char', **kwargs): #note frames are typically 8 for projectile, name2 will not be needed if i change file names
  #Now loads color for everything that needs it
  #For team color add argument. Right now default to team 0 which is red (should be 7 which loads grey)
  #added type and name2 and **kwargs
  #name2 is temporary, just need to rename the images
  #checks kwargs to see if spinning and loads spinning animation
  #loads anything after normal frames as SPECIAL, must have less than 36 frames total, otherwise treated as mage
  #EVERYTHING LOADS NOW EXCEPT SLIME SPLIT, and maybe slime movement is off since only 3 frames are used
  #Relies on number a frames for info - probably not the best idea
  """Function that loads any necessary animation from a sprite sheet, adds team color, and registers it"""
  
  #Get sprite sheet and mask (masks are for later when we add color)
  spriteSheet = glad.resource.get(name).copy() #need a copy so setting the color doesnt overwrite original
  #mask = glad.resource.get(name+'_mask') #only if needs color #not used anymore
  
  #check if team (color) is specified
  team = 0
  for key in kwargs:
    if key == 'team': #load spinning projectile    
      team = kwargs[key]
  
  #Get width to determine how to break up frames
  sheetWidth = spriteSheet.get_width()
  #Determine sprite width
  #Search for pixel denoting width if number of frames is set to 0
  if numFrames==0:
    spriteWidth = 0
    for x in range(sheetWidth):
      if spriteSheet.get_at((x,0)) != (0,0,0,255): #had to change, when i change to 8-bit, the white pixel must change
        spriteWidth = x+1
        numFrames = sheetWidth/spriteWidth
        break
  else:
    spriteWidth = sheetWidth/numFrames
    #Determine height and size
  spriteHeight = spriteSheet.get_height() - 1
  spriteSize = (spriteWidth, spriteHeight)
  
#Set team color
  #if type == 'char': #just for now since slime ball needs color too
   # setTeamColor(spriteSheet) #add team number here sometime
    
  #Create a list of frames
  frameList = []
  refPoint = 0 #reference point use to grab the frame
  for sprite in xrange(numFrames):
    frame = spriteSheet.subsurface((refPoint, 1), (spriteWidth, spriteHeight))
    refPoint += spriteWidth
    frameList.append(frame)
    
  #if type == 'char' load as char, 'proj' for proj, 'other' for rest, other will have similar code as spinning
  #HANDLE PROJECTILE ANIMATIONS
  if type == 'proj':
      
    animationReference = {'DOWN' : 0,
                          'UP' : 1,
                          'RIGHT' : 2,
                          'LEFT' : 3,
                          'DOWNLEFT' : 4,
                          'UPRIGHT' : 5,
                          'DOWNRIGHT' : 6,
                          'UPLEFT' : 7}
        
    #determine if spinning projectile, slime, or normal
    spin=False
    slime=False
    for key in kwargs:
      if key == 'spin' and kwargs[key]== True: #load spinning projectile
        spin=True
      elif key == 'slime' and kwargs[key] == True:
        slime=True
    #handle spinning proj
    if spin:
      anim = frameList
      glad.resource.registerAnimation('ANIM_'+name2+'_SPIN', animation.Animation(anim)) #note - no spinning proj have team color atm
    #handle slime proj
    elif slime:
      setTeamColor(spriteSheet,team)
      anim = []
      frames=7
      for x in range(frames):
        anim.append(frameList[x])
        counter = 5
        while counter > 0:
          anim.append(frameList[counter])
          counter -= 1
        glad.resource.registerAnimation('ANIM_'+name2+'_TEAM_'+str(team), animation.Animation(anim))
    #handle typical projectile
    else:
      #Determine the number of frames per animation
      frames = 1 #frames/animation is typically 1
      if numFrames >= 16 and numFrames%16==0: #if projectile has 16 or more frames total it is likely animated
        frames = numFrames/8
      #Create animations
      for direction in animationReference:
        anim = []
        x = animationReference[direction]
        counter = 0
        while counter < frames:               
          anim.append(frameList[x+counter*8])
          counter += 1
        if name2 == 'LIGHTNING': #Quick fix to add color to lightning
          setTeamColor(spriteSheet,team)
          glad.resource.registerAnimation('ANIM_'+name2+'_TEAM_'+str(team)+'_MOVE'+direction, animation.Animation(anim))
        else:
          glad.resource.registerAnimation('ANIM_'+name2+'_MOVE'+direction, animation.Animation(anim))
  
  #HANDLE CHARACTER ANIMATIONS                  
  elif type == 'char':
    #Set team color first
    setTeamColor(spriteSheet,team)
    #Determine how to handle sprite sheet
    slime = False
    for key in kwargs:
      if key == 'slime':
        slime=True
        frames=kwargs[key]
    #handle slimes
    if slime:
      anim = []
      for x in range(frames):
        anim.append(frameList[x])
      counter = frames-2
      while counter > 0:
        anim.append(frameList[counter])
        counter -= 1
      glad.resource.registerAnimation('ANIM_'+name2+'_TEAM_'+str(team)+'_MOVE', animation.Animation(anim))
    #handle non-slimes
    else:
      #NONMAGES
      if numFrames < 36: #normal sprites have 24, skeleton has 24+4 for burrow, mages have 36, slimes
        animationReference = {'DOWN' : 0, #assuming this is the same for all, which it is except for mage
                              'UP' : 1,
                              'RIGHT' : 2,
                              'LEFT' : 3,
                              'DOWNLEFT' : 12,
                              'UPRIGHT' : 13,
                              'DOWNRIGHT' : 14,
                              'UPLEFT' : 15}
        for direction in animationReference: #CREATE FUNCTION HERE SINCE I USE THE SAME FOR MAGES
          #Walking animations
          x = animationReference[direction]
          anim = createCharWalkAnim(direction, x, frameList)
          glad.resource.registerAnimation('ANIM_'+name2+'_TEAM_'+str(team)+'_MOVE'+direction, animation.Animation(anim))
          #glad.resource.registerAnimation('ANIM_'+name2+'_MOVE'+direction, animation.Animation(anim))
          #Attack animation
          attackAnim = []
          attackAnim.append(anim[0])
          attackAnim.append(anim[1])
          glad.resource.registerAnimation('ANIM_'+name2+'_TEAM_'+str(team)+'_ATTACK'+direction, animation.Animation(attackAnim))
          #glad.resource.registerAnimation('ANIM_'+name2+'_ATTACK'+direction, animation.Animation(attackAnim))
        #Load remaining frames as special animation
        if numFrames > 24: #But not == 36 (that loads mages)
          anim=[]
          for frame in range(24,numFrames):
            anim.append(frameList[frame])
          glad.resource.registerAnimation('ANIM_'+name2+'_TEAM_'+str(team)+'_SPECIAL', animation.Animation(anim))
                  
      #MAGES    
      elif numFrames == 36: #mages have 36   print 'Team color set to ' + str(team) frames
        animationReference = {'DOWN' : 0,
                              'UP' : 1,
                              'RIGHT' : 2,
                              'LEFT' : 3,
                              'DOWNLEFT' : 20,
                              'UPRIGHT' : 21,
                              'DOWNRIGHT' : 22,
                              'UPLEFT' : 23}
        for direction in animationReference: #CREATE FUNCTION HERE SINCE I USE THE SAME AS ABOVE
          #Walking animations
          x = animationReference[direction]
          anim = createCharWalkAnim(direction, x, frameList)
          glad.resource.registerAnimation('ANIM_'+name2+'_TEAM_'+str(team)+'_MOVE'+direction, animation.Animation(anim))
          #Attack animations
          attackAnim = []
          attackAnim.append(frameList[x])
          if x<4:
            attackAnim.append(frameList[x+16])
          else:
            attackAnim.append(frameList[x+12])
          glad.resource.registerAnimation('ANIM_'+name2+'_TEAM_'+str(team)+'_ATTACK'+direction, animation.Animation(attackAnim))
        #Teleport animation
        anim = []
        for frame in range(12,16):
          anim.append(frameList[frame])
        glad.resource.registerAnimation('ANIM_'+name2+'_TEAM_'+str(team)+'_SPECIAL', animation.Animation(anim))
            
  else:
    #THIS IS NOOT COMPLETE, I AM JUST ADDING AS I NEED TO
    
    #other includes:teleport marker, cleric wall,explosion, gas cloud
    #i think i'm going to through in non animated stuff in here too, like blood
    
    sequence = range(numFrames)
    anim = True
    names = None
    
    #kwargs
    #color=True -> add a team color
    #sequence=[ints] -> set a sequence of frame numbers for animation
    #anim=False -> each animation is just 1 frame
    #names=[strings] -> list of names for the animations, otherwise names them with numbers
    
    for x in kwargs:
      if x == 'color': #Color is needed for doors
        if kwargs[x] == True:
          setTeamColor(spriteSheet)
      if x == 'sequence': #Set special order of frames if not sequential
        sequence = kwargs[x]
      if x == 'anim': #Check to see if not actually animated
        if kwargs[x] == False:
          anim = False
      if x == 'names':
        names = kwargs[x]
    
    if anim == False:
      counter = 0
      for frame in frameList:
        anim = [frame]
        if not names and numFrames>1:
          animName = 'ANIM_'+name2+'_'+str(counter)
        elif not names and numFrames==1:
          animName = 'ANIM_'+name2
        elif names:
          animName = 'ANIM_'+name2+'_'+names[counter]
        glad.resource.registerAnimation(animName, animation.Animation(anim))
        #print animName
        counter += 1
    
    
def setTeamColor(spriteSheet, teamNumber=0):
  """Set the appropriate team color for a sprite sheet based off int teamNumber (0-13)"""
  #This could probably be done faster by changing the palette for the spritesheet
  #spriteSheet.set_palette(glad.palette) #not needed since sprites change to 8bit with right palette
  #Go through each pixel and see if it needs change
  for x in range(spriteSheet.get_width()):
    for y in range (spriteSheet.get_height()):
      color = spriteSheet.get_at((x,y))
      counter=248
      for colorToChange in glad.palette[248:]:
        if colorToChange == color:
          spriteSheet.set_at((x,y),(glad.palette[(teamNumber*16+40)+(255-counter)]))
        counter += 1
        
    
def createCharWalkAnim(direction, x, frameList):
  """Orders the frames of the walking animation. x is the position of the first frame"""
  anim = []
  anim.append(frameList[x])
  anim.append(frameList[x+4])
  anim.append(frameList[x])
  anim.append(frameList[x+8])
  return anim
  
  
def registerGladProjectiles():
  """Load all projectiles into the game"""
  
  titleFolder = 'resources/images'
  
  projectileList = ['arrow',
                    'bone1',
                    'boulder1',
                    'farrow',
                    'fire',
                    'hammer',
                    'knife',
                    'lightnin',
                    'meteor',
                    'rock',
                    'sparkle',
                    'sl_ball']
  
  for name in projectileList:
    fullname = os.path.join(titleFolder, name+'.tga')
    glad.resource.register(name, fullname)
    transColor = glad.resource.resourceDict[name].data.get_at((0,1))
    glad.resource.resourceDict[name].data.set_colorkey(transColor)
    

def registerGladCharacters():
  """Load all the characters into the game"""
  
  titleFolder = 'resources/sprites'
  
  #dont need dictionary here
  spriteDict = {'archer': 'archer',
                'archmage': 'archmage',
                'barby': 'barby',
                'b_slime': 'b_slime',
                'cleric': 'cleric',
                'druid': 'druid',
                'elf': 'elf',
                'faerie': 'faerie',
                'firelem': 'firelem',
                'footman': 'footman',
                'ghost': 'ghost',
                'golem': 'golem',
                'mage': 'mage',
                'm_slime': 'm_slime',
                'orc': 'orc',
                'orc2': 'orc2',
                'skeleton': 'skeleton',
                's_slime': 's_slime',
                'thief': 'thief',}
  
  
  #register all sprites and masks for game
  #loads spritesheets and sets the top left corner as transparency
  for name, filename in spriteDict.iteritems():
    spriteFullname = os.path.join(titleFolder+'/spritesheets', filename+'.png')
    glad.resource.register(name, spriteFullname)  
    transColor = glad.resource.resourceDict[name].data.get_at((0,1))
    glad.resource.resourceDict[name].data.set_colorkey(transColor)
    #maskFullname = os.path.join(titleFolder+'/masks', filename+'_mask.png')
    #glad.resource.register(name+'_mask', maskFullname)
    
    #try:
    #  image = pygame.image.load(fullname).convert()
    #  transColor = image.get_at((0,1))
    #  image.set_colorkey(transColor)
    #except pygame.error, msg:
    #  print 'Cannot load image:', fullname
    #  raise SystemExit, msg
    

def registerGladImages():
  """Registers the rest of the images that are not tiles, characters, or projectile"""
  
  folder = 'resources/images/'
  
  imageList = ['bomb1', 'boom1', 'clerglow', 'cloud', 'door', 'expand8', 'marker', 'mshield',
               'telflash', 'tower4', 'tower4b', 'towersm1', 'wave', 'wave2', 'wave3', 'bar1',
               'bigtree', 'blood', 'bonepile', 'bottle', 'food1', 'key', 'lifegem', 'stain',
               'teleport', 'tent', 'tree']
  
  for name in imageList:
    fullname = os.path.join(folder, name+'.tga')
    glad.resource.register(name, fullname)
    transColor = glad.resource.resourceDict[name].data.get_at((0,1))
    glad.resource.resourceDict[name].data.set_colorkey(transColor)
      
def registerGladTiles():
  """This function loads all of the gladiator tiles"""
  #TODO: eventually have all resources here
  #TODO: in future, register automatically, not manually
  
  
  tileFolder = 'resources/tiles/' 
  
  tileSize = (32,32)
  
  tileDict = {'PIX_BOULDER_1': '16stone1.tga',
              'PIX_BOULDER_2': '16stone2.tga',
              'PIX_BOULDER_3': '16stone3.tga',
              'PIX_BOULDER_4': '16stone4.tga',
              'PIX_BRAZIER1': '16braz1.tga',
              'PIX_CARPET_B': '16carpb.tga',
              'PIX_CARPET_L': '16carpl.tga',
              'PIX_CARPET_LL': '16carpll.tga',
              'PIX_CARPET_LR': '16carplr.tga',
              'PIX_CARPET_M': '16carpm.tga',
              'PIX_CARPET_M2': '16carpm2.tga',
              'PIX_CARPET_R': '16carpr.tga',
              'PIX_CARPET_SMALL_CAP': '16cscap.tga',
              'PIX_CARPET_SMALL_CUP': '16cscup.tga',
              'PIX_CARPET_SMALL_HOR': '16cshor.tga',
              'PIX_CARPET_SMALL_LEFT': '16csleft.tga',
              'PIX_CARPET_SMALL_RIGHT': '16csrigh.tga',
              'PIX_CARPET_SMALL_TINY': '16cstiny.tga',
              'PIX_CARPET_SMALL_VER': '16csver.tga',
              'PIX_CARPET_U': '16carpu.tga',
              'PIX_CARPET_UL': '16carpul.tga',
              'PIX_CARPET_UR': '16carpur.tga',
              'PIX_CLIFF_BACK_1': '16clifup.tga',
              'PIX_CLIFF_BACK_2': '16clifu2.tga',
              'PIX_CLIFF_BACK_L': '16cliful.tga',
              'PIX_CLIFF_BACK_R': '16clifur.tga',
              'PIX_CLIFF_BOTTOM': '16cliff1.tga',
              'PIX_CLIFF_LEFT': '16cliff3.tga',
              'PIX_CLIFF_RIGHT': '16cliff4.tga',
              'PIX_CLIFF_TOP': '16cliff2.tga',
              'PIX_CLIFF_TOP_L': '16clifdl.tga',
              'PIX_CLIFF_TOP_R': '16clifdr.tga',
              'PIX_COBBLE_1': '16cob1.tga',
              'PIX_COBBLE_2': '16cob2.tga',
              'PIX_COBBLE_3': '16cob3.tga',
              'PIX_COBBLE_4': '16cob4.tga',
              'PIX_COLUMN1': '16colm0.tga',
              'PIX_COLUMN2': '16colm1.tga',
              'PIX_DIRTGRASS_DARK_LL1': '16dglld.tga',
              'PIX_DIRTGRASS_DARK_LR1': '16dglrd.tga',
              'PIX_DIRTGRASS_DARK_UL1': '16dguld.tga',
              'PIX_DIRTGRASS_DARK_UR1': '16dgurd.tga',
              'PIX_DIRTGRASS_LL1': '16dgll1.tga',
              'PIX_DIRTGRASS_LR1': '16dglr1.tga',
              'PIX_DIRTGRASS_UL1': '16dgul1.tga',
              'PIX_DIRTGRASS_UR1': '16dgur1.tga',
              'PIX_DIRT_1': '16dirt2.tga',
              'PIX_DIRT_DARK_1': '16dirtd1.tga',
              'PIX_FLOOR1': '16floor.tga',
              'PIX_FLOOR_PAVED': '16fpd.tga',
              'PIX_FLOOR_PAVEL': '16fpl.tga',
              'PIX_FLOOR_PAVER': '16fpr.tga',
              'PIX_FLOOR_PAVEU': '16fpu.tga',
              'PIX_GRASS1': '16grass1.tga',
              'PIX_GRASS1_DAMAGED': '16grasd1.tga',
              'PIX_GRASS2': '16grass2.tga',
              'PIX_GRASS3': '16grass3.tga',
              'PIX_GRASS4': '16grass4.tga',
              'PIX_GRASSWATER_LL': '16gwll.tga',
              'PIX_GRASSWATER_LR': '16gwlr.tga',
              'PIX_GRASSWATER_UL': '16gwul.tga',
              'PIX_GRASSWATER_UR': '16gwur.tga',
              'PIX_GRASS_DARK_1': '16grassd.tga',
              'PIX_GRASS_DARK_2': '16grd2.tga',
              'PIX_GRASS_DARK_3': '16grd3.tga',
              'PIX_GRASS_DARK_4': '16grd4.tga',
              'PIX_GRASS_DARK_B1': '16grdb1.tga',
              'PIX_GRASS_DARK_B2': '16grdb2.tga',
              'PIX_GRASS_DARK_BR': '16grdbr.tga',
              'PIX_GRASS_DARK_LL': '16grassi.tga',
              'PIX_GRASS_DARK_R1': '16grdr1.tga',
              'PIX_GRASS_DARK_R2': '16grdr2.tga',
              'PIX_GRASS_DARK_UR': '16grassh.tga',
              'PIX_GRASS_LIGHT_1': '16grl1.tga',
              'PIX_GRASS_LIGHT_BOTTOM': '16grlb.tga',
              'PIX_GRASS_LIGHT_LEFT': '16grll.tga',
              'PIX_GRASS_LIGHT_LEFT_BOTTOM': '16grllb.tga',
              'PIX_GRASS_LIGHT_LEFT_TOP': '16grllt.tga',
              'PIX_GRASS_LIGHT_RIGHT': '16grlr.tga',
              'PIX_GRASS_LIGHT_RIGHT_BOTTOM': '16grlrb.tga',
              'PIX_GRASS_LIGHT_RIGHT_TOP': '16grlrt.tga',
              'PIX_GRASS_LIGHT_TOP': '16grlt.tga',
              'PIX_GRASS_RUBBLE': '16grassr.tga',
              'PIX_H_WALL1': '16tile.tga',
              'PIX_JAGGED_GROUND_1': '16jwg1.tga',
              'PIX_JAGGED_GROUND_2': '16jwg2.tga',
              'PIX_JAGGED_GROUND_3': '16jwg3.tga',
              'PIX_JAGGED_GROUND_4': '16jwg1.tga',
              'PIX_PATH_1': '16path1.tga',
              'PIX_PATH_2': '16path2.tga',
              'PIX_PATH_3': '16path3.tga',
              'PIX_PATH_4': '16path4.tga',
              'PIX_PAVEMENT1': '16pave1.tga',
              'PIX_PAVEMENT2': '16pave2.tga',
              'PIX_PAVEMENT3': '16pave3.tga',
              'PIX_PAVESTEPS1': '16pstep.tga',
              'PIX_PAVESTEPS2': '16ptest.tga',
              'PIX_PAVESTEPS2L': '16ptestl.tga',
              'PIX_PAVESTEPS2R': '16ptestr.tga',
              'PIX_TORCH1': '16torch1.tga',
              'PIX_TORCH2': '16torch2.tga',
              'PIX_TORCH3': '16torch3.tga',
              'PIX_TREE_B1': '16treeb1.tga',
              'PIX_TREE_M1': '16treem1.tga',
              'PIX_TREE_ML': '16treeml.tga',
              'PIX_TREE_MR': '16treemr.tga',
              'PIX_TREE_MT': '16treemt.tga',
              'PIX_TREE_T1': '16treet1.tga',
              'PIX_VOID1': '16space.tga',
              'PIX_WALL2': '16wall2.tga',
              'PIX_WALL3': '16wall3.tga',
              'PIX_WALL4': '16walllo.tga',
              'PIX_WALL5': '16w2lo.tga',
              'PIX_WALLSIDE1': '16brick1.tga',
              'PIX_WALLSIDE_C': '16brickc.tga',
              'PIX_WALLSIDE_CRACK_C1': '16brick3.tga',
              'PIX_WALLSIDE_L': '16brickl.tga',
              'PIX_WALLSIDE_R': '16brickr.tga',
              'PIX_WALLTOP_H': '16ttop.tga',
              'PIX_WALL_ARROW_FLOOR': '16wallof.tga',
              'PIX_WALL_ARROW_GRASS': '16wallog.tga',
              'PIX_WALL_ARROW_GRASS_DARK': '16wallod.tga',
              'PIX_WALL_LL': '16wallll.tga',
              'PIX_WATER1': '16water1.tga',
              'PIX_WATER2': '16water2.tga',
              'PIX_WATER3': '16water3.tga',
              'PIX_WATERGRASS_D': '16wgd.tga',
              'PIX_WATERGRASS_L': '16wgl.tga',
              'PIX_WATERGRASS_LL': '16wgll.tga',
              'PIX_WATERGRASS_LR': '16wglr.tga',
              'PIX_WATERGRASS_R': '16wgr.tga',
              'PIX_WATERGRASS_U': '16wgu.tga',
              'PIX_WATERGRASS_UL': '16wgul.tga',
              'PIX_WATERGRASS_UR': '16wgur.tga'}
  
  #register all times from the game
  for name, filename in tileDict.iteritems():    
    glad.resource.register(name, 
                           os.path.join(tileFolder,filename), tile=True, 
                           size=tileSize)
    
    
  
  
  