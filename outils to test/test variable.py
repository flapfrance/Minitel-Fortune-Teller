class player():
   def __init__(self):
      self._position = 1   
   @property
   def position(self):
      return self._position@position.setter

@position.setter   
def position(self, newPosition):
      self._position = newPosition
      print("execute more code here!")

p = player()
print(p.position)
p.position = 2
