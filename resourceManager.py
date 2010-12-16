
import os.path

import pygame

import glad


  
class AbstractResource(object):
  """Abstract class used to keep resource specific subclasses organized"""
  
  def __init__(self, filename, **kwargs):
    self.data = None
    self.kwargs = kwargs
    self.filename = filename
  
  def load(self):
    raise NotImplementedError()
  
  def get(self):
    assert self.data is not None    
    return self.data
  
class ImageResource(AbstractResource):
  """Handles images and converts them to pygame surfaces"""
  
  def load(self):
    
    kwargs = self.kwargs
    filename = self.filename
        
    w, h = kwargs['size']
    
    origSurface = pygame.image.load(filename) 
    
    
    
    
    #we have to get the subsurface because the first row is black pixels
    self.data = origSurface.subsurface(0,1,w,h)
    
    
class ResourceManager(object):
  """Keep track of all the images we need and whether or not they are
  loaded into memory"""
  
  def __init__(self):   
  
    self.resourceDict = {}
  
  def register(self, name, filename, **kwargs):
        
    #TODO assumes it's an image right now
    r = ImageResource(filename,**kwargs)    
    self.resourceDict[name] = r
    #TODO: for now just load immediately, this may change in the future
    r.load()
  
  def get(self, name):
    return self.resourceDict[name].get()
   
  

      
      
      
def registerGladResources():
  """Convenience function that loads all gladiator resources """
  
  registerGladTiles()
  
  registerGladCharacters()

def registerGladCharacters():
  """Load all the characters into the game"""
  
  #ANDREW, load what you need here 
      
def registerGladTiles():
  """This function loads all of the gladiator tiles"""
  #TODO: eventually have all resources here
  #TODO: in future, register automatically, not manually
  
  
  tileFolder = '/home/chris/glad/resources/images/' 
  
  tileSize = (32,32)
  
  tileDict = {'PIX_BOULDER_1': '16stone1.tga',
              'PIX_BOULDER_2': '16stone2.tga',
              'PIX_BOULDER_3': '16stone3.tga',
              'PIX_BOULDER_4': '16stone4.tga',
              'PIX_BRAZIER1': '16braz1.tga',
              'PIX_CARPET_B': '16carpb.tga',
              'PIX_CARPET_L': '16carpl.tga',
              'PIX_CARPET_LL': '16carpll.tga',
              'PIX_CARPET_LR': '16carplr.tga',
              'PIX_CARPET_M': '16carpm.tga',
              'PIX_CARPET_M2': '16carpm2.tga',
              'PIX_CARPET_R': '16carpr.tga',
              'PIX_CARPET_SMALL_CAP': '16cscap.tga',
              'PIX_CARPET_SMALL_CUP': '16cscup.tga',
              'PIX_CARPET_SMALL_HOR': '16cshor.tga',
              'PIX_CARPET_SMALL_LEFT': '16csleft.tga',
              'PIX_CARPET_SMALL_RIGHT': '16csrigh.tga',
              'PIX_CARPET_SMALL_TINY': '16cstiny.tga',
              'PIX_CARPET_SMALL_VER': '16csver.tga',
              'PIX_CARPET_U': '16carpu.tga',
              'PIX_CARPET_UL': '16carpul.tga',
              'PIX_CARPET_UR': '16carpur.tga',
              'PIX_CLIFF_BACK_1': '16clifup.tga',
              'PIX_CLIFF_BACK_2': '16clifu2.tga',
              'PIX_CLIFF_BACK_L': '16cliful.tga',
              'PIX_CLIFF_BACK_R': '16clifur.tga',
              'PIX_CLIFF_BOTTOM': '16cliff1.tga',
              'PIX_CLIFF_LEFT': '16cliff3.tga',
              'PIX_CLIFF_RIGHT': '16cliff4.tga',
              'PIX_CLIFF_TOP': '16cliff2.tga',
              'PIX_CLIFF_TOP_L': '16clifdl.tga',
              'PIX_CLIFF_TOP_R': '16clifdr.tga',
              'PIX_COBBLE_1': '16cob1.tga',
              'PIX_COBBLE_2': '16cob2.tga',
              'PIX_COBBLE_3': '16cob3.tga',
              'PIX_COBBLE_4': '16cob4.tga',
              'PIX_COLUMN1': '16colm0.tga',
              'PIX_COLUMN2': '16colm1.tga',
              'PIX_DIRTGRASS_DARK_LL1': '16dglld.tga',
              'PIX_DIRTGRASS_DARK_LR1': '16dglrd.tga',
              'PIX_DIRTGRASS_DARK_UL1': '16dguld.tga',
              'PIX_DIRTGRASS_DARK_UR1': '16dgurd.tga',
              'PIX_DIRTGRASS_LL1': '16dgll1.tga',
              'PIX_DIRTGRASS_LR1': '16dglr1.tga',
              'PIX_DIRTGRASS_UL1': '16dgul1.tga',
              'PIX_DIRTGRASS_UR1': '16dgur1.tga',
              'PIX_DIRT_1': '16dirt2.tga',
              'PIX_DIRT_DARK_1': '16dirtd1.tga',
              'PIX_FLOOR1': '16floor.tga',
              'PIX_FLOOR_PAVED': '16fpd.tga',
              'PIX_FLOOR_PAVEL': '16fpl.tga',
              'PIX_FLOOR_PAVER': '16fpr.tga',
              'PIX_FLOOR_PAVEU': '16fpu.tga',
              'PIX_GRASS1': '16grass1.tga',
              'PIX_GRASS1_DAMAGED': '16grasd1.tga',
              'PIX_GRASS2': '16grass2.tga',
              'PIX_GRASS3': '16grass3.tga',
              'PIX_GRASS4': '16grass4.tga',
              'PIX_GRASSWATER_LL': '16gwll.tga',
              'PIX_GRASSWATER_LR': '16gwlr.tga',
              'PIX_GRASSWATER_UL': '16gwul.tga',
              'PIX_GRASSWATER_UR': '16gwur.tga',
              'PIX_GRASS_DARK_1': '16grassd.tga',
              'PIX_GRASS_DARK_2': '16grd2.tga',
              'PIX_GRASS_DARK_3': '16grd3.tga',
              'PIX_GRASS_DARK_4': '16grd4.tga',
              'PIX_GRASS_DARK_B1': '16grdb1.tga',
              'PIX_GRASS_DARK_B2': '16grdb2.tga',
              'PIX_GRASS_DARK_BR': '16grdbr.tga',
              'PIX_GRASS_DARK_LL': '16grassi.tga',
              'PIX_GRASS_DARK_R1': '16grdr1.tga',
              'PIX_GRASS_DARK_R2': '16grdr2.tga',
              'PIX_GRASS_DARK_UR': '16grassh.tga',
              'PIX_GRASS_LIGHT_1': '16grl1.tga',
              'PIX_GRASS_LIGHT_BOTTOM': '16grlb.tga',
              'PIX_GRASS_LIGHT_LEFT': '16grll.tga',
              'PIX_GRASS_LIGHT_LEFT_BOTTOM': '16grllb.tga',
              'PIX_GRASS_LIGHT_LEFT_TOP': '16grllt.tga',
              'PIX_GRASS_LIGHT_RIGHT': '16grlr.tga',
              'PIX_GRASS_LIGHT_RIGHT_BOTTOM': '16grlrb.tga',
              'PIX_GRASS_LIGHT_RIGHT_TOP': '16grlrt.tga',
              'PIX_GRASS_LIGHT_TOP': '16grlt.tga',
              'PIX_GRASS_RUBBLE': '16grassr.tga',
              'PIX_H_WALL1': '16tile.tga',
              'PIX_JAGGED_GROUND_1': '16jwg1.tga',
              'PIX_JAGGED_GROUND_2': '16jwg2.tga',
              'PIX_JAGGED_GROUND_3': '16jwg3.tga',
              'PIX_JAGGED_GROUND_4': '16jwg1.tga',
              'PIX_PATH_1': '16path1.tga',
              'PIX_PATH_2': '16path2.tga',
              'PIX_PATH_3': '16path3.tga',
              'PIX_PATH_4': '16path4.tga',
              'PIX_PAVEMENT1': '16pave1.tga',
              'PIX_PAVEMENT2': '16pave2.tga',
              'PIX_PAVEMENT3': '16pave3.tga',
              'PIX_PAVESTEPS1': '16pstep.tga',
              'PIX_PAVESTEPS2': '16ptest.tga',
              'PIX_PAVESTEPS2L': '16ptestl.tga',
              'PIX_PAVESTEPS2R': '16ptestr.tga',
              'PIX_TORCH1': '16torch1.tga',
              'PIX_TORCH2': '16torch2.tga',
              'PIX_TORCH3': '16torch3.tga',
              'PIX_TREE_B1': '16treeb1.tga',
              'PIX_TREE_M1': '16treem1.tga',
              'PIX_TREE_ML': '16treeml.tga',
              'PIX_TREE_MR': '16treemr.tga',
              'PIX_TREE_MT': '16treemt.tga',
              'PIX_TREE_T1': '16treet1.tga',
              'PIX_VOID1': '16space.tga',
              'PIX_WALL2': '16wall2.tga',
              'PIX_WALL3': '16wall3.tga',
              'PIX_WALL4': '16walllo.tga',
              'PIX_WALL5': '16w2lo.tga',
              'PIX_WALLSIDE1': '16brick1.tga',
              'PIX_WALLSIDE_C': '16brickc.tga',
              'PIX_WALLSIDE_CRACK_C1': '16brick3.tga',
              'PIX_WALLSIDE_L': '16brickl.tga',
              'PIX_WALLSIDE_R': '16brickr.tga',
              'PIX_WALLTOP_H': '16ttop.tga',
              'PIX_WALL_ARROW_FLOOR': '16wallof.tga',
              'PIX_WALL_ARROW_GRASS': '16wallog.tga',
              'PIX_WALL_ARROW_GRASS_DARK': '16wallod.tga',
              'PIX_WALL_LL': '16wallll.tga',
              'PIX_WATER1': '16water1.tga',
              'PIX_WATER2': '16water2.tga',
              'PIX_WATER3': '16water3.tga',
              'PIX_WATERGRASS_D': '16wgd.tga',
              'PIX_WATERGRASS_L': '16wgl.tga',
              'PIX_WATERGRASS_LL': '16wgll.tga',
              'PIX_WATERGRASS_LR': '16wglr.tga',
              'PIX_WATERGRASS_R': '16wgr.tga',
              'PIX_WATERGRASS_U': '16wgu.tga',
              'PIX_WATERGRASS_UL': '16wgul.tga',
              'PIX_WATERGRASS_UR': '16wgur.tga'}
  
  #register all times from the game
  for name, filename in tileDict.iteritems():    
    glad.resource.register(name, 
                           os.path.join(tileFolder,filename), 
                           size=tileSize)