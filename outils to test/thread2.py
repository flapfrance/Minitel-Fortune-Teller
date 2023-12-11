 
 
import threading
import time
 
class monThread(Thread):
   def __init__(self):
      Thread.__init__(self)
       self._etat = False
       self._pause = False
 
   def run(self):
       self._etat = True
       while self._etat:
          if self._pause:
              time.sleep(0.1)  # éviter de saturer le processeur
              continue 
          #faire plein de truc...
 
    def stop(self)
        """Arrête l'exécution du thread.
 
        Après avoir appelé cette fonction le thread n'est plus utilisable.
        """
        self._etat = False
 
    def pause(self):
        """Arrête l'exécution du thread momentanément."""
        self._pause = True
 
    def continue(self):
        """Reprendre l'exécution d'un thread 'mis en pause'."""
        self._pause = False
