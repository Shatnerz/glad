#python imports
import logging

#glad imports
#game globals here
import glad
import config
import sdl
import resourceManager
import worldManager

if __name__ == '__main__':
  #Setup logging
  logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(funcName)s: %(message)s')


  #Setup our application
  
  glad.config = config.BasicConfig('config.cfg')
  app = glad.app = sdl.App()
  glad.input = app.getInputInterface() 
  
  #Setup the resource manager
  glad.resource = resourceManager.ResourceManager()
    
  #Load a test world
  world = glad.world = worldManager.TestWorld()
  
  renderer = sdl.Renderer()
  
  #Load default glad graphics
  resourceManager.registerGladResources()
    
     
  while app.isRunning():
    
    app.update()    
    
    timeDelta = app.getTimeDelta()
    
    world.update(timeDelta)
    
    renderer.draw(world) 


    


#a = Rect((0,0),(10,10))
#a.vel = (2.0,0.0)
#
#b = Rect((75,0), (10,10))
#b.vel = (0.0,0.0)
#
#print a.getCollisionInfo(b)
  
  
  