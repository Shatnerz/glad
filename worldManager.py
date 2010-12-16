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
      
  def update(self, time):
    
    for c in self.controllerList:
      c.process()
    
    for object in self.objectList:
      object.update(time)   


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
    
  def getPosInTime(self, time):
           
    x, y = self.movedDir    
    speed = self.speed
    
    if (x,y) != (0,0):
      norm = math.sqrt(x*x + y*y)
      
      #keep track of vx/vy so we don't have to keep recalculating
      vx = float(speed*x/norm)
      vy = float(speed*y/norm)
      
      self.moveSpeed = (vx,vy)
      
      return (self.pos[0] + vx*time, self.pos[1] + vy*time)
    else:
      return self.pos
    
  def getRect(self):
    return (self.pos[0],self.pos[1],
            self.size[0],self.size[1])
    
  def getRequestedPos(self):
    return self.requestedPos  
    
  def requestMove(self, direction):
    """Indicate whe preferred direction this object wants to go"""
    
    assert direction is not None    
    self.movedDir = direction
        
  def updatePos(self, time):
    self.pos = self.requestedPos
    
  def update(self, time):
    
    self.requestedPos = self.getPosInTime(time)
    
    self.updatePos(time)

 
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


  
class TestWalker(AbstractObject):
  
  def __init__(self, **kwargs):
    AbstractObject.__init__(self,**kwargs)
    
    #speed is in pixels / second
    self.speed = 150.0
        
  def draw(self, screen, offset):
    
    newRect = self.getRect()
    
    pygame.draw.rect(screen, (128,128,0), newRect)    
    
    
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
    
    #setup controls for this testwalker
    pc1 = PlayerController(tw)
    self.controllerList.append(pc1)

