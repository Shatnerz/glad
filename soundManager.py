import glad
import pygame
from util import dotProduct
from util import Vector

class SoundManager(object):
  """Abstract Class to Handle all sounds"""
  
  def __init__(self):
    self.channels = 8
    pygame.mixer.set_num_channels(self.channels)
    #pygame.mixer.set_reserved(2) #not sure how this works but reverse a channel for menu sounds and music
    #TODO - ignore sounds that are below a certain intensity
  
  def play(self, sound, pos):
    
    #Calculate volume
    left, right = self.getIntensity(pos)

    #find open channel
    channel = pygame.mixer.find_channel()              
    #open new channel if needed
    #theres probably a safer way of doing this
    while channel is None: #open new channel if needed
      self.setNumChannels(self.channels+1)
      print 'Creating new audio channel: ', self.channels
      channel = pygame.mixer.find_channel() 
      
    #play sound
    #sound.play()
    channel.play(sound)
    channel.set_volume(left, right)
    #print left,'\t',right
    
  def setNumChannels(self, num):
    self.channels = num
    pygame.mixer.set_num_channels(self.channels)
    
  def getIntensity(self, pos):
    #Camera doesnt have position so im just using the position of the followed object (of 1st camera)
    camPos = glad.renderer.cameraList[0].objectFollowed.getPos()

    r=(pos-camPos)#separation vector
    if r.isNullVector(): #if the vector is null, sound will be max anyways
      sin = 1
      cos = 1
    else:
      #calculate angles to determine where sound is coming from
      cos = dotProduct(r.getNormalized(),Vector(-1,0))
      sin = dotProduct(r.getNormalized(), Vector(0,1))
    #Calculate intensity for left and right channels
    #when sound is directly to the side have 80 percent come from that side speaker
    #hopefully this will give some directional sounds
    k = 130000 #arbitrary constant to calculate sound intensity
    if r.isNullVector():
      intensity = k #removes division by zero error
    else:
      intensity = k/r.getMagnitude()**2
    #major is the percent of the sound intensity from the side with the greater intensity
    a=0.68 #max percent of the intensity coming from one side
    major = (a*0.5)/((0.5*cos)**2+(a*sin)**2)**0.5 #equation for an ellipse
    if r[0] <= 0:
      right = major
      left = 1-major
    else:
      left = major
      right = 1-major
    right *= intensity
    left *= intensity
    if right > 1: right = 1
    if left > 1: left = 1
    return left,right
  