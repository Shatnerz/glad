from object import AbstractObject
from util import Rect, Vector
import random #for firing variation
import animation
import glad
import util

class BasicProjectile(AbstractObject):
  def __init__(self, pos, shape, owner, moveDir, name='TEST', spin=False, speed=400, slime=False, **kwargs): #can probably get rid of spin and slime and use **kwargs, but not sure how
    
    AbstractObject.__init__(self, pos, shape, owner.team, moveDir, **kwargs)
    
    self.collisionType = 'PROJECTILE'
    
    self.owner = owner
    
    self.speed = speed
    
    self.damage = 25
    
    #NOTE: must use normalized direction vector!
    self.vel = moveDir.getNormalized()*self.speed
    
    self.orientation = Vector(moveDir)
    self.directionString = self.orientationToString()
    
    self.range = self.owner.range #arbitrary range in pixels for now, not in src they do line of sight * step size
    self.distance = 0 #distance traveled
    
    #Setup random waver for the projectile
    waver = self.speed/2 #absolute amount
    #waver = random.uniform(0,(waver)) - waver/2 #similar to openglad code
    gauss = random.gauss(0,0.25) #have a gaussian distribution just because i can
    if gauss > 1: gauss=1
    elif gauss < -1: gauss=-1
    waver = waver * gauss    
    #get vector perpendicular to direction 
    normVector = Vector(-1*self.vel[1],self.vel[0]).getNormalized() #the negative reciprocal of direction vector
    #Create vector for the waver
    waverVector = normVector*waver    
    #Add waver to velocity vector
    self.vel += waverVector
    
    self.sound = glad.resource.resourceDict['fwip']
    
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
      
  def update(self,time):
    #Update as abstract object
    AbstractObject.update(self,time)
    
    #Update distance traveled
    self.distance += self.vel.getNorm()*time
    
    #Check to see if it hit max range yet
    if self.distance >= self.range:
      self.alive = False
  
  def onCollide(self, enemy):
    #should only happen with units, but may want to chec if unit
    #enemy.life -= self.damage
    self.owner.rangedHit(enemy)
    self.alive = False
    #print enemy.life

class BasicRangedAttack(object):
  
  def __init__(self, owner, type='meteor', size=(16,16)):
    
    self.owner = owner
    
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
    
    dict = {'rock': Rock(projectilePos,projectileShape,self.owner,orientation),
            'arrow': Arrow(projectilePos,projectileShape,self.owner,orientation),
            'firearrow': FireArrow(projectilePos,projectileShape,self.owner,orientation),
            'fireball': Fireball(projectilePos,projectileShape,self.owner,orientation),
            'hammer': Hammer(projectilePos,projectileShape,self.owner,orientation),
            'lightning': Lightning(projectilePos,projectileShape,self.owner,orientation),
            'meteor': Meteor(projectilePos,projectileShape,self.owner,orientation),
            'bone' : Bone(projectilePos,projectileShape,self.owner,orientation),
            'knife' : Knife(projectilePos,projectileShape,self.owner,orientation),
            'sparkle' : Sparkle(projectilePos,projectileShape,self.owner,orientation),
            'boulder' : Boulder(projectilePos,projectileShape,self.owner,orientation)}
    proj = dict[self.type]
    proj.owner = self.owner
    
    
    #play sound - if I do this when the projectile is created, it plays it for each entry in the above dict
    #need to play sound for each attack, right now just this, knifeThrower, and slimeAttack
    proj.sound.play(self.owner.pos)
    #if self.type == "arrow":
    #  glad.resource.resourceDict['twang'].play(self.owner.pos)
    #elif self.type == "sparkle":
    #  glad.resource.resourceDict['faerie1'].play(self.owner.pos)
    #elif self.type == "lightning":
    #  glad.resource.resourceDict['bolt1'].play(self.owner.pos)
    #elif self.type == "meteor":
    #  glad.resource.resourceDict['blast1'].play(self.owner.pos)
    #else:
    #  glad.resource.resourceDict['fwip'].play(self.owner.pos) #Just testing sound, should be for only stuff on screen or nearby,
    
    #proj = BasicProjectile(projectilePos, projectileShape, team, orientation) #basic projectile should be default
    #proj = Fireball(projectilePos,projectileShape,team,orientation)
    ##proj = Knife(projectilePos,projectileShape,team,orientation) 
    
    glad.world.objectList.append(proj)
    
    return True
  
class SlimeAttack(BasicRangedAttack):
  
  def __init__(self, owner, size=(24, 24), type=None):
    BasicRangedAttack.__init__(self, owner, type, size=(24,24))
    self.hue = owner.hue
    
  def attack(self, pos, gap, orientation,team):
    
    if self.nextAttackTimer != 0.0:
      return False
    
    self.nextAttackTimer += self.attackCooldown
    
    #create a knife just outside the spawn location
    
    projectileShape = Rect.createAtOrigin(self.size[0], self.size[1])
        
    #TODO: how to handle diagonal movement and firing?
    # spawn outside rect, or inside?
    
    projectilePos = pos + orientation.getNormalized()*gap
    
    proj = SlimeBall(projectilePos,projectileShape,self.owner,orientation,self.hue)
    #proj = Rock(projectilePos,projectileShape,team,orientation) 
    
    glad.world.objectList.append(proj)
    
    #play sound effect
    proj.sound.play(self.owner.pos)
    
    return True  
  
class KnifeThrower(BasicRangedAttack):
  """Spawns knives"""
  
  def __init__(self, owner, maxKnives = 3):
    
    BasicRangedAttack.__init__(self, owner, 'knife')
    
    #temporary defaults for now    
    self.maxKnives = maxKnives
    self.knivesAvailable = self.maxKnives
    
    #self.nextAttackTimer = 0.0
    #self.attackCooldown = 0.4
    
    self.knives = [] #list of knives
    
    #self.owner = owner
    
  def update(self, time):
    
    self.nextAttackTimer -= time
    
    if self.nextAttackTimer < 0.0:
      self.nextAttackTimer = 0.0   
  
    #Check on knives
    for knife in self.knives:
      if knife.alive == False:
        self.knivesAvailable += 1
    #Remove all "dead" knives
    self.knives = [x for x in self.knives if x.alive]
    
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
        
    #proj = BasicProjectile(knifePos,knifeShape,team,orientation)
    proj = MagicKnife(knifePos,knifeShape,self.owner,orientation)
    proj.owner = self.owner #Set owner so it can return and keep track of unit
    
    self.knives.append(proj)
    
    glad.world.objectList.append(proj)
    
    #play sound effect
    proj.sound.play(self.owner.pos)
    
    return True
#   TODO: spawn knife here
    
  
class Meteor(BasicProjectile):
  def __init__(self, pos, shape, owner, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, owner, moveDir, name='METEOR', **kwargs)
    self.sound = glad.resource.resourceDict['blast1']
    

class Bone(BasicProjectile):
  def __init__(self, pos, shape, owner, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, owner, moveDir, name='BONE', spin=True, **kwargs)
    
    
class SlimeBall(BasicProjectile):
  def __init__(self, pos, shape, owner, moveDir, hue=0, **kwargs): #hue was used to colorize
    
    self.speed=75
    
    BasicProjectile.__init__(self, pos, shape, owner, moveDir, name='SLIME_BALL_TEAM_'+str(owner.team), slime=True, speed=self.speed, **kwargs)
    
    self.hue = hue #does this do anything anymore?

    
class Knife(BasicProjectile):
  def __init__(self, pos, shape, owner, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, owner, moveDir, name='KNIFE', spin=True, **kwargs)
    
    
class MagicKnife(Knife):
  """Knife that returns to owner"""
  def __init__(self, pos, shape, owner, moveDir, **kwargs):
    Knife.__init__(self, pos, shape, owner, moveDir)
    
    self.returning = False
    self.owner = None
    
    self.damage=1
    
    self.alreadyHit = []
    #glad.resource.resourceDict['fwip'].play()
    
  def update(self, time):
    #Update as abstract object
    AbstractObject.update(self,time)
    
    if not self.owner.alive:
      self.alive = False
    
    if not self.returning:
      #Update distance traveled
      self.distance += self.vel.getNorm()*time    
      #Check to see if it hit max range yet
      if self.distance >= self.range:
        self.returning = True
    
    elif self.returning: #returns along straight line between knife and owner
      direction = self.pos - self.owner.pos
      direction = direction.getNormalized()
      self.vel = direction*self.speed
      
      #if util.getCollisionInfo(self.shape.translate(self.getPos()), self.vel, self.owner.shape.translate(self.owner.getPos()), self.owner.vel):
      #  time = util.getCollisionInfo(self.shape.translate(self.getPos()), self.vel, self.owner.shape.translate(self.owner.getPos()), self.owner.vel)[0]
      #  print time  
      
      #CHECK FOR COLLISION WITH OWNER
      #cant use onCollide because collision between unit and projectile of the same team are ignored
      if util.Rect.touches(self.shape.translate(self.getPos()), self.owner.shape.translate(self.owner.getPos())):
        #print "COLLISION"
        self.alive = False
      
  def onCollide(self, enemy):
    #collision should only happen on collision with enemy units
    self.returning = True
    #Make sure enemy is only hit once
    #Note - may want to take into account circumstance when knife can hit twice, like if soldier outruns knife and it hits twice
    applyDamage = True
    for hit in self.alreadyHit:
      if enemy==hit:
        applyDamage = False
    if applyDamage:
      self.alreadyHit.append(enemy)
      BasicProjectile.onCollide(self, enemy)
      self.alive = True
 
class Boulder(BasicProjectile):
  def __init__(self, pos, shape, owner, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, owner, moveDir, name='BOULDER', spin=True, **kwargs)
      

class Rock(BasicProjectile):
  def __init__(self, pos, shape, owner, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, owner, moveDir, name='ROCK', **kwargs)
      

class Hammer(BasicProjectile):
  def __init__(self, pos, shape, owner, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, owner, moveDir, name='HAMMER', **kwargs)
    

class Sparkle(BasicProjectile):
  def __init__(self, pos, shape, owner, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, owner, moveDir, name='SPARKLE', spin=True, **kwargs)
    self.sound = glad.resource.resourceDict['faerie1']

class Lightning(BasicProjectile):
  def __init__(self, pos, shape, owner, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, owner, moveDir, name='LIGHTNING_TEAM_'+str(owner.team), **kwargs)
    self.sound = glad.resource.resourceDict['bolt1']
    

class Fireball(BasicProjectile):
  def __init__(self, pos, shape, owner, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, owner, moveDir, name='FIREBALL', **kwargs)
    self.sound = glad.resource.resourceDict['blast1']
    
    
class Arrow(BasicProjectile):
  def __init__(self, pos, shape, owner, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, owner, moveDir, name='ARROW', **kwargs)
    self.sound = glad.resource.resourceDict['twang']
    

class FireArrow(BasicProjectile):
  def __init__(self, pos, shape, owner, moveDir, **kwargs):
    
    BasicProjectile.__init__(self, pos, shape, owner, moveDir, name='FIRE_ARROW', **kwargs)
    self.sound = glad.resource.resourceDict['twang']
    
