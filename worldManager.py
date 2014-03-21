import pygame

import glad

#from multiMethod import multimethod

import unit, projectile

from util import Vector,Rect,getCollisionInfo,getOverlap

class AbstractWorld(object):
  
  def __init__(self):
    self.objectList = []
    self.controllerList = []
    
    self.worldBoundingRect = None

    
  def addObject(self, obj):
    """Add an object to the world, throws exception if the object
    can't be placed there"""
    
    #TODO: we should check for this somewhere, but not every time
    #we are using a grid to for broad-phase collision
    # detection, it assumes that no object is bigger than
    # the given size
  
  #TODO: handle placing object on top of another object
  
  def createTestGrid(self, (width, height)):
    
    #simple grass grid
    self.tileGrid = [[1 for x in range(width)] for y in range(height)]
    
    #the basic tile sizes are 32 x 32
    worldBoundingRect = (0,0,width*32,height*32)
    
    #Set the world bounding rectangle    
    self.worldBoundingRect = Rect(*worldBoundingRect)
    
  
  def draw(self, screen, offset):
    #draw corpses first then the rest
    for o in self.objectList:
      if isinstance(o, unit.Corpse):
        o.draw(screen, offset)
    for o in self.objectList:
      if not isinstance(o, unit.Corpse):
        o.draw(screen, offset)
      
  def getBoundingRect(self):
    return self.worldBoundingRect
      
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
      
      objI.onCollide(objJ)
      objJ.onCollide(objI)
      
      #print 'Collision: %s' % str(collisionInfo)
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
      
class TurretController(object):
  """Unit test controller that constantly fires"""
  def __init__(self, target):
    self.target = target
  def process(self):
    self.target.attack()  

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
    
    #I was bored
    if glad.input.isKeyTapped(pygame.K_q):
      glad.resource.resourceDict['yo'].play(self.target.pos)
    #Quick hack to switch characters
    if glad.input.isKeyTapped(pygame.K_TAB):
      if glad.world.objectList.__contains__(self.target):
        x = glad.world.objectList.index(self.target)
      else:
        x=0
      numObjects = len(glad.world.objectList)
      switch=False
      while switch==False:
        x += 1
        if x >= numObjects:
          x -= numObjects
        if isinstance(glad.world.objectList[x],unit.BasicUnit):
          self.target = glad.world.objectList[x]
          glad.renderer.cameraList[0].followObject(self.target)
          switch = True
     
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
    sold1 = unit.Soldier(pos=(100,100),team=1)    
    self.objectList.append(sold1)
    
    #add 1 firelem for testing
    firelem1 = unit.FireElem(pos = (700,700), team = 1)
    self.objectList.append(firelem1)
    
    #add one of each unit for testing
    archer1 = unit.Archer(pos=(700, 650))
    barby1 = unit.Barbarian(pos=(650, 650))
    cleric1 = unit.Cleric(pos=(650, 700))
    druid1 = unit.Druid(pos=(650, 750))
    elf1 = unit.Elf(pos=(700, 750))
    faerie1 = unit.Faerie(pos=(750, 650))
    ghost1 = unit.Ghost(pos=(750, 700))
    golem1 = unit.Golem(pos=(850, 700))################not up yet
    orc1 = unit.Orc(pos=(750, 750))
    orcCap1 = unit.OrcCaptain(pos=(700, 800))
    skel1 = unit.Skeleton(pos=(600, 700))################not up yet
    thief1 = unit.Thief(pos=(700, 600))
    sold2 = unit.Soldier(pos=(600, 600))
    #mage1 = unit.Mage(pos=(600, 800))
    #archmage1 = unit.Archmage(pos=(800,800))########################
    #smallSlime1 = unit.SmallSlime(pos=(700, 900))####################
    #mSlime1 = unit.MediumSlime(pos=(600, 900))
    #bSlime1 = unit.BigSlime(pos=(800, 900))
    
    self.objectList.append(archer1)
    self.objectList.append(barby1)
    self.objectList.append(cleric1)
    self.objectList.append(druid1)
    self.objectList.append(elf1)
    self.objectList.append(faerie1)
    self.objectList.append(ghost1)
    self.objectList.append(golem1)##################
    self.objectList.append(orc1)
    self.objectList.append(orcCap1)
    self.objectList.append(skel1)##################
    self.objectList.append(thief1)
    self.objectList.append(sold2)
    #self.objectList.append(mage1)
    #self.objectList.append(archmage1)#################
    #self.objectList.append(smallSlime1)#################
    #self.objectList.append(mSlime1)
    #self.objectList.append(bSlime1)
    
    #TODO: put this someplace reasonable
    sold1.team = 1
    
            
    tw2 = unit.TestWalker(pos=(300,300),team=2)
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
    pc4 = PlayerController(barby1)
    self.controllerList.append(pc4)
    pc5 = PlayerController(cleric1)
    self.controllerList.append(pc5)
    pc6 = PlayerController(druid1)
    self.controllerList.append(pc6)
    pc7 = PlayerController(elf1)
    self.controllerList.append(pc7)
    pc8 = PlayerController(faerie1)
    self.controllerList.append(pc8)
    pc9 = PlayerController(ghost1)
    self.controllerList.append(pc9)
    pc10 = PlayerController(golem1)#############
    self.controllerList.append(pc10)##############
    pc11 = PlayerController(orc1)
    self.controllerList.append(pc11)
    pc12 = PlayerController(orcCap1)
    self.controllerList.append(pc12)
    pc13 = PlayerController(skel1)#############
    self.controllerList.append(pc13)##########
    pc14 = PlayerController(thief1)
    self.controllerList.append(pc14)
    pc15 = PlayerController(sold2)
    self.controllerList.append(pc15)
    #pc16 = PlayerController(mage1)
    #self.controllerList.append(pc16)
    #pc17 = PlayerController(archmage1)###############
    #self.controllerList.append(pc17)################
    #pc18 = PlayerController(smallSlime1)###########
    #self.controllerList.append(pc18)##############
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
    
    

class TestWorld1(AbstractWorld):
  """Simple world for testing"""
  
  def __init__(self):
    AbstractWorld.__init__(self)
    
    #Create empty, boring grid    
    self.createTestGrid((40,40))
    
    #add 1 soldier for testing
    sold1 = unit.Soldier(pos=(100,100),team=0)
    sold1.rangedWeapon = projectile.KnifeThrower(sold1,10)
    #sold1.rangedWeapon = unit.SlimeAttack(sold1,sold1.hue)
    #sold1.rangedWeapon.knivesAvailable = 15
    #sold1.animationPlayer.timer=0.1
    #sold1 = unit.SmallSlime(pos=(100,100),team=1)
    #sold1 = unit.Golem(pos=(100,100),team=1)
    #sold1 = unit.TestWalker(pos=(100,100),team=1)
    
    sold1.rangedWeapon.attackCooldown=.2
    
    sold2 = unit.Soldier(pos=(200,200), team=1)
    sold3 = unit.FireElem(pos=(200, 100), team=0)
    
    #sold4 = unit.FireElem(pos=(300, 100), team=0)
    #sold5 = unit.FireElem(pos=(400, 100), team=0)
    #sold6 = unit.FireElem(pos=(500, 100), team=0)
    #sold7 = unit.FireElem(pos=(200, 300), team=0)
    #sold8 = unit.FireElem(pos=(200, 400), team=0)
    #sold9 = unit.FireElem(pos=(200, 500), team=0)
    
    self.objectList.append(sold1)
    self.objectList.append(sold2)
    self.objectList.append(sold3)
    
    #self.objectList.append(sold4)
    #self.objectList.append(sold5)
    #self.objectList.append(sold6)
    #self.objectList.append(sold7)
    #self.objectList.append(sold8)
    #self.objectList.append(sold9)
    
    #set the player to control this unit
    pc1 = PlayerController(sold1)
    self.controllerList.append(pc1)
    tc1 = TurretController(sold2)
    self.controllerList.append(tc1)
                
    #set the camera to follow this unit
    cam1 = glad.renderer.cameraList[0]
    cam1.followObject(sold1)
    
    #HUD testing
    #print cam1.overlay


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