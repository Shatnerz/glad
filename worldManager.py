import pygame

import glad

#from multiMethod import multimethod

from util import Vector,Rect,getCollisionInfo,getOverlap


class AbstractWorld(object):
  
  def __init__(self):
    self.objectList = []
    self.controllerList = []
    
  def addObject(self, pos):
    """Add an object to the world, throws exception if the object
    can't be placed there"""
    pass
  
  def draw(self, screen, offset):
    for o in self.objectList:
      o.draw(screen, offset)
      
  def generateCollisionList(self, time):
    """Generate a dictionary of collisions between object
    TODO: FINISH DOC HERE
    
    only considers collisions that happen <= time"""
    
    #d = {}
    l = []
    
    #TODO: improve, this is O(n^2) for testing
    
    for i in range(len(self.objectList)):      
      for j in range(i+1, len(self.objectList)):
        
        objI = self.objectList[i]
        objJ = self.objectList[j]
        
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
    within the bounding box of an objects trajectory during time"""
    
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
      
      
      
#      width,height = self.objectList[i].getRect().getSize()
#      
#      lx = min(p1[0],p2[0])
#      rx = max(p1[0]+width, p2[0]+width)
#      
#      ty = min(p1[1],p2[1])
#      by = max(p1[1]+height, p2[1]+height)
#      
#      Rect(pos=(lx,ty), size=(rx-lx, by-ty))
      
      boundDict[i] = bbox
                
    d = {}
    
    #TODO: improve, this is O(n^2) for testing
    
    for i in range(len(self.objectList)):      
      for j in range(i+1, len(self.objectList)):
        
        iObj = self.objectList[i]
        jObj = self.objectList[j]
        
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
      o.updatePos(time)
      
    #update animations, weapons, other stuff
    for o in self.objectList:
      o.update(time)


class AbstractObject(object):
  """All game world objects are ultimately derived from this class.
  Contains a variety of useful functions used for movement and 
  collision detection"""
  
  def __init__(self, pos, shape, moveSpeed = 0.0, moveDir=None):
    
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
      self.moveDir.normalize()
    
    self.vel = self.moveDir * self.moveSpeed
      
    #Keep track of where the objects wants to go next
    self.requestedPos = pos
    
    #Set up the animation object
    #TODO: this is temporary for testing
    self.animation = TestAnimation(shape.getSize())
    
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
    """Indicate whe preferred direction this object wants to go"""  
    
    assert direction is not None

    #update the direction
    self.moveDir = Vector(direction)
    
    #update the objects velocity
    #TODO: what if the move direction is 0 vector?    
    if not self.moveDir.isNullVector():
      self.moveDir.normalize()
      
    self.vel = self.moveDir*self.moveSpeed
        
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
    
class TestAnimation(Animation):
  
  def __init__(self, size, time=1.0, colorList=None):
    
    frameList = []
    
    if colorList is None:
      colorList = [(0,0,64),(0,0,128),(0,0,192)]
            
    for c in colorList:
      f = pygame.Surface(size)
      f.fill(c)
      frameList.append(f)      
    
    Animation.__init__(self,size,frameList,time,True)
    
    
 
 
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
    
    shape = Rect.createAtOrigin(320, 320)    
    AbstractObject.__init__(self, pos, shape, **kwargs)
    
    
class BasicUnit(AbstractObject):
  
  def __init__(self, pos, shape, **kwargs):
    AbstractObject.__init__(self, pos, shape, **kwargs)    
  
    #Default statistics  
    self.strength = 10
    self.dexterity = 10
    self.constitution = 10
    self.intelligence = 10
    self.armor = 10    
    self.level = 1
    
    self.rangedWeapon = None
    self.meleeWeapon = None    
    
  def attack(self):
    self.rangedAttack()
    pass
    
  def meleeAttack(self, target):
    pass
  
  def rangedAttack(self):
    
    #spawn the ranged attack just outside of the rect
    
    self.rangedWeapon.attack(self.getCenterPos(), self.size, self.faceDir)
    pass
  
  def update(self, time):
    AbstractObject.update(self, time)
    
    self.rangedWeapon.update(time)
  
  

class BasicProjectile(AbstractObject):
  def __init__(self, **kwargs):
    
    AbstractObject.__init__(self, **kwargs)
    
    self.speed = 450.0
    
    #
    x,y = self.faceDir
    
    
    speed = self.speed
    norm = math.sqrt(x*x + y*y)
      
    #keep track of vx/vy so we don't have to keep recalculating
    vx = float(speed*x/norm)
    vy = float(speed*y/norm)
    
    self.moveSpeed = (vx,vy)
  
  
  
class KnifeThrower(object):
  """Spawns knives"""
  
  def __init__(self):
    
    #temporary defaults for now    
    self.maxKnives = 99
    self.knivesAvailable = 99
    
    self.nextAttackTimer = 0.0
    self.attackCooldown = 1.0
    
  def update(self, time):
    
    self.nextAttackTimer -= time
    
    if self.nextAttackTimer < 0.0:
      self.nextAttackTimer = 0.0   
  
  def attack(self, centerPos, size, faceDir):
    
    if self.nextAttackTimer != 0.0 or self.knivesAvailable == 0:
      print 'cooldown: ', self.nextAttackTimer, self.knivesAvailable
      return #do nothing
    
    self.knivesAvailable -= 1
    self.nextAttackTimer += self.attackCooldown
    
    #create a knife just outside the spawn location
    
    knifeSize = (10,10)
    
    #TODO: how to handle diagonal movement and firing?
    # spawn outside rect, or inside?
    
    print faceDir
    
    kcx = centerPos[0] + (knifeSize[0]/2.0 + size[0]/2.0) * faceDir[0]
    kcy = centerPos[1] + (knifeSize[1]/2.0 + size[1]/2.0) * faceDir[1]
    
    
    proj = BasicProjectile(size = knifeSize)    
    
    proj.setCenterPos((kcx,kcy))
    
    proj.movedDir = faceDir    
    
  
    
    
    glad.world.objectList.append(proj)
    #TODO: spawn knife here
    
      

class Soldier(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    #For now, just use BasicUnit Defaults
    
    #default soldier size    
    shape = Rect.createAtOrigin(32, 32)
      
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
  
    self.moveSpeed = 300.0
    self.rangedWeapon = KnifeThrower()
    
class Firelem(BasicUnit):
    #based of sample soldier for the start
    def __init__(self, pos, **kwargs):
        shape = Rect.createAtOrigin(32, 32)
        
        BasicUnit.__init__(self, pos, shape, **kwargs)
        self.moveSpeed = 300;
        self.rangedWeapon = KnifeThrower()
    
    
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
    sold1 = Soldier(pos=(100,100))    
    self.objectList.append(sold1)
    
    #add 1 firelem for testing
    firelem1 = Firelem(pos = (100,200))
    self.objectList.append(firelem1)
    
            
    tw2 = TestWalker(pos=(300,300))
    self.objectList.extend([tw2])
    
    #setup controls for this testwalker
    #pc1 = PlayerController(sold1)
    #self.controllerList.append(pc1)
    pc2 = PlayerController(firelem1)
    self.controllerList.append(pc2)
    
    #Set the first camera to follow the first testWalker
    #Note: the render must be initialized before the world
    cam1 = glad.renderer.cameraList[0]
    #print cam1
    cam1.followObject(firelem1)
    
    
    cam1.setWorldBoundingRect((0,
                               0,
                               gridWidth*32, #TODO: don't hardcode tile sizes
                               gridHeight*32)) #TODO: don't hardcode tile sizes




