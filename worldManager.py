import math

import pygame

import glad

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
        
        r1 = objI.getRect()
        r1vel = objI.getVelocity()
        r2 = objJ.getRect()
        r2vel = objJ.getVelocity()        
        
        colInfo = Rect.getCollisionInfo(r1, r1vel, r2, r2vel)
        
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
      
      width,height = self.objectList[i].getRect().getSize()
      
      lx = min(p1[0],p2[0])
      rx = max(p1[0]+width, p2[0]+width)
      
      ty = min(p1[1],p2[1])
      by = max(p1[1]+height, p2[1]+height)
      
      boundDict[i] = Rect(pos=(lx,ty), size=(rx-lx, by-ty))
                
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
    obj.moveSpeed = (0.0,0.0)
    
    #remove all references to obj from collisionList
    
    collisionList = [x for x in collisionList if x[1] is not obj and x[3] is not obj]
    
    #Now, recalculate collision for all of its check if any of its neighbors
    
    
    r1 = obj.getRect()
    r1vel = obj.getVelocity()    
    
    for n in neighborDict[obj]:
      
        r2 = n.getRect()
        r2vel = n.getVelocity()
        
        colInfo = Rect.getCollisionInfo(r1, r1vel, r2, r2vel)
        
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

    for c in self.controllerList:
      c.process()    
    
    #First move everything
    for o in self.objectList:      
      o.update(time)
      
    #Resolve collisions
    self.greedyCollisionDetection(time)
    
    #Finalize positions
    for o in self.objectList:
      o.updatePos(time)  


class AbstractObject(object):
  
  def __init__(self, pos=None, size=None):
    self.pos = pos
    self.size = size
    
    #ghost - walls, 
    
    #fly through walls
    #fly over water
    #fly through people    
    
    self.movedDir = (0,0)    
    self.moveSpeed = (0.0,0.0)
    
    self.requestedPos = pos
    
    #TODO: make a moveable and immobile objects class
    self.speed = 0.0
    
  def getCenter(self):
    
    cx = self.pos[0] + self.size[0]/2.0
    cy = self.pos[1] + self.size[1]/2.0
    
    return (cx,cy)
    
  def getPosInTime(self, time):
    
    vx,vy = self.moveSpeed
    
    return (self.pos[0] + vx*time, self.pos[1] + vy*time)   
           
#    x, y = self.movedDir    
#    speed = self.speed
#    
#    if (x,y) != (0,0):
#      norm = math.sqrt(x*x + y*y)
#      
#      #keep track of vx/vy so we don't have to keep recalculating
#      vx = float(speed*x/norm)
#      vy = float(speed*y/norm)
#      
#      self.moveSpeed = (vx,vy)
#      
#      return (self.pos[0] + vx*time, self.pos[1] + vy*time)
#    else:
#      return self.pos
    
  def getRect(self):
    #return (self.pos[0],self.pos[1],
    #        self.size[0],self.size[1])
    
    return Rect(self.pos, self.size)
    
  def getRequestedPos(self):
    return self.requestedPos
  
  def getVelocity(self):
    return self.moveSpeed
  
  def isCollision(self, o,requested=False):
    #request=True means we check requested positions
    """Check if this object's rect overlaps the other's rect"""
    
    if requested:
      ax1,ay1 = self.requestedPos
    else:
      ax1,ay1 = self.pos
    ax2,ay2 = ax1+self.size[0],ay1+self.size[1]
    
    if requested:
      bx1,by1 = o.requestedPos
    else:
      bx1,by1 = o.pos
    bx2,by2 = bx1+o.size[0],by1+o.size[1]
    
    if ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1:
      return True
    else:
      return False
    
  def requestMove(self, direction):
    """Indicate whe preferred direction this object wants to go"""
    
    assert direction is not None    
    self.movedDir = direction
    
    x,y = self.movedDir
    if (x,y) != (0,0):
      speed = self.speed
      norm = math.sqrt(x*x + y*y)
      
      #keep track of vx/vy so we don't have to keep recalculating
      vx = float(speed*x/norm)
      vy = float(speed*y/norm)
    
      self.moveSpeed = (vx,vy)
    else:
      self.moveSpeed = (0.0,0.0)
        
  def updatePos(self, time):
    self.pos = self.requestedPos
    
  def update(self, time):
    
    self.requestedPos = self.getPosInTime(time)
    
    #self.updatePos(time)
    
    #TODO: animaitons should be updated after collision detection
    #update the animation
    self.anim.update(time)

class Animation(object):
  def __init__(self, frameList, timer, loop=False):
    
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
    
    #draw offsets
    
    pyRect = pygame.Rect(pos.getPos(),pos.getSize())    
    
    screen.blit(self.frameList[self.currentFrameIndex],
                pyRect)
    
    
  
class AnimationPlayer(object):
  def __init__(self):
    pass
 
class PlayerController(object):
  """Manipulate an object via input events""" 
  
  def __init__(self, target):
    
    self.moveUp = 'w'
    self.moveDown = 's'
    self.moveLeft = 'a'
    self.moveRight = 'd'
    
    self.target = target
      
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
    



class Rect(object):
  """Basic rectangle class. Contains overlap checking"""
  
  def __init__(self, pos, size):
    self.pos = pos
    self.size = size
    
  def __repr__(self):
    return 'Rect: %s %s' % (self.pos, self.size)
    
  def getCenter(self):
    
    return (self.pos[0] + self.size[0]/2.0, 
            self.pos[1] + self.size[1]/2.0)
    
  @staticmethod
  def touches(a,b):
    """Checks if 2 rectangles intersect each other"""
    
    ax1 = a.pos[0]
    ax2 = a.pos[0] + a.size[0]
    ay1 = a.pos[1]
    ay2 = a.pos[1] + a.size[1]
    
    bx1 = b.pos[0]
    bx2 = b.pos[0] + b.size[0]
    by1 = b.pos[1]
    by2 = b.pos[1] + b.size[1]
    
    #uses <= vs < because when rectangles are touching, they don't intersect
    
    if ax1 <= bx2 and ax2 >= bx1 and \
      ay1 <= by2 and ay2 >= by1:
      return True
    else:
      return False
    
  def getPos(self):
    return self.pos
  
  def getSize(self):
    return self.size
    
  @staticmethod
  def getAxisProjCollisionRange((a1,a2),av,(b1,b2),bv):
    """TODO: document this"""
    
    if (bv-av) == 0.0:
      #no relative movement on this axis, 2 scenarios
      
      #TODO:, decide about >= vs >
      
      #1 already overlapping
      if a2 > b1 and a1 < b2:
        return 'OVERLAPS' #always overlapping
      else:
        return 'NEVER_OVERLAPS' #never overlap
      # not overlapping, return None
    else:      
      t1 = (a2-b1)/(bv-av)    # a2+avt >= b1+bvt
      t2 = (a1-b2)/(bv-av)    # a1+avt <= b2+bvt
      
    return (min(t1,t2), max(t1,t2))
  
  def getXProjAtTime(self, time, vel):    
    x1 = self.pos[0] + vel[0]*time    
    return (x1, x1+self.size[0])
  
  def getYProjAtTime(self, time, vel):       
    y1 = self.pos[1] + vel[1]*time    
    return (y1, y1+self.size[1])   
    
  
  @staticmethod
  def collisionStopsMovement(ax,ay,r1vel,bx,by):
    #check if the collision will stop forward movement at this time
    if r1vel[0] > 0.0:      
      if ax[1] >= bx[0]:
        return True    
    elif r1vel[0] < 0.0:
      if ax[0] <= bx[1]:
        return True
    
    if r1vel[1] > 0.0:
      if ay[1] >= by[0]:
        return True
    elif r1vel[1] < 0.0:
      if ay[0] <= by[1]:
        return True   
      
    return False
      
  
  @staticmethod
  def getCollisionInfo(r1, r1vel, r2, r2vel):    
    """Returns a tuple with the collision time between r1 and r2,
    and whether this collision could potentially stop r1's movement"""
    
    time = None
    isStopping = None
    
    xRange = Rect.getAxisProjCollisionRange(r1.getXProj(),
                                            r1vel[0],
                                            r2.getXProj(),
                                            r2vel[0])
    
    yRange = Rect.getAxisProjCollisionRange(r1.getYProj(),
                                            r1vel[1],
                                            r2.getYProj(),
                                            r2vel[1])
    
    #print 'xrange: ', xRange
    #print 'yrange: ', yRange
    
        
    if xRange == 'OVERLAPS' and yRange == 'OVERLAPS':
      #print 'overlaps!!!!!'
      time = 0.0 #objects already overlap      
    elif xRange == 'NEVER_OVERLAPS' or yRange == 'NEVER_OVERLAPS':
      time = 'NEVER_OVERLAPS'
    elif xRange == 'OVERLAPS':
      #if times have different signs, we are inside
      if yRange[0]*yRange[1] < 0:
        time = 0.0
      else:
        time = min(yRange)
    elif yRange == 'OVERLAPS':
      #if times have different signs, we are inside
      if xRange[0]*xRange[1] < 0:
        time = 0.0
      else:
        time = min(xRange)
    else: #xRange and yRange both have valid intervals
      #TODO: FINISH THIS      
      overlap = getOverlap(xRange,yRange)
      
#      print 'DEBUG!'
#      print 'overlap', overlap
      
      if overlap is None:
        return None
      else:
        #TODO: WRONG!!!
        #time = overlap
        time = overlap[0]        
        
      if xRange[0]*xRange[1] < 0 and yRange[0]*yRange[1] < 0:
        #we are inside
        time = 0.0
      
    if time == 'NEVER_OVERLAPS':
      return None
    
    #TODO: should we allow negatives times and deal with later
    if time < 0:      
      return None
    
    
    #TODO: calc if each object will hae it's movement stopped
    
    #get positions at time
    ax = r1.getXProjAtTime(time,r1vel)
    bx = r2.getXProjAtTime(time,r2vel)
    
    ay = r1.getYProjAtTime(time,r1vel)
    by = r2.getYProjAtTime(time,r2vel)
    
    
    r1Stops = Rect.collisionStopsMovement(ax,ay,r1vel,bx,by) 
    r2Stops = Rect.collisionStopsMovement(bx,by,r2vel,ax,ay)
    
     
    
    return (time,r1Stops,r2Stops)              
  
  def getXProj(self):
    return (self.pos[0],self.pos[0]+self.size[0])
  
  def getYProj(self):
    return (self.pos[1],self.pos[1]+self.size[1])


  
class TestWalker(AbstractObject):
  
  def __init__(self, **kwargs):
    AbstractObject.__init__(self,**kwargs)
    
    #speed is in pixels / second
    self.speed = 150.0
    
    #create three simple frame images for testing
    f1 = pygame.Surface(self.size)
    f2 = pygame.Surface(self.size)
    f3 = pygame.Surface(self.size)
    
    f1.fill((128,128,0))
    f2.fill((64,128,0))
    f3.fill((128,64,0))
    
    self.anim = Animation([f1,f2,f3],.25,True)
        
  def draw(self, screen, offset):
    
    newRect = self.getRect()
    
    #TODO: handle screen offset
    
    x = newRect.pos[0] - offset[0]
    y = newRect.pos[1] - offset[1]
    
    self.anim.draw(screen, Rect(pos=(x,y),size=newRect.size))
    
    #pygame.draw.rect(screen, (128,128,0), newRect)    
    
    
class TestWorld(AbstractWorld):
  """Simple world for testing"""
  
  def __init__(self):
    AbstractWorld.__init__(self)
    
    #Create empty, boring grid
    
    gridWidth, gridHeight = (40,40)  
    
    #simple grass grid
    self.tileGrid = [[1 for x in range(gridWidth)] for y in range(gridHeight)]
    
    #add 1 testwalker
    tw = TestWalker(pos=(100,100), size=(32,32))   
    self.objectList.append(tw) 
    
    #add 2 more testwalkers for collision detection
    tw2 = TestWalker(pos=(200,100), size=(320,320))    
    #tw3 = TestWalker(pos=(200,200), size=(32,32))
    #self.objectList.extend([tw2,tw3])
    self.objectList.extend([tw2])
    
    #setup controls for this testwalker
    pc1 = PlayerController(tw)
    self.controllerList.append(pc1)
    
    #Set the first camera to follow the first testWalker
    #Note: the render must be initialized before the world
    cam1 = glad.renderer.cameraList[0]
    print cam1
    cam1.followObject(tw)


def getOverlap((aMin,aMax),(bMin,bMax)):
  
  #TODO: note, using >= / <= for first 2 if's eliminates touching
  # as an intersection
  
  if aMax < bMin or aMin > bMax:
    return None
  else:  
    #return min(aMax, bMax) - max(aMin, bMin)
    #return a tuple
    return (max(aMin,bMin),min(aMax,bMax))
