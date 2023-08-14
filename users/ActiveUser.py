class ActiveUser:
    def __init__(self,user=None) -> None:
        if user is None:
            self.user=[]
        else:
            self.user=user
    def setUser(self,user):
        self.user=user
    def getUser(self):
        return self.user