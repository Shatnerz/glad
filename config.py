
import ConfigParser

class BasicConfig(object):
  
  def __init__(self, filename):
    
    self.parser = ConfigParser.RawConfigParser()
    
    self.parser.read(filename)  
  
  def get(section, option):
  
    return self.parser.get(section, option)

  def getBoolean(section, option):
    return self.parser.getboolean(section,option)


  def getResolution(section, option):
  
    s = self.get(section, option)  
    l = s.split('x')  
    l = [int(x) for x in l]
  
    return tuple(l)
                    
