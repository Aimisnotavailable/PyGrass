import pygame
from scripts.utils import load_images

class Assets:
    
    def __init__(self):
      self.assets = {
                  'img' : {
                      'grass' : load_images("\grass"),

                  },

                  "sfx" : {},
                  }