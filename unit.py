
import glad
import animation

from util import Rect, Vector

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
    
    anim = animation.TestAnimation(size = shape.getSize())
    
    self.animationPlayer = animation.AnimationPlayer(anim, 1.0, True) 
    
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
    
    
class BasicUnit(AbstractObject):
  
  def __init__(self, pos, shape, hue=180, name='SOLDIER', slime=False, **kwargs):
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
    self.directionString = self.orientationToString() #may not be needed
    
    #self.name = "SOLDIER" #might as well be soldier by default, name used to load animations with current name format
    self.name=name
    self.slime=slime
    if self.slime:
        self.currentAnimation = 'ANIM_' + self.name +'_MOVE'
    else:
        self.currentAnimation = 'ANIM_' + self.name +'_MOVE' + self.orientationToString()
    self.animationPlayer = animation.AnimationPlayer(glad.resource.resourceDict[self.currentAnimation], 0.2, True)
    
    self.alwaysMove = False
    
    #turning
    self.turnTime = 0.08
    
    #Attacking
    self.attacking = False
    #attack animation
    self.shooting = False #think of better name
    self.attackTime = 0.1 #time attack frame is up
    self.attackTimer = 0
    
    self.hue = hue
    
    #Wasn't sure how sync sync attack animation with attack well
    #this was the easiest thing i could think of
    #may be able to change Animation or AnimationPLayer for better method
    self.animateAttack = False
    self.animateAttackTimer = 0
    
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
  
  def update(self, time):
    
    oldAnimation = self.currentAnimation
    
    if self.rangedWeapon:
      self.rangedWeapon.update(time)
    
    self.directionString = self.orientationToString()
    
    #update current animation
    if self.slime:
      self.currentAnimation = 'ANIM_' + self.name +'_MOVE'
    else:
      if not self.animateAttack:
        self.currentAnimation = 'ANIM_' + self.name +'_MOVE' + self.directionString
    
    if not self.attacking and not self.shooting:
      #self.animation.setAnimation(self.directionString)####
      pass
      
    if self.shooting:
      self.attackTimer += time
      if self.attackTimer >= self.attackTime:
        self.attackTimer = 0
        #self.animation.setAnimation(self.directionString)###
        self.shooting = False
        
    #must be better way to sync attack and animation
    #without this animation is only on for 1 loop
    if self.animateAttack:
      cooldown = 0.01 ##should be less then weapon cooldown so it doesnt stick
      if self.animateAttackTimer >= cooldown:
        self.animateAttack = False
      else:
        self.animateAttackTimer += time
    
    if self.attacking:
      #check if melee or ranged
      #use ranged since melee isnt really set up
      if self.rangedAttack():
        self.shooting = True
        self.attackTimer = 0 #reset attack timer
            
        #sets animation to attack and starts timer when animation cannot change
        if not self.slime:
          self.currentAnimation = 'ANIM_' + self.name + '_ATTACK' + self.directionString       
          self.animationPlayer.animation = glad.resource.resourceDict[self.currentAnimation]
          self.animationPlayer.currentFrameIndex=0
          self.animateAttack = True
          self.animateAttackTimer = 0
            
        if not self.alwaysMove:
          #self.animation.rangedAttack(self.directionString)#######
          pass
    
    #update turnTime
    if self.turning:
      #self.animation.setAnimation(self.directionString)###pass
      self.turnTimer += time
      
    if self.currentAnimation != oldAnimation and not self.animateAttack: #only change if not the same and not animating an attack
      self.animationPlayer.currentFrameIndex=0 #removes any index errors
      self.animationPlayer.animation = glad.resource.resourceDict[self.currentAnimation]
    #Animate only if moving - code farther below was a little sloppy
    if not self.alwaysMove:
      if self.vel[0] != 0 or self.vel[1] != 0: #ADD SOMETHING HERE TO UPDATE ANIMATION WHILE ATTACKING
        if self.animationPlayer:
          self.animationPlayer.update(time)
    else:
      if self.animationPlayer:
         self.animationPlayer.update(time)
    
    ################This chunk does nothing now, but helped animate before############################    
    #animate only if moving and not shooting
    if not self.alwaysMove:
      if self.vel[0] != 0 or self.vel[1] != 0:
        if self.attacking and not self.shooting:
          #self.animation.setAnimation(self.directionString)####
          pass
          #if self.animation:####
            #self.animation.update(time)####
        if not self.attacking and not self.shooting:
          #self.animation.setAnimation(self.directionString)####
          pass
          #if self.animation:
           # self.animation.update(time)
    else:
      #if self.animation:
       # self.animation.update(time)
       pass
   #############################################################################################
    
    #Turn off attacking unless its called in the next loop      
    self.attacking = False

class BasicProjectile(AbstractObject):
  def __init__(self, pos, shape, team, moveDir, name='TEST', spin=False, slime=False, **kwargs): #can probably get rid of spin and slime and use **kwargs, but not how
    
    AbstractObject.__init__(self, pos, shape, team, moveDir, **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    
    self.orientation = Vector(moveDir)
    self.directionString = self.orientationToString()
    
    self.name=name
    if self.name == 'TEST':
        anim = animation.TestAnimation(size = shape.getSize())
        self.animationPlayer = animation.AnimationPlayer(anim, 1.0, True)
    else:
        if spin:
            self.currentAnimation = 'ANIM_' + self.name + '_SPIN'
        elif slime:
            self.currentAnimation = 'ANIM_' + self.name
        else:
            self.currentAnimation = 'ANIM_' + self.name +'_MOVE' + self.orientationToString()
        self.animationPlayer = animation.AnimationPlayer(glad.resource.resourceDict[self.currentAnimation], 0.2, True) #freezes if false
  
class Meteor(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, name='METEOR', **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    
    self.animationPlayer.colorCycle=True
    self.animationPlayer.color = 'ORANGE'
    #self.animation = animation.AnimateRangedAttack('meteor', self.directionString)
    #self.animationPlayer = animation.AnimationPlayer(glad.resource.resourceDict[self.currentAnimation], 0.2, True)

class Bone(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, name='BONE', spin=True, **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    

    #self.animation = animation.AnimateSpinningAttack('bone1', self.directionString)
    
class SlimeBall(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, hue=0, **kwargs): #hue was used to colorize
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, name='SLIME_BALL', slime=True, **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 100.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    
    self.hue = hue

    #self.animation = animation.AnimateSlimeBall('sl_ball', self.directionString, self.hue, frames = 12)
    
class Knife(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, name='KNIFE', spin=True, **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    

    #self.animation = animation.AnimateSpinningAttack('knife', self.directionString)
 
class Boulder(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, name='BOULDER', spin=True, **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    

    #self.animation = animation.AnimateSpinningAttack('boulder1', self.directionString, frames = 1)   

class Rock(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, name='ROCK', **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    

    #self.animation = animation.AnimateRangedAttack('rock', self.directionString, frames = 12)    

class Hammer(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, name='HAMMER', **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    

    #self.animation = animation.AnimateRangedAttack('hammer', self.directionString, frames = 12)

class Sparkle(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, name='SPARKLE', spin=True, **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    

    #self.animation = animation.AnimateSpinningAttack('sparkle', self.directionString, frames = 12)

class Lightning(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, name='LIGHTNING', **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    

    #self.animation = animation.AnimateRangedAttack('lightnin', self.directionString)

class Fireball(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, name='FIREBALL', **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    
    self.animationPlayer.colorCycle=True
    self.animationPlayer.color = 'BLUE'
    #self.animation = animation.AnimateRangedAttack('fire', self.directionString)
    
class Arrow(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, name='ARROW', **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    

    #self.animation = animation.AnimateRangedAttack('arrow', self.directionString, frames = 12)

class FireArrow(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, name='FIRE_ARROW', **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    

    #self.animation = animation.AnimateRangedAttack('farrow', self.directionString, frames = 16)


class BasicRangedAttack(object):
  
  def __init__(self, type='meteor', size=(16,16)):
    
    self.nextAttackTimer = 0.0
    self.attackCooldown = 0.4
    
    self.size = size
    
    self.type = type
    
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
    
    dict = {'rock': Rock(projectilePos,projectileShape,team,orientation),
            'arrow': Arrow(projectilePos,projectileShape,team,orientation),
            'firearrow': FireArrow(projectilePos,projectileShape,team,orientation),
            'fireball': Fireball(projectilePos,projectileShape,team,orientation),
            'hammer': Hammer(projectilePos,projectileShape,team,orientation),
            'lightning': Lightning(projectilePos,projectileShape,team,orientation),
            'meteor': Meteor(projectilePos,projectileShape,team,orientation),
            'bone' : Bone(projectilePos,projectileShape,team,orientation),
            'knife' : Knife(projectilePos,projectileShape,team,orientation),
            'sparkle' : Sparkle(projectilePos,projectileShape,team,orientation),
            'boulder' : Boulder(projectilePos,projectileShape,team,orientation)}
    proj = dict[self.type]
    
    #proj = BasicProjectile(projectilePos, projectileShape, team, orientation) #basic projectile should be default
    #proj = Fireball(projectilePos,projectileShape,team,orientation)
    ##proj = Knife(projectilePos,projectileShape,team,orientation) 
    
    glad.world.objectList.append(proj)
    
    return True
  
class SlimeAttack(BasicRangedAttack):
  
  def __init__(self, hue, size=(24, 24), type=None):
    BasicRangedAttack.__init__(self, type, size=(24,24))
    self.hue = hue
    
  def attack(self, pos, gap, orientation,team):
    
    if self.nextAttackTimer != 0.0:
      return False
    
    self.nextAttackTimer += self.attackCooldown
    
    #create a knife just outside the spawn location
    
    projectileShape = Rect.createAtOrigin(self.size[0], self.size[1])
        
    #TODO: how to handle diagonal movement and firing?
    # spawn outside rect, or inside?
    
    projectilePos = pos + orientation.getNormalized()*gap
    
    proj = SlimeBall(projectilePos,projectileShape,team,orientation,self.hue)
    #proj = Rock(projectilePos,projectileShape,team,orientation) 
    
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
      
    BasicUnit.__init__(self, pos, shape, name='SOLDIER', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('knife',size=(12,12)) #changed knife to meteor
    
    #self.animation = animation.AnimateUnit('footman', self.directionString)
    #self.currentAnimation = 'ANIM_SOLDIER_MOVE'+self.orientationToString()
    #self.animationPlayer = animation.AnimationPlayer(glad.resource.resourceDict[self.currentAnimation], 0.2, True)
    
class FireElem(BasicUnit):
  #based off sample soldier for the start
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 32)
        
    BasicUnit.__init__(self, pos, shape, name='FIRE_ELEM', **kwargs)
        
    #self.rangedWeapon = KnifeThrower()
    self.rangedWeapon = BasicRangedAttack('meteor')
        
    #self.animation = animation.AnimateUnit('firelem', self.directionString, self.hue)
    self.alwaysMove = True
    
    self.animationPlayer.colorCycle=True
    self.animationPlayer.color = 'ORANGE'
   
class Archer(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 32)
    
    BasicUnit.__init__(self, pos, shape, name='ARCHER', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('arrow', size=(14,14))
    
    #self.animation = animation.AnimateUnit('archer', self.directionString)
    
class Archmage(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 28)
    
    BasicUnit.__init__(self, pos, shape, name='ARCHMAGE', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('fireball')
    
    self.animationPlayer.colorCycle=True
    self.animationPlayer.color = 'ORANGE'
    #self.animation = animation.AnimateMage('archmage', self.directionString)

class Barbarian(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 28)
    
    BasicUnit.__init__(self, pos, shape, name='BARBARIAN', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('hammer', size=(12,12))
    
    #self.animation = animation.AnimateUnit('barby', self.directionString)
    
class Cleric(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 24)
    
    BasicUnit.__init__(self, pos, shape, name='CLERIC', **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    #self.animation = animation.AnimateUnit('cleric', self.directionString)
    
class Druid(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 22)
    
    BasicUnit.__init__(self, pos, shape, name='DRUID', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('lightning')
    
    #self.animation = animation.AnimateUnit('druid', self.directionString)
    
class Elf(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(20, 20)
    
    BasicUnit.__init__(self, pos, shape, name='ELF', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('rock',size=(12,12))
    
    #self.animation = animation.AnimateUnit('elf', self.directionString)
    
class Faerie(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(16, 16)
    
    BasicUnit.__init__(self, pos, shape, name='FAERIE', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('sparkle')
    
    #self.animation = animation.AnimateUnit('faerie', self.directionString)
    self.alwaysMove = True
    
class Ghost(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(26, 28)
    
    BasicUnit.__init__(self, pos, shape, name='GHOST', **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    #self.animation = animation.AnimateUnit('ghost', self.directionString)
    self.alwaysMove = True
    
class Golem(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(96, 72)
    
    BasicUnit.__init__(self, pos, shape, name='GOLEM', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('boulder', size=(26,26))
    
    #self.animation = animation.AnimateUnit('golem', self.directionString)
    
class Mage(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 28)
    
    BasicUnit.__init__(self, pos, shape, name='MAGE', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('fireball')
    
    #self.animation = animation.AnimateMage('mage', self.directionString) 

class Orc(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 32)
    
    BasicUnit.__init__(self, pos, shape, name='ORC', **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    #self.animation = animation.AnimateUnit('orc', self.directionString) 
    
class OrcCaptain(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 32)
    
    BasicUnit.__init__(self, pos, shape, name='ORC_CAPTAIN', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('knife', size=(12,12))
    
    #self.animation = animation.AnimateUnit('orc2', self.directionString) 
    
class Skeleton(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(30, 26)
    
    BasicUnit.__init__(self, pos, shape, name='SKELETON', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('bone', size=(14,14))
    
    #self.animation = animation.AnimateUnit('skeleton', self.directionString) 
    
class SmallSlime(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(24, 24)
    
    BasicUnit.__init__(self, pos, shape, name='SMALL_SLIME', slime=True, **kwargs)
    
    self.rangedWeapon = SlimeAttack(self.hue)
    
    self.alwaysMove = True
    
    #self.animation = animation.AnimateSmallSlime('s_slime')

class MediumSlime(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(40, 40)
    
    BasicUnit.__init__(self, pos, shape, name='MEDIUM_SLIME', slime=True, **kwargs)
    
    self.rangedWeapon = SlimeAttack(self.hue)
    
    self.alwaysMove = True
    
    #self.animation = animation.AnimateMediumSlime('m_slime')
    
class BigSlime(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(64, 64)
    
    BasicUnit.__init__(self, pos, shape, name='BIG_SLIME', slime=True, **kwargs)
    
    self.rangedWeapon = SlimeAttack(self.hue)
    
    self.alwaysMove = True
    
    #self.animation = animation.AnimateBigSlime('b_slime')
    
class Thief(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 26)
    
    BasicUnit.__init__(self, pos, shape, name='THIEF', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('knife', size=(12,12))
    
    #self.animation = animation.AnimateUnit('thief', self.directionString)     
    
