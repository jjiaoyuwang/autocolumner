class Vacuum:
    def __init__(self,id):
        self.status=False;##the vacuum is off.
        self.id=id;


    def on(self):
        self.status=True;
        return "the vacuum "+self.id+"  is on.";
    

    def off(self):
        self.status=False;
        return "the vacuum "+self.id+" is off.";