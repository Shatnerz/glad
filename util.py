import math

from multiMethod import multimethod

class Vector(object):
  """Basic vector class with convenience functions"""
  
  def __init__(self, *args):
    """Accepts 4 inputs: e.g 
      Vector(1,2,3)
      Vector(v) # where v is an instance of Vector
      Vector([1,2,3])
      Vector((1,2,3))"""        
    
    #TODO: consolidate these if statements
    
    #If a vector is passed as an argument, make a copy
    if len(args) == 1 and isinstance(args[0],Vector):
      args = args[0]    
    
    elif isinstance(args[0],(list,tuple)):
      args = args[0]    
    
    self.data = [float(x) for x in args]
    
  def __repr__(self):
    return 'Vector'+str(self.data)
  
  def __add__(self, v):
    assert isinstance(v,Vector)
    assert len(self) == len(v)
    
    data = self.data[:] #get copy of data
    
    for x in range(len(self)):
      data[x] = self.data[x] + v.data[x]
      
    return Vector(data)
  
  def __sub__(self,v):
    
    a = self*-1
    return a+v
  
  def __eq__(self, v):    
    return (self-v).isNullVector()     
  
  def __getitem__(self, i):
    return self.data[i]
  
  def __setitem__(self,i,val):
    self.data[i] = val
    
  def __len__(self):
    return len(self.data)
  
  def __mul__(self, scalar):
    data = [x*scalar for x in self.data]
    return Vector(data)  
    
  def copy(self):
    v = Vector(self.data[:])    
    return v
    
  def getNorm(self):
    
    sum = 0.0
    for x in self.data:
      sum += x*x
      
    assert sum != 0.0, "Calculated norm of 0 vector"
    
    return math.sqrt(sum)
  
  def isNullVector(self):
    
    for x in self.data:
      if x != 0.0: return False
      
    return True
  
  def getNormalized(self):
    """Returns a new normalized version of self"""
    
    norm = self.getNorm()
    
    data = [x/norm for x in self.data]
    
    return Vector(data)
    

class Rect(object):
  """Basic rectangle class. Contains overlap checking"""
  
  def __init__(self, x1,y1,x2,y2):
    """Constructs a rectangle with from the above points"""
    
    self.x1 = min(x1,x2)
    self.x2 = max(x1,x2)
    
    self.y1 = min(y1,y2)
    self.y2 = max(y1,y2) 
    
  def __repr__(self):
    return 'Rect: %0.2f %0.2f %0.2f %0.2f' % (self.x1,self.y1,self.x2,self.y2)
  
  @staticmethod
  def createAtOrigin(width, height):
    
    r = Rect(-width/2.0,-height/2.0,width/2.0,height/2.0)
    return r
  
  @staticmethod
  def union(a,b):
    """Returns a rectangle containing both a, b"""
    
    lx = min(a.x1,b.x1)
    rx = max(a.x2,b.x2)
      
    ty = min(a.y1,b.y1)
    by = max(a.y2,b.y2)
    
    return Rect(lx,ty,rx,by)
  
  def contains(self, point):
    
    if point[0] > self.x2 or point[1] > self.y2:
      return False
    
    if point[0] < self.x1 or point[1] < self.y1:
      return False
    
    return True
    
    
  def getBoundingBox(self):
    """Since this is a rectangle, we just return a itself"""
    
    return self   
    
  def getCenter(self):
    """Returns center of the rect"""
    
    return ( (self.x1 + self.x2)/2.0,
             (self.y1 + self.y2)/2.0)
    
  @staticmethod
  def touches(a,b):
    """Checks if 2 rectangles intersect each other"""
    
    ax1 = a.x1
    ax2 = a.x2
    ay1 = a.y1
    ay2 = a.y2
    
    bx1 = b.x1
    bx2 = b.x2
    by1 = b.y1
    by2 = b.y2
    
    #uses <= vs < because when rectangles are touching, they don't intersect
    
    if ax1 <= bx2 and ax2 >= bx1 and \
      ay1 <= by2 and ay2 >= by1:
      return True
    else:
      return False
    
  def translate(self, v):
    
    return Rect(self.x1+v[0], self.y1+v[1], 
                self.x2+v[0], self.y2+v[1])

  def getSize(self):
    """Returns tuple containing (width, height)"""
    return (self.x2-self.x1,self.y2-self.y1)
    
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
    x1 = self.x1 + vel[0]*time    
    return (x1, x1+self.x2-self.x1)
  
  def getYProjAtTime(self, time, vel):       
    y1 = self.y1 + vel[1]*time    
    return (y1, y1+self.y2-self.y1)   
    
  
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
  
  def getXProj(self):
    return (self.x1,self.x2)
  
  def getYProj(self):
    return (self.y1,self.y2)



def getOverlap((aMin,aMax),(bMin,bMax)):
  
  #TODO: note, using >= / <= for first 2 if's eliminates touching
  # as an intersection
  
  if aMax < bMin or aMin > bMax:
    return None
  else:  
    #return min(aMax, bMax) - max(aMin, bMin)
    #return a tuple
    return (max(aMin,bMin),min(aMax,bMax)) 
  
  
@multimethod(Rect,Vector,Rect,Vector)
def getCollisionInfo(r1,r1vel,r2,r2vel):
  """Returns a tuple with the collision time between rects r1 and r2,
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