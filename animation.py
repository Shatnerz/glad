

import pygame

import glad

from util import Vector


class AnimationPlayer(object):
  """Handles updating and drawing animations to the screen"""
  
  def __init__(self, animation, timer, loop=False, cycle=False):
    
    self.animation = animation    
    self.timer = timer
    self.loop = loop
    
    self.currentFrameIndex = 0
    self.timeLeft = timer
    
    #Color Cycling
    self.colorCycle = cycle
    self.color = 'NONE'
    #grab palette from first frame for palette color cycling
    if self.animation.frameList[0].get_bitsize() == 8:
      self.palette = list(self.animation.frameList[0].get_palette())
    else: self.palette = None
    self.cycleTime = 0.1
    self.cycleTimeLeft = self.cycleTime
    
  def update(self, time):
    #if the timer is disabled, do nothing
    if self.timeLeft is None:
      return
    
    self.timeLeft -= time
    
    if self.timeLeft <= 0.0:     
      #reset the time left for the next animation
      # if it is < 0, we shorten the timeLeft by that amount to keep
      # the animation running smoothly
      self.timeLeft = self.timer + self.timeLeft
      
      #increment the frame
      self.currentFrameIndex += 1
      
      #if looping is true, set the frame to the first one
      if self.currentFrameIndex == len (self.animation.frameList):
        
        if self.loop:
          self.currentFrameIndex = 0
        else:
          self.timeLeft = None #disable future updates
    
    #if self.colorCycle:      
    #  self.updateColorCycle(time)

  def draw(self, screen, pos):
    
    #pos was the 'center' of the object, now we translate it
    # to the upper left corner for pygame
    frameWidth = self.animation.frameSize[0]
    frameHeight = self.animation.frameSize[0]
    
    x = pos[0] - frameWidth/2.0
    y = pos[1] - frameHeight/2.0
    
    #Note: pos should be upperleft coordinate of rect   
    pyRect = pygame.Rect((x,y), self.animation.frameSize)    
    
    screen.blit(self.animation.frameList[self.currentFrameIndex],
                pyRect)
    
  def cycleColors(self):
    """Cycles the colors between start and end in the index"""
    #end should be 1 greater than in base.h
    #Orange: 224 to 232
    #Blue: 208 to 224
    #Now cycles in reverse order from what I initially had
    if self.color == 'ORANGE':
      start=224
      end=232
    elif self.color == 'BLUE':
      start=208
      end = 224
    else:
      start=0
      end=0
      
    if self.palette: #THE COMMENTED OUT SECTION IS JUST THE SAME CYCLE IN REVERSE    
      last = self.palette[end-1]
      var = range(start+1,end)
      var.sort(reverse=True)
      for x in var:
        self.palette[x] = self.palette[x-1]
      self.palette[start] = last
      self.animation.frameList[self.currentFrameIndex].set_palette(self.palette)
      #first = self.palette[start]
      #var = range(start,end-1)
      #for x in var:
      #  self.palette[x] = self.palette[x+1]
      #self.palette[end-1] = first
      #self.animation.frameList[self.currentFrameIndex].set_palette(self.palette)
      
  def updateColorCycle(self, time):
    """Update the color cycling"""
    if self.cycleTimeLeft >0:
      self.cycleTimeLeft -= time
      if self.cycleTimeLeft <= 0.0:
        self.cycleTimeLeft += self.cycleTime 
        self.cycleColors()#Color cycles for oranges
        if self.cycleTimeLeft < 0:
          updateColorCycle(time)
    else:
      self.cycleTimeLeft += self.cycleTime
      self.colorCycle()

class Animation(object):
  def __init__(self, frameList):
    
    assert len(frameList) != 0
        
    self.frameList = frameList
    
    #Note: assumes all frames are the same size!
    # gets the size from the first frame
    self.frameSize = frameList[0].get_size()
           
class TestAnimation(Animation):
  
  def __init__(self, size=(32,32), colorList=None):
    
    frameList = []
    
    if colorList is None:
      colorList = [(255,0,0),(0,255,0),(0,0,255)]
            
    for c in colorList:
      f = pygame.Surface(size)
      f.fill(c)
      frameList.append(f)      
    
    Animation.__init__(self,frameList)   
    
  
class AnimateRangedAttack(Animation):
  """Animation class for projectiles""" #mostly copied from animateUnit
  
  def __init__(self, name, directionString, frames = 8, time = 0.2, loop=True):
    
    #load spriteSheet
    self.spriteSheet = glad.resource.get(name)
    
    #get the size of each frame
    self.spriteWidth = self.spriteSheet.get_width()/frames
    self.spriteHeight = self.spriteSheet.get_height() - 1
    self.size = (self.spriteWidth, self.spriteHeight)
    
    #sort all frames into a list
    self.allFramesList = self.sortFrames()
    
    self.animationDict = {'north' : [self.allFramesList[1]],
                     'east' : [self.allFramesList[2]],
                     'south' : [self.allFramesList[0]],
                     'west' : [self.allFramesList[3]],
                     'northeast' : [self.allFramesList[5]],
                     'southeast' : [self.allFramesList[6]],
                     'southwest' : [self.allFramesList[4]],
                     'northwest' : [self.allFramesList[7]]}  
    
    self.currentAnimation = self.animationDict[directionString]
    
    Animation.__init__(self, self.size, self.currentAnimation, time, loop)
    
  def sortFrames(self):
    """sort frames into one list"""
      
    spriteWidth = self.spriteWidth     
    spriteHeight = self.spriteHeight
      
    #Sort frames
    frameList = []
    point = 0
    sheetWidth = self.spriteSheet.get_width()
    numSprites = sheetWidth/spriteWidth
    for sprite in xrange(numSprites):
      frame = self.spriteSheet.subsurface((point, 1), (spriteWidth, spriteHeight))
      point += spriteWidth
      frameList.append(frame)
    return frameList
       
class AnimateSpinningAttack(AnimateRangedAttack):
  """animation class for rotating/animating projectiles"""
  
  def __init__(self, name, directionString, frames = 8, time = 0.1, loop=True):
    
    #load spriteSheet
    self.spriteSheet = glad.resource.get(name)
    
    #get the size of each frame
    self.spriteWidth = self.spriteSheet.get_width()/frames
    self.spriteHeight = self.spriteSheet.get_height() - 1
    self.size = (self.spriteWidth, self.spriteHeight)
    
    self.allFramesList = self.sortFrames()
    
    self.animationDict = {'north' : self.allFramesList,
                     'east' : self.allFramesList,
                     'south' : self.allFramesList,
                     'west' : self.allFramesList,
                     'northeast' : self.allFramesList,
                     'southeast' : self.allFramesList,
                     'southwest' : self.allFramesList,
                     'northwest' : self.allFramesList}
    self.currentAnimation = self.animationDict[directionString]
    
    Animation.__init__(self, self.size, self.currentAnimation, time, loop)

class AnimateSlimeBall(AnimateRangedAttack):
  """Animation class for slime ball projectiles"""
  def __init__(self, name, directionString, hue, frames = 8, time = 0.1, loop=True):
    #load spriteSheet
    self.spriteSheet = glad.resource.get(name)
    self.mask = self.spriteSheet
    self.hue = hue
    #self.colorize()   NEED TO DO THIS BEFOREHAND, IT SLOWS THE GAME NOTICEABLY AT THE MOMENT
    
    #get the size of each frame
    self.spriteWidth = self.spriteSheet.get_width()/frames
    self.spriteHeight = self.spriteSheet.get_height() - 1
    self.size = (self.spriteWidth, self.spriteHeight)
    
    self.allFramesList = self.sortFrames()
    
    self.attack = []
    for x in range(7):
      self.attack.append(self.allFramesList[x])
    x = 6
    while x > 1:
      self.attack.append(self.allFramesList[x])
      x -= 1
    
    self.animationDict = {'north' : self.attack,
                     'east' : self.attack,
                     'south' : self.attack,
                     'west' : self.attack,
                     'northeast' : self.attack,
                     'southeast' : self.attack,
                     'southwest' : self.attack,
                     'northwest' : self.attack}
    self.currentAnimation = self.animationDict[directionString]
    
    Animation.__init__(self, self.size, self.currentAnimation, time, loop)
    
  def colorize(self):
    """Colorize the slimeball to match slime, slightly modified from AnimateUnit """
    transColor = self.spriteSheet.get_at((0,1))
    for x in range(self.mask.get_width()):
      for y in range(self.mask.get_height()):
        if self.mask.get_at((x, y)) != transColor: #find white pixels in mask
          #Get rgb
          r, g, b, alpha = self.spriteSheet.get_at((x, y))
          #to grayscale
          avg = (r + g + b)/3
          r, g, b = avg, avg, avg
          color = pygame.Color(r, g, b)
          #get hsv
          hue, sat, value, alpha = color.hsva
          #set hue
          hue = self.hue
          #set sat
          satPeak = -0.0068434106*value*value+1.6463624986*value+2.007500384
          if satPeak > 100:
              satPeak = 100
          if value <= 50:
              sat = satPeak
          elif value > 50:
              sat = satPeak-(satPeak/50.0*(value-50))
          #set value
          spriteSat = 50 #the above setting are for sat=50, i dont remember all of this
          num = spriteSat/50.0
          if value <= 50:
            valAdd = value/2*num
          elif value > 50:
            valAdd = (value-2*num*(value-50))/2
          value += valAdd
          #set color
          color.hsva = (hue, sat, value, alpha)
          self.spriteSheet.set_at((x, y), (color))


class AnimateUnit(Animation):
  
  """Animation class for all generic units"""
  def __init__(self, name, directionString, hue = 180, time = 0.2):
    
    #load spriteSheet
    self.spriteSheet = glad.resource.get(name)
    self.mask = glad.resource.get(name+'_mask')
    #set color
    self.hue = hue
    self.colorize()
    
    #get size of each sprite
    self.spriteWidth = self.getSpriteWidth()
    self.spriteHeight = self.spriteSheet.get_height() - 1
    self.size = (self.spriteWidth, self.spriteHeight)
    
    #sort all frames into a list
    self.allFramesList = self.sortFrames()
    
    ###################################################Revise##################################   
    self.north = self.createAnimation('north')
    self.east = self.createAnimation('east')
    self.south = self.createAnimation('south')
    self.west = self.createAnimation('west')
    
    self.northeast = self.createAnimation('northeast')
    self.southeast = self.createAnimation('southeast')
    self.southwest = self.createAnimation('southwest')
    self.northwest = self.createAnimation('northwest')
    
    #used to determine animation based on direction string
    self.animationDict = {'north' : self.north,
                     'east' : self.east,
                     'south' : self.south,
                     'west' : self.west,
                     'northeast' : self.northeast,
                     'southeast' : self.southeast,
                     'southwest' : self.southwest,
                     'northwest' : self.northwest}  
    
    self.currentAnimation = self.animationDict[directionString]
    
    #load attack animations #if this works possibly load direction animations like this
    self.directions = ['north', 'east', 'south', 'west', 'northeast', 'northwest', 'southeast', 'southwest']
    self.meleeAttacks = self.loadMeleeAttacks()
    self.rangedAttacks = self.loadRangedAttacks()
    
    Animation.__init__(self, self.size, self.currentAnimation, time, True)
    
  def getSpriteWidth(self):
    """find individual sprite width(assuming all are same width)"""
    
    spriteWidth = 0
    for x in range(self.spriteSheet.get_width()):
       #look for white pixel denoting sprite width
      if self.spriteSheet.get_at((x,0)) == (255, 255, 255):
         spriteWidth = x+1
         break
    return spriteWidth
    
  def sortFrames(self):
    """sort frames into one list"""
      
    spriteWidth = self.spriteWidth     
    spriteHeight = self.spriteHeight
      
    #Sort frames
    frameList = []
    point = 0
    sheetWidth = self.spriteSheet.get_width()
    numSprites = sheetWidth/spriteWidth
    for sprite in xrange(numSprites):
      frame = self.spriteSheet.subsurface((point, 1), (spriteWidth, spriteHeight))
      point += spriteWidth
      frameList.append(frame)
        
    return frameList
  
  def createAnimation(self, animationString):
    """breakdown frame list into animations"""
    #only works for walking now
    #used when sorting frames into animations
    animationReference = {'south' : 0,
                               'north' : 1,
                               'east' : 2,
                               'west' : 3,
                               'southwest' : 12,
                               'northeast' : 13,
                               'southeast' : 14,
                               'northwest' : 15}
    
    x = animationReference[animationString]
    
    animation = []
    animation.append(self.allFramesList[x])
    animation.append(self.allFramesList[x+4])
    animation.append(self.allFramesList[x])
    animation.append(self.allFramesList[x+8])
    
    return animation
  
  def setAnimation(self, animationString):
    #if self.frameList != self.animationDict[animationString]:
    #  self.frameList = self.animationDict[animationString]
    if self.frameList[0].get_offset != self.animationDict[animationString][0].get_offset:
      self.frameList = self.animationDict[animationString]
      self.currentFrameIndex = 0
  
  def colorize(self):
    """Colorize spriteSheet using self.hue and self.mask"""
    #possibly add something to lighten/darken colors to add more team colors
    
    for x in range(self.mask.get_width()):
      for y in range(self.mask.get_height()):
        if self.mask.get_at((x, y)) == (255, 255, 255): #find white pixels in mask
          #Get rgb
          r, g, b, alpha = self.spriteSheet.get_at((x, y))
          #to grayscale
          avg = (r + g + b)/3
          r, g, b = avg, avg, avg
          color = pygame.Color(r, g, b)
          #get hsv
          hue, sat, value, alpha = color.hsva
          #set hue
          hue = self.hue
          #set sat
          satPeak = -0.0068434106*value*value+1.6463624986*value+2.007500384
          if satPeak > 100:
              satPeak = 100
          if value <= 50:
              sat = satPeak
          elif value > 50:
              sat = satPeak-(satPeak/50.0*(value-50))
          #set value
          spriteSat = 50 #the above setting are for sat=50, i dont remember all of this
          num = spriteSat/50.0
          if value <= 50:
            valAdd = value/2*num
          elif value > 50:
            valAdd = (value-2*num*(value-50))/2
          value += valAdd
          #set color
          color.hsva = (hue, sat, value, alpha)
          self.spriteSheet.set_at((x, y), (color))

  def loadMeleeAttacks(self):
    """Load all melee attacks into dictionary"""
    meleeAttacks = {}
    for x in self.directions:
      attackAnimation = []
      direction = self.animationDict[x]
      attackAnimation.append(direction[1])
      attackAnimation.append(direction[0])
      meleeAttacks[x] = attackAnimation
    return meleeAttacks  
  
  def loadRangedAttacks(self):
    """Load all melee attacks into dictionary"""
    rangedAttacks = self.loadMeleeAttacks()
    return rangedAttacks

  def meleeAttack(self, directionString):
    """Set the animation to the melee attack animation for the direction"""
    if self.frameList != self.meleeAttacks[directionString]:
      self.currentFrameIndex = 0
      self.frameList = self.meleeAttacks[directionString]
    
    #animation = Animation(self, self.size, attackAnimation, attacktime/2, loop=False)
    #return animation
    
  def rangedAttack(self, directionString):
    """Set the animation to ranged attack, which is typically the melee animation"""
    #if self.frameList != self.rangedAttacks[directionString]:
    if self.frameList[0].get_offset() != self.rangedAttacks[directionString][0].get_offset(): #compare offset
      #print self.rangedAttacks[directionString][0].get_offset(), "*******", self.frameList[0].get_offset()
      self.currentFrameIndex = 0
      self.frameList = self.rangedAttacks[directionString]
        

class AnimateMage(AnimateUnit):
  """Animation class for all mages"""
  
  def __init__(self, name, directionString, hue = 180, time = 0.2):
    AnimateUnit.__init__(self, name, directionString, hue, time)
    
  def createAnimation(self, animationString):
    """breakdown frame list into animations"""
    #only works for walking now
    #used when sorting frames into animations
    animationReference = {'south' : 0,
                               'north' : 1,
                               'east' : 2,
                               'west' : 3,
                               'southwest' : 20,
                               'northeast' : 21,
                               'southeast' : 22,
                               'northwest' : 23}
    
    x = animationReference[animationString]
    
    animation = []
    animation.append(self.allFramesList[x])
    animation.append(self.allFramesList[x+4])
    animation.append(self.allFramesList[x])
    animation.append(self.allFramesList[x+8])
    
    return animation
          
  def loadRangedAttacks(self):
    """Load all ranged attacks into dictionary"""
    
    rangedAttacks = {}
    
    attackDict = {'south' : 16,
                  'north' : 17,
                  'east' : 18,
                  'west' : 19,
                  'southwest' : 32,
                  'northeast' : 33,
                  'southeast' : 34,
                  'northwest' : 35}
    
    for x in self.directions:
      attackAnimation = []
      direction = self.animationDict[x]
      attackAnimation.append(self.allFramesList[attackDict[x]]) #add the frame from attackDict
      attackAnimation.append(direction[0])
      rangedAttacks[x] = attackAnimation
    return rangedAttacks
        
class AnimateSmallSlime(AnimateUnit):
  
  """Animation class for only small slimes"""
  
  def __init__(self, name, directionString = 'north', hue = 180, time = 0.2):
    AnimateUnit.__init__(self, name, directionString, hue, time)
    
  def createAnimation(self, directionString='north'):
    animation = []
    for x in range(8):
      animation.append(self.allFramesList[x])
    x = 6
    while x > 0:
      animation.append(self.allFramesList[x])
      x -= 1
    return animation

class AnimateMediumSlime(AnimateSmallSlime):
  """Animation class for only medium slimes"""
  
  def __init__(self, name, directionString='north', hue = 180, time = 0.2):
    
    AnimateSmallSlime.__init__(self, name,directionString, hue, time)
    
  def createAnimation(self, directionString='north'):
    animation = []
    for x in range(12):
      animation.append(self.allFramesList[x])
    x = 10
    while x > 0:
      animation.append(self.allFramesList[x])
      x -= 1
    return animation
  
class AnimateBigSlime(AnimateSmallSlime):
  """Animation class for only big slimes"""
  #TODO: ill add splitting animations when i add special animations
  #also i only use the first 3 frames for moving
  
  def __init__(self, name, directionString='north', hue = 180, time = 0.2):
    
    AnimateSmallSlime.__init__(self, name, directionString, hue, time)
    
  def createAnimation(self, directionString='north'):
    animation = []
    for x in range(3):
      animation.append(self.allFramesList[x])
    x = 1
    while x > 0:
      animation.append(self.allFramesList[x])
      x -= 1
    return animation
