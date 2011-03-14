
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
    #TODO: animaitons should be updated after collision detection
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
  
  def __init__(self, pos, shape, hue=180, **kwargs):
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
    
    self.hue = hue
    
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
    
    self.orientation = Vector(moveDir)
    self.directionString = self.orientationToString()
  
class Meteor(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    

    self.animation = animation.AnimateRangedAttack('meteor', self.directionString)

class Bone(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    

    self.animation = animation.AnimateSpinningAttack('bone1', self.directionString)
    
class SlimeBall(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, hue, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 100.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    
    self.hue = hue

    self.animation = animation.AnimateSlimeBall('sl_ball', self.directionString, self.hue, frames = 12)
    
class Knife(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    

    self.animation = animation.AnimateSpinningAttack('knife', self.directionString)
 
class Boulder(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    

    self.animation = animation.AnimateSpinningAttack('boulder1', self.directionString, frames = 1)   

class Rock(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    

    self.animation = animation.AnimateRangedAttack('rock', self.directionString, frames = 12)    

class Hammer(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    

    self.animation = animation.AnimateRangedAttack('hammer', self.directionString, frames = 12)

class Sparkle(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    

    self.animation = animation.AnimateSpinningAttack('sparkle', self.directionString, frames = 12)

class Lightning(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    

    self.animation = animation.AnimateRangedAttack('lightnin', self.directionString)

class Fireball(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    

    self.animation = animation.AnimateRangedAttack('fire', self.directionString)
    
class Arrow(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    

    self.animation = animation.AnimateRangedAttack('arrow', self.directionString, frames = 12)

class FireArrow(BasicProjectile):
  def __init__(self, pos, shape, team, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, team, moveDir, **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.speed = 450.0
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    

    self.animation = animation.AnimateRangedAttack('farrow', self.directionString, frames = 16)


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
    #proj = Rock(projectilePos,projectileShape,team,orientation) 
    
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
      
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('knife',size=(12,12))
    
    self.animation = animation.AnimateUnit('footman', self.directionString)
    
class FireElem(BasicUnit):
  #based off sample soldier for the start
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 32)
        
    BasicUnit.__init__(self, pos, shape, **kwargs)
        
    #self.rangedWeapon = KnifeThrower()
    self.rangedWeapon = BasicRangedAttack('meteor')
        
    self.animation = animation.AnimateUnit('firelem', self.directionString, self.hue)
    self.alwaysMove = True
   
class Archer(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 32)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('arrow', size=(14,14))
    
    self.animation = animation.AnimateUnit('archer', self.directionString)
    
class Archmage(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 28)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('fireball')
    
    self.animation = animation.AnimateMage('archmage', self.directionString)

class Barbarian(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 28)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('hammer', size=(12,12))
    
    self.animation = animation.AnimateUnit('barby', self.directionString)
    
class Cleric(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 24)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    self.animation = animation.AnimateUnit('cleric', self.directionString)
    
class Druid(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 22)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('lightning')
    
    self.animation = animation.AnimateUnit('druid', self.directionString)
    
class Elf(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(20, 20)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('rock',size=(12,12))
    
    self.animation = animation.AnimateUnit('elf', self.directionString)
    
class Faerie(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(16, 16)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('sparkle')
    
    self.animation = animation.AnimateUnit('faerie', self.directionString)
    self.alwaysMove = True
    
class Ghost(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(26, 28)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    self.animation = animation.AnimateUnit('ghost', self.directionString)
    self.alwaysMove = True
    
class Golem(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(96, 72)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('boulder', size=(26,26))
    
    self.animation = animation.AnimateUnit('golem', self.directionString)
    
class Mage(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 28)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('fireball')
    
    self.animation = animation.AnimateMage('mage', self.directionString) 

class Orc(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 32)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = KnifeThrower()
    
    self.animation = animation.AnimateUnit('orc', self.directionString) 
    
class OrcCaptain(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 32)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('knife', size=(12,12))
    
    self.animation = animation.AnimateUnit('orc2', self.directionString) 
    
class Skeleton(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(30, 26)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('bone', size=(14,14))
    
    self.animation = animation.AnimateUnit('skeleton', self.directionString) 
    
class SmallSlime(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(24, 24)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = SlimeAttack(self.hue)
    
    self.alwaysMove = True
    
    self.animation = animation.AnimateSmallSlime('s_slime')

class MediumSlime(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(40, 40)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = SlimeAttack(self.hue)
    
    self.alwaysMove = True
    
    self.animation = animation.AnimateMediumSlime('m_slime')
    
class BigSlime(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(64, 64)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = SlimeAttack(self.hue)
    
    self.alwaysMove = True
    
    self.animation = animation.AnimateBigSlime('b_slime')
    
class Thief(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 26)
    
    BasicUnit.__init__(self, pos, shape, **kwargs)
    
    self.rangedWeapon = BasicRangedAttack('knife', size=(12,12))
    
    self.animation = animation.AnimateUnit('thief', self.directionString)     
    
