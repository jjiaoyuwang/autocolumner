class Sepfunnel:
    def __init__(self,id):
        self.status=False;##the sep_funnel is off.
        self.id=id;


    def on(self):
        self.status=True;
        return "the sep_funnel "+self.id+"  is on.";
    

    def off(self):
        self.status=False;
        return "the sep_funnel "+self.id+" is off.";