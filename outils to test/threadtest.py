import time
from threading import Thread


def chatbot():
    time.sleep(5)
    print("AND FINISHED CHATBOT")
    thread_2.stopthread()
def WaitForAnswer():
        
        print("State Wait")
        answer = ""
        #while answer == "":
        while thread_2.is_alive():# == True :    
            for x in range (0,200):
                #m.pos(1,1)
                #m._print(str(x))
                print(x)
                time.sleep(1)
        self.changeState(self.stateSend)

##############################################################################
class Monthread(threading.Thread):
 
    def __init__(self):
        threading.Thread.__init__(self)
        self.arret=False # =variable pour porter l'ordre d'arrêter le thread
 
    def run(self):
        try:
            # ...
            while True:
                if self.arret:
                    raise ValueError ("arrêt demandé")
                # ...
            # ...
        except:
            # ...
            # récupération et impression du message d'erreur
            print u"%s" % sys.exc_info()[1]
            # ...
            # fin de run, donc fin du thread
 
    def stopthread(self):
        self.arret=True
 
##############################################################################

print "Lancement du thread"
app=Monthread()
app.start()
tps=time.time()
while app.isAlive():
    if time.time()-tps > 5: # arrêt du thread au bout de 5 secondes
        app.stopthread()
    time.sleep(0.1)
print "fin du thread"
time.sleep(2)

message = "trallai"
thread_1 = Thread(target=WaitForAnswer, args=())
thread_2 = Thread(target=chatbot, args=())
thread_1.start()
            
thread_2.start()
print("Shit started")
            
