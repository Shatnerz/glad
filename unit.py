import glad
import animation
import util

from util import Rect, Vector

from object import AbstractObject
from projectile import *
  

class Corpse(AbstractObject):
  
  def __init__(self, pos, owner, **kwargs):
    shape = Rect.createAtOrigin(32, 32)
    AbstractObject.__init__(self, pos, shape, **kwargs)
    
    self.owner = self #keep a copy of who the corpse belongs to
    
    self.collisionType = 'OBJ' #should add collision type for corpses, keys, and other stuff you can walk over
    
    self.currentAnimation = 'ANIM_BLOOD_'+str(random.randint(0,3))
    self.animationPlayer = animation.AnimationPlayer(glad.resource.resourceDict[self.currentAnimation], 0.2, True)
    
    
class BasicUnit(AbstractObject):
  
  def __init__(self, pos, shape = Rect.createAtOrigin(32, 32), hue=180, name='SOLDIER', slime=False, **kwargs):
    AbstractObject.__init__(self, pos, shape, **kwargs)
    
    self.collisionType = 'UNIT'
  
    #Default statistics  
    self.strength = 10
    self.dexterity = 10
    self.constitution = 10
    self.intelligence = 10
    self.armor = 10    
    self.level = 1
    
    self.life = 100
    self.mana = 100
    
    self.rangedWeapon = None
    self.meleeWeapon = None
    
    self.rangedDamage = 10
    self.meleeDamage = 10
    
    self.range = 400 #range for ranged weapon (in pixels)
    
    self.moveSpeed = 200
    
    #By default, have units face 'right'
    self.orientation = Vector(1,0)
    self.directionString = self.orientationToString() #may not be needed
    
    #self.name = "SOLDIER" #might as well be soldier by default, name used to load animations with current name format
    self.name=name
    self.slime=slime
    if self.slime:
        self.currentAnimation = 'ANIM_' + self.name + '_TEAM_' + str(self.team) +'_MOVE'
    else:
        self.currentAnimation = 'ANIM_' + self.name + '_TEAM_' + str(self.team) +'_MOVE' + self.orientationToString()
    
    self.animationTime = 0.2    
    self.animationPlayer = animation.AnimationPlayer(glad.resource.resourceDict[self.currentAnimation], self.animationTime , True)
    
    self.alwaysMove = False
    
    #turning
    self.turnTime = 0.08
    
    #Attacking
    self.attacking = False
    #attack animation
    self.attackTime = 0.1 #time attack frame is up
    self.attackTimer = 0
    self.animateAttack = False
    
    self.hue = hue #I thnk this is from my old method of team coloring - can probably be removed

    
  def attack(self):
    self.attacking = True
    
  def meleeAttack(self, target):
    print 'Melee'
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
      #subtract mana points - just for testing now
      self.mana -= 5
      return True
      #self.animation.rangedAttack(self.directionString)
    else:
      return False
    
  def rangedHit(self, target):
    target.life -= self.rangedDamage
    #update stats here
    print target, ' Remaning life: ', target.life
    
  def die(self):
    """Kill unit and handle his death"""
    self.alive = False
    glad.resource.resourceDict['die1'].play(self.pos) #just testing sound out again
    corpse = Corpse(self.pos, self)
    glad.world.objectList.append(corpse)
  
  def update(self, time):
    #update everything needed for a basic unit, sloppy at the moment
    if self.life <= 0:
      self.die() 
    
    if self.rangedWeapon:
      self.rangedWeapon.update(time)
      
    #update turnTime
    if self.turning:
      self.turnTimer += time
      
    oldAnimation = self.currentAnimation
    
    self.directionString = self.orientationToString()   
    
    #update current animation
    if self.slime:
      self.currentAnimation = 'ANIM_' + self.name + '_TEAM_' + str(self.team) +'_MOVE'
    else:
      self.currentAnimation = 'ANIM_' + self.name + '_TEAM_' + str(self.team) +'_MOVE' + self.directionString
      
    if self.attacking:
      #Check if melee or ranged
      #Just assume ranged for now
      if self.rangedAttack(): #fires if ready
        if not self.alwaysMove:
          #dont animate attacking for firelems etc. doesnt look smooth
          self.animateAttack = True
      
    if self.animateAttack:
      self.currentAnimation = 'ANIM_' + self.name + '_TEAM_' + str(self.team) +'_ATTACK' + self.directionString
      self.animationPlayer.timer = self.attackTime
      if self.animationPlayer.currentFrameIndex == 1: #Stop after reaching last frame
        self.animateAttack=False
        self.animationPlayer.timer = self.animationTime   
    
    if self.currentAnimation != oldAnimation: #only change if not the same
      self.animationPlayer.currentFrameIndex=0 #removes any index errors
      self.animationPlayer.animation = glad.resource.resourceDict[self.currentAnimation]
      
    #Animate only if moving or animating attack
    if self.alwaysMove or self.animateAttack:
      if self.animationPlayer:
        self.animationPlayer.update(time)
    elif not self.alwaysMove:
      if self.vel[0] != 0 or self.vel[1] != 0:
        if self.animationPlayer:
          self.animationPlayer.update(time)
    
    #Turn off attacking    
    self.attacking = False
  
    
class Soldier(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    #For now, just use BasicUnit Defaults
    
    #default soldier size    
    shape = Rect.createAtOrigin(32, 32)
      
    BasicUnit.__init__(self, pos, shape, name='SOLDIER', **kwargs)
    
    #self.rangedWeapon = BasicRangedAttack('knife',size=(12,12))
    self.rangedWeapon = KnifeThrower(self)
        
class FireElem(BasicUnit):
  #based off sample soldier for the start
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 32)
        
    BasicUnit.__init__(self, pos, shape, name='FIRE_ELEM', **kwargs)
        
    #self.rangedWeapon = KnifeThrower()
    self.rangedWeapon = BasicRangedAttack(self, 'meteor')
        
    self.alwaysMove = True
    
    self.animationPlayer.timer = 0.1
   
class Archer(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 32)
    
    BasicUnit.__init__(self, pos, shape, name='ARCHER', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack(self, 'arrow', size=(14,14))
      
class Archmage(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 28)
    
    BasicUnit.__init__(self, pos, shape, name='ARCHMAGE', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack(self, 'fireball')
    
class Barbarian(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 28)
    
    BasicUnit.__init__(self, pos, shape, name='BARBARIAN', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack(self, 'hammer', size=(12,12))
        
class Cleric(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 24)
    
    BasicUnit.__init__(self, pos, shape, name='CLERIC', **kwargs)
    
    self.rangedWeapon = KnifeThrower(self)
       
class Druid(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 22)
    
    BasicUnit.__init__(self, pos, shape, name='DRUID', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack(self, 'lightning')
       
class Elf(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(20, 20)
    
    BasicUnit.__init__(self, pos, shape, name='ELF', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack(self, 'rock',size=(12,12))
       
class Faerie(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(16, 16)
    
    BasicUnit.__init__(self, pos, shape, name='FAERIE', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack(self, 'sparkle')
    
    self.alwaysMove = True
    
class Ghost(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(26, 28)
    
    BasicUnit.__init__(self, pos, shape, name='GHOST', **kwargs)
    
    self.rangedWeapon = KnifeThrower(self)
    
    self.alwaysMove = True
    
class Golem(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(96, 72)
    
    BasicUnit.__init__(self, pos, shape, name='GOLEM', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack(self, 'boulder', size=(26,26))
       
class Mage(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 28)
    
    BasicUnit.__init__(self, pos, shape, name='MAGE', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack(self, 'fireball')
    
class Orc(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 32)
    
    BasicUnit.__init__(self, pos, shape, name='ORC', **kwargs)
    
    self.rangedWeapon = KnifeThrower(self)
        
class OrcCaptain(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 32)
    
    BasicUnit.__init__(self, pos, shape, name='ORC_CAPTAIN', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack(self, 'knife', size=(12,12))
        
class Skeleton(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(30, 26)
    
    BasicUnit.__init__(self, pos, shape, name='SKELETON', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack(self, 'bone', size=(14,14))
       
class SmallSlime(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(24, 24)
    
    BasicUnit.__init__(self, pos, shape, name='SMALL_SLIME', slime=True, **kwargs)
    
    self.rangedWeapon = SlimeAttack(self)
    
    self.alwaysMove = True
    
class MediumSlime(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(40, 40)
    
    BasicUnit.__init__(self, pos, shape, name='MEDIUM_SLIME', slime=True, **kwargs)
    
    self.rangedWeapon = SlimeAttack(self)
    
    self.alwaysMove = True
       
class BigSlime(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(64, 64)
    
    BasicUnit.__init__(self, pos, shape, name='BIG_SLIME', slime=True, **kwargs)
    
    self.rangedWeapon = SlimeAttack(self)
    
    self.alwaysMove = True
       
class Thief(BasicUnit):
  
  def __init__(self, pos, **kwargs):
    shape = Rect.createAtOrigin(32, 26)
    
    BasicUnit.__init__(self, pos, shape, name='THIEF', **kwargs)
    
    self.rangedWeapon = BasicRangedAttack(self, 'knife', size=(12,12))
       
    
    
