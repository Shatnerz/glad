from object import AbstractObject
from util import Rect, Vector
import glad
import animation

class Tile(AbstractObject):
  
  tileDict = {0: 'PIX_H_WALL1',
              1: 'PIX_GRASS1',
              2: 'PIX_WATER1',
              3: 'PIX_VOID1',
              4: 'PIX_WALL2',
              5: 'PIX_WALL3',
              6: 'PIX_FLOOR1',
              7: 'PIX_WALL4',
              8: 'PIX_WALL5',
              9: 'PIX_CARPET_LL',
              10: 'PIX_CARPET_L',
              11: 'PIX_CARPET_B',
              12: 'PIX_CARPET_LR',
              13: 'PIX_CARPET_UR',
              14: 'PIX_CARPET_U',
              15: 'PIX_CARPET_UL',
              16: 'PIX_GRASS2',
              17: 'PIX_GRASS3',
              18: 'PIX_GRASS4',
              19: 'PIX_WATER2',
              20: 'PIX_WATER3',
              21: 'PIX_PAVEMENT1',
              22: 'PIX_WALLSIDE1',
              23: 'PIX_WALLSIDE_L',
              24:   'PIX_WALLSIDE_R',
              25: 'PIX_WALLSIDE_C',
              26: 'PIX_WALL_LL',
              27: 'PIX_PAVESTEPS1',
              28: 'PIX_BRAZIER1',
              29: 'PIX_WATERGRASS_LL',
              30: 'PIX_WATERGRASS_LR',
              31: 'PIX_WATERGRASS_UL',
              32: 'PIX_WATERGRASS_UR',
              33: 'PIX_CARPET_M',
              34: 'PIX_CARPET_M2',
              35: 'PIX_PAVESTEPS2',
              36: 'PIX_PAVESTEPS2L',
              37: 'PIX_PAVESTEPS2R',
              38: 'PIX_WALLTOP_H',
              39: 'PIX_TORCH1',
              40: 'PIX_TORCH2',
              41: 'PIX_TORCH3',
              42: 'PIX_CARPET_R',
              43: 'PIX_FLOOR_PAVEL',
              44: 'PIX_FLOOR_PAVER',
              45: 'PIX_FLOOR_PAVEU',
              46: 'PIX_FLOOR_PAVED',
              47: 'PIX_GRASSWATER_LL',
              48: 'PIX_GRASSWATER_LR',
              49: 'PIX_GRASSWATER_UL',
              50: 'PIX_GRASSWATER_UR',
              51: 'PIX_PAVEMENT2',
              52: 'PIX_PAVEMENT3',
              53: 'PIX_COLUMN1',
              54: 'PIX_COLUMN2',
              55: 'PIX_TREE_B1',
              56: 'PIX_TREE_M1',
              57: 'PIX_TREE_T1',
              58: 'PIX_TREE_ML',
              59: 'PIX_DIRT_1',
              60: 'PIX_DIRTGRASS_UL1',
              61: 'PIX_DIRTGRASS_UR1',
              62: 'PIX_DIRTGRASS_LL1',
              63: 'PIX_DIRTGRASS_LR1',
              64: 'PIX_PATH_1',
              65: 'PIX_PATH_2',
              66: 'PIX_PATH_3',
              67: 'PIX_BOULDER_1',
              68: 'PIX_WATERGRASS_U',
              69: 'PIX_WATERGRASS_L',
              70: 'PIX_WATERGRASS_R',
              71: 'PIX_WATERGRASS_D',
              72: 'PIX_COBBLE_1',
              73: 'PIX_COBBLE_2',
              74: 'PIX_PATH_4',
              75: 'PIX_COBBLE_3',
              76: 'PIX_COBBLE_4',
              77: 'PIX_WALL_ARROW_GRASS',
              78: 'PIX_WALL_ARROW_FLOOR',
              79: 'PIX_GRASS1_DAMAGED',
              80: 'PIX_TREE_MR',
              81: 'PIX_TREE_MT',
              82: 'PIX_GRASS_DARK_1',
              83: 'PIX_GRASS_DARK_LL',
              84: 'PIX_GRASS_DARK_UR',
              85: 'PIX_GRASS_RUBBLE',
              86: 'PIX_GRASS_DARK_2',
              87: 'PIX_GRASS_DARK_3',
              88: 'PIX_GRASS_DARK_4',
              89: 'PIX_BOULDER_2',
              90: 'PIX_BOULDER_3',
              91: 'PIX_BOULDER_4',
              92: 'PIX_GRASS_DARK_B1',
              93: 'PIX_GRASS_DARK_B2',
              94: 'PIX_GRASS_DARK_BR',
              95: 'PIX_GRASS_DARK_R1',
              96: 'PIX_GRASS_DARK_R2',
              97: 'PIX_WALL_ARROW_GRASS_DARK',
              98: 'PIX_DIRTGRASS_DARK_UL1',
              99: 'PIX_DIRTGRASS_DARK_UR1',
              100: 'PIX_DIRTGRASS_DARK_LL1',
              101: 'PIX_DIRTGRASS_DARK_LR1',
              102: 'PIX_WALLSIDE_CRACK_C1',
              103: 'PIX_DIRT_DARK_1',
              104: 'PIX_GRASS_LIGHT_1',
              105: 'PIX_GRASS_LIGHT_TOP',
              106: 'PIX_GRASS_LIGHT_RIGHT_TOP',
              107: 'PIX_GRASS_LIGHT_RIGHT',
              108: 'PIX_GRASS_LIGHT_RIGHT_BOTTOM',
              109: 'PIX_GRASS_LIGHT_BOTTOM',
              110: 'PIX_GRASS_LIGHT_LEFT_BOTTOM',
              111: 'PIX_GRASS_LIGHT_LEFT',
              112: 'PIX_GRASS_LIGHT_LEFT_TOP',
              113: 'PIX_CLIFF_BOTTOM',
              114: 'PIX_CLIFF_TOP',
              115: 'PIX_CLIFF_LEFT',
              116: 'PIX_CLIFF_RIGHT',
              117: 'PIX_CLIFF_BACK_1',
              118: 'PIX_CLIFF_BACK_2',
              119: 'PIX_CLIFF_BACK_L',
              120: 'PIX_CLIFF_BACK_R',
              121: 'PIX_CLIFF_TOP_L',
              122: 'PIX_CLIFF_TOP_R',
              123: 'PIX_JAGGED_GROUND_1',
              124: 'PIX_JAGGED_GROUND_2',
              125: 'PIX_JAGGED_GROUND_3',
              126: 'PIX_JAGGED_GROUND_4',
              127: 'PIX_CARPET_SMALL_HOR',
              128: 'PIX_CARPET_SMALL_VER',
              129: 'PIX_CARPET_SMALL_CUP',
              130: 'PIX_CARPET_SMALL_CAP',
              131: 'PIX_CARPET_SMALL_LEFT',
              132: 'PIX_CARPET_SMALL_RIGHT',
              133: 'PIX_CARPET_SMALL_TINY'}
  
  water = [2, 19, 20, 47, 48, 49, 50, 68, 69, 70, 71]#maybe include 29, 30, 31, 32
  tree = [55, 56, 57, 58, 80, 81]
  wall = [0]
  barrier = [] #boulders and stuff that can be shot over but not walked over
  
  def __init__(self, pos, tileNum, type = None, shape=Rect.createAtOrigin(32,32), **kwargs):
    
    AbstractObject.__init__(self, pos, shape, team=None, moveDir=None, **kwargs)
    
    self.collisionType = 'LAND'
    if tileNum in Tile.water:
      self.collisionType = 'WATER'
    elif tileNum in Tile.tree:
      self.collisionType = 'TREE'
    elif tileNum in Tile.wall:
      self.collisionType = 'WALL'
    elif tileNum in Tile.barrier:
      self.CollisionType = 'BARRIER'
    
    #set appropriate tile to be drawn
    self.tileNum = tileNum
    tileName = Tile.tileDict[self.tileNum]
    anim = [glad.resource.get(tileName)]
    self.currentAnimation = animation.Animation(anim)
    self.animationPlayer = animation.AnimationPlayer(self.currentAnimation, 0.2, True)