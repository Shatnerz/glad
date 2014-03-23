import animation
from util import Rect, Vector

class AbstractObject(object):
  """All game world objects are ultimately derived from this class.
  Contains a variety of useful functions used for movement and 
  collision detection"""
  
  def __init__(self, pos, shape, team=1, moveSpeed = 50.0, moveDir=None):
    
    #General
    self.collisionType = None
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
    
    anim = animation.TestAnimation(size = shape.getSize())
    
    self.animationPlayer = animation.AnimationPlayer(anim, 1.0, True) 
    
    #set the team property
    self.team = team
    
    #Turning
    self.turning = False
    self.turnTime = 0.05
    self.turnTimer = 0
    
  def onCollide(self, object):
    """Handles collision"""
    pass
    #print object
    #if object.collisionType == 'PROJECTILE':
    #  print 'proj'
    
  def orientationToString(self):
    #converts the orientation to a string
    #makes it easier for animation
    #if self.orientation == None: #FIX FOR IF THERE IS NO ORIENTATION
     # return 'north'
    
    string = ''
    if self.orientation[0] == 0 and self.orientation[1] < 0:
      string = 'UP'
    elif self.orientation[0] == 0 and self.orientation[1] > 0:
      string = 'DOWN'
    elif self.orientation[0] > 0 and self.orientation[1] == 0:
      string = 'RIGHT'
    elif self.orientation[0] < 0 and self.orientation[1] == 0:
      string = 'LEFT'
    elif self.orientation[0] < 0 and self.orientation[1] < 0:
      string = 'UPLEFT'
    elif self.orientation[0] > 0 and self.orientation[1] > 0:
      string = 'DOWNRIGHT'
    elif self.orientation[0] < 0 and self.orientation[1] > 0:
      string = 'DOWNLEFT'
    elif self.orientation[0] > 0 and self.orientation[1] < 0:
      string = 'UPRIGHT'
    
    return string  
  
  def draw(self, screen, offset):
    
    #draw the animation, centered at the objects position
    # and offset according to the location of the camera    
    self.animationPlayer.draw(screen, self.getPos()+offset)
  
    
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
    #TODO: animations should be updated after collision detection
    
    #update the animation   
    if self.animationPlayer:
      self.animationPlayer.update(time)
    
    #update turning clock  
    if self.turning:
      self.turnTimer += time

class TestWalker(AbstractObject):
  
  def __init__(self, pos, **kwargs):    
    
    shape = Rect.createAtOrigin(64, 64)    
    AbstractObject.__init__(self, pos, shape, **kwargs)
    
    self.collisionType = 'UNIT'
    self.orientation = Vector(1,0)
    