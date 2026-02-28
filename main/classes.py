class Train:
    def __init__(self):
        self.carriages = [Carriage(i) for i in range(1,12)]
class Carriage:
    def __init__(self, number):
        self.number = number
        self.seats = [Seat(i) for i in range(1,101)]

class Seat:
    def __init__(self,number):
        self.number = number
        self.is_taken = False