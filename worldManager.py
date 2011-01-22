import pygame

import glad

#from multiMethod import multimethod

from util import Vector,Rect,getCollisionInfo,getOverlap

class AbstractWorld(object):
  
  def __init__(self):
    self.objectList = []
    self.controllerList = []

    
  def addObject(self, obj):
    """Add an object to the world, throws exception if the object
    can't be placed there"""
    
    #TODO: we should check for this somewhere, but not every time
    #we are using a grid to for broad-phase collision
    # detection, it assumes that no object is bigger than
    # the given size
  
  #TODO: handle placing object on top of another object
  
  def draw(self, screen, offset):
    for o in self.objectList:
      o.draw(screen, offset)
      
  def generateCollisionList(self, time):
    """Generate a dictionary of collisions between object
    that are allowed to generate collision events
    TODO: FINISH DOC HERE
    
    only considers collisions that happen <= time"""
    
    #d = {}
    l = []
    
    #TODO: improve, this is O(n^2) for testing
    
    for i in range(len(self.objectList)):      
      for j in range(i+1, len(self.objectList)):
        
        objI = self.objectList[i]
        objJ = self.objectList[j]
        
        
        #If the objecs can't collide, don't even bother 
        # comparing them
        if not CollisionFilter.canCollide(objI, objJ):
          continue
        
        #Note, the shapes are at the origin, so we have to translate them
        # to the objects current position
        s1 = objI.shape.translate(objI.getPos())
        s1vel = objI.vel
        
        s2 = objJ.shape.translate(objJ.getPos())
        s2vel = objJ.vel

        #TODO: this will always return none!!!
        colInfo = getCollisionInfo(s1,s1vel,s2,s2vel)
                
        if colInfo is not None:          
          
          #only consider events <= time
          colTime, objIStops, objJStops = colInfo         
          
          if colTime <= time:
            #print colInfo
            
            #if objI not in d:
            #  d[objI] = set([()])
            
            l.append((colTime, objI, objIStops,objJ,objJStops))
  
    return l   
  
  def generateNeighborDict(self, time):
    """Generate dict of neighbors. A neighbor is any object
    within the bounding box of an objects trajectory during time.
    Objects must be able to collide to be considered neighbors"""
    
    #first, calculate bounding box for each object
    
    boundDict = {}
    
    for i in range(len(self.objectList)):      
      
      p1 = self.objectList[i].pos
      p2 = self.objectList[i].getPosInTime(time)
      
      shape = self.objectList[i].shape
      
      #Get bounding boxes at the 2 positions
      box1 = shape.getBoundingBox().translate(p1)
      box2 = shape.getBoundingBox().translate(p2)
      
      #generate the union between them and store it
      bbox = Rect.union(box1, box2)
      
      boundDict[i] = bbox
                
    d = {}
    
    #TODO: improve, this is O(n^2) for testing
    #TODO: is this only necessary for objects that can stop each other?
    
    for i in range(len(self.objectList)):      
      for j in range(i+1, len(self.objectList)):
        
        iObj = self.objectList[i]
        jObj = self.objectList[j]
        
        #this is only applicable for objects which can create
        # collision events
        if not CollisionFilter.canCollide(iObj,jObj):
          continue
        
        iRect = boundDict[i]
        jRect = boundDict[j]
        
        if Rect.touches(iRect, jRect):
          
          if iObj in d:            
            d[iObj].add(jObj)
          else:
            d[iObj] = set([jObj])          
          
          if jObj in d:
            d[jObj].add(iObj)
          else:
            d[jObj] = set([iObj])
            
    return d
  
  @staticmethod
  def stopObjectEarly(obj, colTime, time, neighborDict, collisionList):
    
    newPos = obj.getPosInTime(colTime)
    
    #Set the new object position as the position right before the collision
    #set its movement to 0
    obj.pos = newPos;
    obj.requestedPos = newPos;    
    obj.movedDir = (0,0)    
    obj.vel = Vector(0.0,0.0)
    
    #remove all references to obj from collisionList
    
    collisionList = [x for x in collisionList if x[1] is not obj and x[3] is not obj]
    
    #Now, recalculate collision for all of its check if any of its neighbors
        
    s1 = obj.shape.translate(obj.getPos())
    s1vel = obj.vel
    
    for n in neighborDict[obj]:
      
        s2 = n.shape.translate(n.getPos())
        s2vel = n.vel
        
        colInfo = getCollisionInfo(s1, s1vel, s2, s2vel)
        
        if colInfo is not None:
          
          
          #only consider events <= time
          cTime, objIStops, objJStops = colInfo         
          
          #ctime must be > original colTime
          if cTime <= time and cTime >= colTime:
            #print colInfo
            
            #if objI not in d:
            #  d[objI] = set([()])
            
            collisionList.append((cTime, obj, objIStops,n,objJStops))
  
    #sort collision list again 
    collisionList.sort(key=lambda x:x[0])
    
      
  def greedyCollisionDetection(self, time):
    """Objects are simply moved in order, and if an object
    can't move because it's space has been taking, it's movement is 
    canceled"""
    
    #collisionList = self.generateCollisionList(time)
    
    neighborDict = self.generateNeighborDict(time)
    
    #print neighborDict
    
    collisionList = self.generateCollisionList(time)
    
    #sort the list by time
    collisionList.sort(key=lambda x:x[0])
    
    #print collisionList
    
    #TODO: handle case where
    
    #print collisionList 
    
    while len(collisionList) > 0:
      
      #pop off the first item
      collisionInfo = collisionList.pop(0)
      colTime,objI,objIStops,objJ,objJStops = collisionInfo
      
      print 'Collision: %s' % str(collisionInfo)
#      print objI.getRect()
#      print objJ.getRect()

      #We don't 'stop' objects in motion unless necessary
      if not CollisionFilter.canStop(objI,objJ):
        continue
      
      if objIStops:
        #remove all future collisions with objI in them
        AbstractWorld.stopObjectEarly(objI, colTime, time, neighborDict,collisionList)
      
      if objJStops:
        #remove all future collisions with objJ in them
        AbstractWorld.stopObjectEarly(objJ, colTime, time, neighborDict,collisionList)
    
    #for (colTime,objI,objIStops,objJ,objJStops) in collisionList:
    #  print (colTime,objI,objIStops,objJ,objJStops)
      
    
        
        
    
      
  def update(self, time):
    
    #Process controllers, either player or AI
    for c in self.controllerList:
      c.process()
    
    #First move everything into their 'requested' positions
    for o in self.objectList:      
      o.updateRequestedPos(time)
      
    #Resolve collisions between requested positions
    self.greedyCollisionDetection(time)
    
    #Finalize positions
    for o in self.objectList:
      
      #keep track of it's old position
      lastPos = o.pos
      #update it's position
      o.updatePos(time)
      
      #if object is outside of the world, kill it
      #TODO: handle object end of life better
      if not self.worldBoundingRect.contains(o.pos):
        o.alive = False
            
      
    #update animations, weapons, other stuff
    for o in self.objectList:
      o.update(time)
      
      
    #remove all dead objects
    self.objectList = [x for x in self.objectList if x.alive]
    


class AbstractObject(object):
  """All game world objects are ultimately derived from this class.
  Contains a variety of useful functions used for movement and 
  collision detection"""
  
  def __init__(self, pos, shape, team=1, moveSpeed = 50.0, moveDir=None):
    
    #General
    
    #All objects are alive/enabled by default.
    self.alive = True
    
    #Objects position (the center)
    self.pos = Vector(pos)
    
    #The objects shape, used for collision detection 
    self.shape = shape
    
    self.moveSpeed = moveSpeed
    if not moveDir:
      self.moveDir = Vector(0,0)
    else:
      self.moveDir = Vector(moveDir)
      
    #Velocity is the normalized direction scaled by the speed
    #TODO: calculate on update?
    if not self.moveDir.isNullVector():
      #self.moveDir.normalize()    
      self.vel = self.moveDir.getNormalized() * self.moveSpeed
    else:
      self.vel = Vector(0,0)
      
    #Keep track of where the objects wants to go next
    self.requestedPos = pos
    
    #Keep track of which direction the object is 'facing'
    self.orientation = None
    
    #Set up the animation object
    self.frames = []
    #TODO: this is temporary for testing
    self.animation = TestAnimation(shape.getSize())
    
    #set the team property
    self.team = team
    
    #Turning
    self.turning = False
    self.turnTime = 0.05
    self.turnTimer = 0
    
  def orientationToString(self):
    #converts the orientation to a string
    #makes it easier for animation
    #if self.orientation == None: #FIX FOR IF THERE IS NO ORIENTATION
     # return 'north'
    
    string = ''
    if self.orientation[0] == 0 and self.orientation[1] < 0:
      string = 'north'
    elif self.orientation[0] == 0 and self.orientation[1] > 0:
      string = 'south'
    elif self.orientation[0] > 0 and self.orientation[1] == 0:
      string = 'east'
    elif self.orientation[0] < 0 and self.orientation[1] == 0:
      string = 'west'
    elif self.orientation[0] < 0 and self.orientation[1] < 0:
      string = 'northwest'
    elif self.orientation[0] > 0 and self.orientation[1] > 0:
      string = 'southeast'
    elif self.orientation[0] < 0 and self.orientation[1] > 0:
      string = 'southwest'
    elif self.orientation[0] > 0 and self.orientation[1] < 0:
      string = 'northeast'
    
    return string  
  
  def draw(self, screen, offset):
    
    #draw the animation, centered at the objects position
    # and offset according to the location of the camera    
    self.animation.draw(screen, self.getPos()+offset)
  
    
  def setPos(self, pos):    
    self.pos = Vector(pos)
      
  def getPos(self):
    return self.pos
    
  def getPosInTime(self, time):
    """Calculate the objects position in 'time' as a function
    of its current position and velocity."""
    
    return self.pos + self.vel*time
    
    
#    
#  def getRect(self):
#    #return (self.pos[0],self.pos[1],
#    #        self.size[0],self.size[1])
#    
#    return Rect(self.pos, self.size)
    
  def getRequestedPos(self):
    return self.requestedPos
  
#  def getVelocity(self):
#    return self.moveSpeed
  
#  def isCollision(self, o,requested=False):
#    #request=True means we check requested positions
#    """Check if this object's rect overlaps the other's rect"""
#    
#    if requested:
#      ax1,ay1 = self.requestedPos
#    else:
#      ax1,ay1 = self.pos
#    ax2,ay2 = ax1+self.size[0],ay1+self.size[1]
#    
#    if requested:
#      bx1,by1 = o.requestedPos
#    else:
#      bx1,by1 = o.pos
#    bx2,by2 = bx1+o.size[0],by1+o.size[1]
#    
#    if ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1:
#      return True
#    else:
#      return False
    
  def requestMove(self, direction):
    """Indicate when preferred direction this object wants to go"""  
    
    assert direction is not None
    
    if direction != (0, 0):
      normalizedOrientation = self.orientation.getNormalized()
      normalizedDirection = Vector(direction).getNormalized()
      if normalizedOrientation == normalizedDirection:
        #only move if facing the right direction, else turn
      
        #update the direction
        self.moveDir = Vector(direction)
        
        self.vel = self.moveDir.getNormalized()*self.moveSpeed
        self.turning = False
        
        #update the objects velocity
        #TODO: what if the move direction is 0 vector?    
        #if not self.moveDir.isNullVector():
          #self.moveDir.normalize()
          #self.vel = self.moveDir.getNormalized()*self.moveSpeed
        #else:
          #self.vel = Vector(0,0)
      else:
        self.turning = True
        self.vel = Vector(0,0)
        self.turn(Vector(direction))
    else:
      #not trying to move
      self.vel = Vector(0,0)
      self.turning = False
      
  def turn(self, direction):
    """Use cross product to find the best direction and turns 45 degrees"""
    
    if self.orientation.getNormalized() != direction.getNormalized(): #prevents over turning incase time is large
      if self.turnTimer >= self.turnTime:
    
        o = self.orientation.getNormalized()
        d = direction.getNormalized()
        value = o[0]*d[1] - o[1]*d[0]
    
        sinCos = 0.707106781 #rotate 45  degrees so sin and cos are equal
        if value >= 0:
          x = self.orientation[0]*sinCos - self.orientation[1]*sinCos
          y = self.orientation[0]*sinCos + self.orientation[1]*sinCos
        else:
          x = self.orientation[0]*sinCos + self.orientation[1]*sinCos
          y = self.orientation[1]*sinCos - self.orientation[0]*sinCos
      
          #Smooths out all rounding errors
        if x > 0:
          x = 1
        elif x < 0:
          x = -1
        if y > 0:
          y = 1
        elif y < 0:
          y = -1
      
        self.orientation = Vector(x,y)
      
        self.turnTimer -= self.turnTime
        self.turn(direction) #turns again if time exceeds one turn, but dont want to overturn
        
  def updatePos(self, time):
    """Set the objects position equal to its requested position. Usually
    done after collision resolution"""
    self.pos = self.requestedPos
    
  def updateRequestedPos(self, time):
    """Update the objects requested position, done before
    collision resolution"""    
    self.requestedPos = self.getPosInTime(time)
    
  def update(self, time):
    #TODO: animaitons should be updated after collision detection
    #update the animation
    
    if self.animation:
      self.animation.update(time)
    
    #update turning clock  
    if self.turning:
      self.turnTimer += time

class Animation(object):
  def __init__(self, size, frameList, timer, loop=False):
    
    #Note: assumes all frames are the same size!
    self.frameSize = Vector(size) 
    
    self.timer = timer
    self.loop = loop
    self.timeLeft = timer
    
    self.frameList = frameList
    self.currentFrameIndex = 0

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
      if self.currentFrameIndex == len (self.frameList):
        
        if self.loop:
          self.currentFrameIndex = 0
        else:
          self.timeLeft = None #disable future updates
  
  def draw(self, screen, pos):
    
    #pos was the 'center' of the object, now we translate it
    # to the upper left corner for pygame
    x = pos[0] - self.frameSize[0]/2.0
    y = pos[1] - self.frameSize[1]/2.0
    
    #Note: pos should be upperleft coordinate of rect   
    pyRect = pygame.Rect((x,y), self.frameSize)    
    
    screen.blit(self.frameList[self.currentFrameIndex],
                pyRect)
      
      
class CollisionFilter:
  
  alwaysCollides = {'UNIT': ['UNIT']}
  
  #Collision occur only if objects belong to opposing teams
  enemyCollides = {'PROJECTILE': ['UNIT']}
  
  
  #keep track of objects that stop each other
  alwaysStop = {'UNIT' : ['UNIT']}
  
  @staticmethod
  def canCollide(a, b):   
    
    
    ac = CollisionFilter.alwaysCollides
    ec = CollisionFilter.enemyCollides
    
    if a.collisionType in ac.get(b.collisionType,[]) or \
      b.collisionType in ac.get(a.collisionType,[]):
      return True    
    elif a.team != b.team and (a.collisionType in ec.get(b.collisionType,[]) or \
      b.collisionType in ec.get(a.collisionType,[])):
      return True
    
    return False
  
  @staticmethod
  def canStop(a,b):
    """Used to determine if a unit stops another after a collision"""
    
    sd = CollisionFilter.alwaysStop
    
    if a.collisionType in sd.get(b.collisionType,[]) or \
      b.collisionType in sd.get(a.collisionType,[]):
      return True
    
    return False
  

 
class CollisionGrid(object):
  
  def __init__(self, worldSize):
    
    self.maxObjectSize = (64,64)
    
    self.numCols = int(worldSize[0] / self.maxObjectSize[0])
    self.numRows = int(worldSize[1] / self.maxObjectSize[1])    
    
    self.data = [[set() for x in range(self.numCols)] for y in range(self.numRows)]
    
    
  def getObjectsNearPos(self,pos):
    row = pos[1]/self.maxObjectSize[1]
    col = pos[0]/self.maxObjectSize[0]
    
  def getObjectsNearGrid(self,row,col):
    
    pass
  
  def getObjectsInCell(self,row,col):
    pass
      
      
class TestAnimation(Animation):
  
  def __init__(self, size, time=1.0, colorList=None):
    
    frameList = []
    
    if colorList is None:
      colorList = [(255,0,0),(0,255,0),(0,0,255)]
            
    for c in colorList:
      f = pygame.Surface(size)
      f.fill(c)
      frameList.append(f)      
    
    Animation.__init__(self,size,frameList,time,True)
    
  def setAnimation(selfself, string):
    pass
  
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
    
    #directions
    #self.north = self.allFramesList[1]
    #self.east = self.allFramesList[2]
    #self.south = self.allFramesList[0]
    #self.west = self.allFramesList[3]
    
    #self.northeast = self.allFramesList[5]
    #self.southeast = self.allFramesList[6]
    #self.southwest = self.allFramesList[4]
    #self.northwest = self.allFramesList[7]
    
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

class PlayerController(object):
  """Manipulate an object via input events""" 
  
  def __init__(self, target):
    
        
    self.moveUp = pygame.K_w
    self.moveDown = pygame.K_s
    self.moveLeft = pygame.K_a
    self.moveRight = pygame.K_d
    
    self.target = target
    
    self.attack = pygame.K_SPACE
      
  def process(self):
    
    vert = 0
    horiz = 0    
        
    if glad.input.isKeyPressed(self.moveUp):
      vert -= 1
    if glad.input.isKeyPressed(self.moveDown):
      vert += 1
    if glad.input.isKeyPressed(self.moveRight):
      horiz += 1
    if glad.input.isKeyPressed(self.moveLeft):
      horiz -= 1
      
    direction = (horiz, vert)
         
    self.target.requestMove(direction)
    
    #attack
    if glad.input.isKeyPressed(self.attack):
      self.target.attack()
     
class TestWalker(AbstractObject):
  
  def __init__(self, pos, **kwargs):    
    
    shape = Rect.createAtOrigin(64, 64)    
    AbstractObject.__init__(self, pos, shape, **kwargs)
    
    self.collisionType = 'UNIT'
    
    
class BasicUnit(AbstractObject):
  
  def __init__(self, pos, shape, **kwargs):
    AbstractObject.__init__(self, pos, shape, **kwargs)
    
    self.collisionType = 'UNIT'
  
    #Default statistics  
    self.strength = 10
    self.dexterity = 10
    self.constitution = 10
    self.intelligence = 10
    self.armor = 10    
    self.level = 1
    
    self.rangedWeapon = None
    self.meleeWeapon = None
    
    self.moveSpeed = 200
    
    #By default, have units face 'right'
    self.orientation = Vector(1,0)
    self.directionString = self.orientationToString()
    
    self.alwaysMove = False
    
    #turning
    self.turnTime = 0.08
    
    #Attacking
    self.attacking = False
    #attack animation
    self.shooting = False #think of better name
    self.attackTime = 0.1 #time attack frame is up
    self.attackTimer = 0
    
  def attack(self):
    #self.animation.rangedAttack(self.orientationToString())
    #NEED TO SET ATTACK ANIMATION WHEN ATTACKING
    #ALSO SYNC IT WITH THE ATTACKS (during attack - frame 1, between attacks - frame 2)
    #self.rangedAttack()
    self.attacking = True
    pass
    
  def meleeAttack(self, target):
    pass
  
  def rangedAttack(self):
    #spawn the ranged attack just outside of the rect
    
    #gap = space between center of player and center of projectile
    #TODO: abstract/put in the correct place
    gap = 16
    
    if self.rangedWeapon.attack(self.getPos(), 
                             gap, 
                             self.orientation,
                             self.team):
      return True
      #self.animation.rangedAttack(self.directionString)
    else:
      return False
  
  def orientationToString(self):
    #converts the orientation to a string
    #makes it easier for animation
    string = ''
    if self.orientation[0] == 0 and self.orientation[1] < 0:
      string = 'north'
    elif self.orientation[0] == 0 and self.orientation[1] > 0:
      string = 'south'
    elif self.orientation[0] > 0 and self.orientation[1] == 0:
      string = 'east'
    elif self.orientation[0] < 0 and self.orientation[1] == 0:
      string = 'west'
    elif self.orientation[0] < 0 and self.orientation[1] < 0:
      string = 'northwest'
    elif self.orientation[0] > 0 and self.orientation[1] > 0:
      string = 'southeast'
    elif self.orientation[0] < 0 and self.orientation[1] > 0:
      string = 'southwest'
    elif self.orientation[0] > 0 and self.orientation[1] < 0:
      string = 'northeast'
    
    return string
  
  def update(self, time): 
    
    if self.rangedWeapon:
      self.rangedWeapon.update(time)
    
    self.directionString = self.orientationToString()
    if not self.attacking and not self.shooting:
      self.animation.setAnimation(self.directionString)
      
    if self.shooting:
      self.attackTimer += time
      if self.attackTimer >= self.attackTime:
        self.attackTimer = 0
        self.animation.setAnimation(self.directionString)
        self.shooting = False
    
    if self.attacking:
      #check if melee or ranged
      #use ranged since melee isnt really set up
      if self.rangedAttack():
        self.shooting = True
        self.attackTimer = 0
        if not self.alwaysMove: #TODO fix attack animation for always move
          self.animation.rangedAttack(self.directionString)
    
    #update turnTime
    if self.turning:
      self.animation.setAnimation(self.directionString)
      self.turnTimer += time
      
        
    #animate only if moving and not shooting
    if not self.alwaysMove:
      if self.vel[0] != 0 or self.vel[1] != 0:
        if self.attacking and not self.shooting:
          self.animation.setAnimation(self.directionString)
          if self.animation:
            self.animation.update(time)
        if not self.attacking and not self.shooting:
          self.animation.setAnimation(self.directionString)
          if self.animation:
            self.animation.update(time)
    else:
      if self.animation:
        self.animation.update(time)
    
    #Turn of attacking unless its called in the next loop      
    self.attacking = False

class BasicProjectile(AbstractObject):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    AbstractObject.__init__(self, pos, shape, team, moveDir, **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
  
class Meteor(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    AbstractObject.__init__(self, pos, shape, team, moveDir, **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    
    self.orientation = Vector(moveDir)
    self.directionString = self.orientationToString()
    self.animation = AnimateRangedAttack('meteor', self.directionString)

class BasicRangedAttack(object):
  
  def __init__(self, size=(16,16)):
    
    self.nextAttackTimer = 0.0
    self.attackCooldown = 0.4
    
    self.size = size
    
  def update(self, time):
    
    self.nextAttackTimer -= time
    
    if self.nextAttackTimer < 0.0:
      self.nextAttackTimer = 0.0 
      
  def attack(self, pos, gap, orientation,team):
    
    if self.nextAttackTimer != 0.0:
      return False
    
    self.nextAttackTimer += self.attackCooldown
    
    #create a knife just outside the spawn location
    
    projectileShape = Rect.createAtOrigin(self.size[0], self.size[1])
        
    #TODO: how to handle diagonal movement and firing?
    # spawn outside rect, or inside?
    
    projectilePos = pos + orientation.getNormalized()*gap
    
    proj = Meteor(projectilePos,projectileShape,team,orientation) 
    
    glad.world.objectList.append(proj)
    
    return True
  
class KnifeThrower(object):
  """Spawns knives"""
  
  def __init__(self):
    
    #temporary defaults for now    
    self.maxKnives = 99
    self.knivesAvailable = 99
    
    self.nextAttackTimer = 0.0
    self.attackCooldown = 0.4
    
  def update(self, time):
    
    self.nextAttackTimer -= time
    
    if self.nextAttackTimer < 0.0:
      self.nextAttackTimer = 0.0   
  
  def attack(self, pos, gap, orientation,team):
    
    if self.nextAttackTimer != 0.0 or self.knivesAvailable == 0:
      #print 'cooldown: ', self.nextAttackTimer, self.knivesAvailable
      return False
    
    self.knivesAvailable -= 1
    self.nextAttackTimer += self.attackCooldown
    
    #create a knife just outside the spawn location
    
    knifeShape = Rect.createAtOrigin(10,10)
        
    #TODO: how to handle diagonal movement and firing?
    # spawn outside rect, or inside?
    
    knifePos = pos + orientation.getNormalized()*gap
    
    #print orientation.getNormalized() * gap
    
    
    
    proj = BasicProjectile(knifePos,knifeShape,team,orientation)
    
    
    glad.world.objectList.append(proj)
    
    return True
#   TODO: spawn knife here
    
    

class Soldier(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    #For now, just use BasicUnit Defaults
    
    #default soldier size    
    shape = Rect.createAtOrigin(32, 32)
      
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    self.animation = AnimateUnit('footman', self.directionString)
    
class FireElem(BasicUnit):
  #based off sample soldier for the start
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 32)
        
    BasicUnit.__init__(self, pos, shape, **kwargs)
        
    #self.rangedWeapon = KnifeThrower()
    self.rangedWeapon = BasicRangedAttack()
        
    self.animation = AnimateUnit('firelem', self.directionString)
    self.alwaysMove = True
   
class Archer(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 32)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    self.animation = AnimateUnit('archer', self.directionString)
    
class Archmage(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 28)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    self.animation = AnimateMage('archmage', self.directionString)

class Barbarian(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 28)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    self.animation = AnimateUnit('barby', self.directionString)
    
class Cleric(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 24)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    self.animation = AnimateUnit('cleric', self.directionString)
    
class Druid(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 22)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    self.animation = AnimateUnit('druid', self.directionString)
    
class Elf(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(20, 20)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    self.animation = AnimateUnit('elf', self.directionString)
    
class Faerie(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(16, 16)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    self.animation = AnimateUnit('faerie', self.directionString)
    self.alwaysMove = True
    
class Ghost(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(26, 28)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    self.animation = AnimateUnit('ghost', self.directionString)
    self.alwaysMove = True
    
class Golem(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(96, 72)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    self.animation = AnimateUnit('golem', self.directionString)
    
class Mage(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 28)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    self.animation = AnimateMage('mage', self.directionString) 

class Orc(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 32)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    self.animation = AnimateUnit('orc', self.directionString) 
    
class OrcCaptain(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 32)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    self.animation = AnimateUnit('orc2', self.directionString) 
    
class Skeleton(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(30, 26)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    self.animation = AnimateUnit('skeleton', self.directionString) 
    
class SmallSlime(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(24, 24)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    self.alwaysMove = True
    
    self.animation = AnimateSmallSlime('s_slime')

class MediumSlime(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(40, 40)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    self.alwaysMove = True
    
    self.animation = AnimateMediumSlime('m_slime')
    
class BigSlime(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(64, 64)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    self.alwaysMove = True
    
    self.animation = AnimateBigSlime('b_slime')
    
class Thief(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 26)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    self.animation = AnimateUnit('thief', self.directionString)     
    
class TestWorld(AbstractWorld):
  """Simple world for testing"""
  
  def __init__(self):
    AbstractWorld.__init__(self)
    
    #Create empty, boring grid
    
    gridWidth, gridHeight = (40,40)  
    
    #simple grass grid
    self.tileGrid = [[1 for x in range(gridWidth)] for y in range(gridHeight)]
    
    
    
    
    #add 1 testwalker
    #tw = TestWalker(pos=(100,100), size=(32,32))
    #self.objectList.append(tw)
    
    #add 1 soldier for testing
    sold1 = Soldier(pos=(100,100),team=1)    
    self.objectList.append(sold1)
    
    #add 1 firelem for testing
    firelem1 = FireElem(pos = (700,700), team = 1)
    self.objectList.append(firelem1)
    
    #add one of each unit for testing
    archer1 = Archer(pos=(700, 650))
    #barby1 = Barbarian(pos=(650, 650))
    #cleric1 = Cleric(pos=(650, 700))
    #druid1 = Druid(pos=(650, 750))
    #elf1 = Elf(pos=(700, 750))
    #faerie1 = Faerie(pos=(750, 650))
    #ghost1 = Ghost(pos=(750, 700))
    #golem1 = Golem(pos=(850, 700))
    #orc1 = Orc(pos=(750, 750))
    #orcCap1 = OrcCaptain(pos=(700, 800))
    #skel1 = Skeleton(pos=(600, 700))
    #thief1 = Thief(pos=(700, 600))
    #sold2 = Soldier(pos=(600, 600))
    mage1 = Mage(pos=(600, 800))
    #archmage1 = Archmage(pos=(800,800))
    smallSlime1 = SmallSlime(pos=(700, 900))
    #mSlime1 = MediumSlime(pos=(600, 900))
    #bSlime1 = BigSlime(pos=(800, 900))
    
    self.objectList.append(archer1)
    #self.objectList.append(barby1)
    #self.objectList.append(cleric1)
    #self.objectList.append(druid1)
    #self.objectList.append(elf1)
    #self.objectList.append(faerie1)
    #self.objectList.append(ghost1)
    #self.objectList.append(golem1)
    #self.objectList.append(orc1)
    #self.objectList.append(orcCap1)
    #self.objectList.append(skel1)
    #self.objectList.append(thief1)
    #self.objectList.append(sold2)
    self.objectList.append(mage1)
    #self.objectList.append(archmage1)
    self.objectList.append(smallSlime1)
    #self.objectList.append(mSlime1)
    #self.objectList.append(bSlime1)
    
    #TODO: put this someplace reasonable
    sold1.team = 1
    
            
    tw2 = TestWalker(pos=(300,300),team=2)
    self.objectList.extend([tw2])
    
    #TODO: put this someplace reasonable
    tw2.team = 2
    
    #setup controls for this testwalker
    #pc1 = PlayerController(sold1)
    #self.controllerList.append(pc1)
    pc2 = PlayerController(firelem1)
    self.controllerList.append(pc2)
    #setup controls so all units move in sync
    pc3 = PlayerController(archer1)
    self.controllerList.append(pc3)
    #pc4 = PlayerController(barby1)
    #self.controllerList.append(pc4)
    #pc5 = PlayerController(cleric1)
    #self.controllerList.append(pc5)
    #pc6 = PlayerController(druid1)
    #self.controllerList.append(pc6)
    #pc7 = PlayerController(elf1)
    #self.controllerList.append(pc7)
    #pc8 = PlayerController(faerie1)
    #self.controllerList.append(pc8)
    #pc9 = PlayerController(ghost1)
    #self.controllerList.append(pc9)
    #pc10 = PlayerController(golem1)
    #self.controllerList.append(pc10)
    #pc11 = PlayerController(orc1)
    #self.controllerList.append(pc11)
    #pc12 = PlayerController(orcCap1)
    #self.controllerList.append(pc12)
    #pc13 = PlayerController(skel1)
    #self.controllerList.append(pc13)
    #pc14 = PlayerController(thief1)
    #self.controllerList.append(pc14)
    #pc15 = PlayerController(sold2)
    #self.controllerList.append(pc15)
    pc16 = PlayerController(mage1)
    self.controllerList.append(pc16)
    #pc17 = PlayerController(archmage1)
    #self.controllerList.append(pc17)
    pc18 = PlayerController(smallSlime1)
    self.controllerList.append(pc18)
    #pc19 = PlayerController(mSlime1)
    #self.controllerList.append(pc19)
    #pc20 = PlayerController(bSlime1)
    #self.controllerList.append(pc20)
    
    #Set the first camera to follow the first testWalker
    #Note: the render must be initialized before the world
    cam1 = glad.renderer.cameraList[0]
    #print cam1
    cam1.followObject(firelem1)
    
    #TODO: don't hardcode tile sizes
    worldBoundingRect = (0,0,gridWidth*32,gridHeight*32)    
    self.worldBoundingRect = Rect(*worldBoundingRect)
    
    cam1.setWorldBoundingRect(worldBoundingRect) #TODO: don't hardcode tile sizes


    self.collisionGrid = CollisionGrid(worldBoundingRect[2:4])
    
    
    



"""
PASS THOGUH
ghost:
water
walls 
team projectiles

fairie:
water
team projectiles

walker:
team projectiles


2 questions: collision, stoppable


Projectiles:
collide with: walkers,flyers,ghosts, walls

walkers



Grid size:
#when adding objects to world, check that they are smaller than cell size

"""