class Pump:
    def __init__(self,id):
        self.status=False;##the pump is off.
        self.id=id;


    def on(self):
        self.status=True;#turn on
        return "the pump "+self.id+"  is on.";
    

    def off(self):
        self.status=False;#turn off
        return "the pump "+self.id+" is off.";
    
