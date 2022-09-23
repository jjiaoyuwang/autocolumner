class Arm:
    def __init__(self,id):
        self.id=id;
        self.position=0;


    def smaller(self):
        if self.position>0:
            self.position=self.position-1;
        return "the arm is at "+str(self.position);
    

    def bigger(self):
        if self.position<10:
            self.position=self.position+1;
        return "the arm is at "+str(self.position);

    def tomin(self):
        self.position=0;
        return "the arm is at "+str(self.position);

    def tomax(self):
        self.position=10;
        return "the arm is at "+str(self.position);