import glad
import pygame
from util import dotProduct
from util import Vector

from os import listdir
from os.path import isfile, join

class SoundManager(object):
  """Abstract Class to Handle all sounds"""
  
  def __init__(self):
    self.channels = 8
    pygame.mixer.set_num_channels(self.channels)
    #pygame.mixer.set_reserved(2) #not sure how this works but reverse a channel for menu sounds and music
    
    self.soundVolume = 1 #from 0 to 1
    self.musicVolume = 1 #from 0 to 1
    
    self.battleMusic = self.getMusic('resources/sound/music/battle')
    self.menuMusic = self.getMusic('resources/sound/music/menu')
    self.currentMusic = None
    self.songIndex = 0
    
  
  def play(self, sound, pos):
    
    #Calculate volume
    left, right = self.getIntensity(pos)

    if left + right >= 0.02: #arbitrary cutoff volume
      left *= self.soundVolume
      right *= self.soundVolume
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
      
  def playMusic(self, music = None, index=0):
    """Plays music from a list or file locations. List will repeat with soundManager.update()"""
    if music == None:
      music = self.battleMusic
    if isinstance(music, list):
      self.songIndex = index
      while self.songIndex > len(music)-1:
        self.songIndex -= len(music)
      pygame.mixer.music.load(music[self.songIndex])
    else:
      self.songIndex = 0
      pygame.mixer.music.load(music)
    self.currentMusic = music
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(self.musicVolume)
    pygame.mixer.music.set_endevent(pygame.constants.USEREVENT)
    
  def stopMusic(self):
    pygame.mixer.music.stop()
    
  def fadeMusic(self, time=400):
    """Stop music after fading out over time (in ms)"""
    pygame.mixer.music.fadeout(time)
    
  def getMusic(self, path):
    """Reutrns a list of all mp3 in a foler"""
    music =[]
    files = [ f for f in listdir(path) if isfile(join(path,f))]
    for f in files:
      m = join(path,f)
      #if not f.endswith('.mp3'):
      #  files.remove(f)
      if f.endswith('.mp3'):
        music.append(m)
    return music
    
  def setNumChannels(self, num):
    self.channels = num
    pygame.mixer.set_num_channels(self.channels)
    
  def getIntensity(self, pos):
    """Returns the appropriate intensity of the sound being played assuming intensity falls off at 1/r^2"""
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
  
  def update(self):
    """Check if background music ended"""
    for event in pygame.event.get(pygame.constants.USEREVENT):
      if event.type == pygame.constants.USEREVENT:
        if self.currentMusic is not None:
          #play next song
          self.songIndex += 1
          self.playMusic(self.currentMusic, self.songIndex)