#python imports
import logging

#glad imports
#game globals here
import glad
import config
import sdl
import resourceManager
import worldManager
import soundManager

if __name__ == '__main__':
  #Setup logging
  logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(funcName)s: %(message)s')

  #Setup our application
  glad.config = config.BasicConfig('config.cfg')
  app = glad.app = sdl.App()
  glad.input = app.getInputInterface() 
  
  #Setup the resource manager
  glad.resource = resourceManager.ResourceManager()
   
  renderer = sdl.Renderer()
  glad.renderer = renderer
  
  #Load default glad graphics
  
  resourceManager.registerGladResources()
  
  #Load a test world
  world = glad.world = worldManager.TestWorld1()
  
  sound = glad.sound = soundManager.SoundManager()
  
  glad.sound.playMusic()
  
    
     
  while app.isRunning():
    
    app.update()    
    
    timeDelta = app.getTimeDelta()
    
    world.update(timeDelta)
    
    renderer.draw(world)
    
    sound.update()