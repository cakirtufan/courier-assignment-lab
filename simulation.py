class Courier():

    def __init__(self, courier_id, x, y, speed_kmh):

        self.courier_id = courier_id 
        self.x = x
        self.y = y
        self.speed_kmh = speed_kmh
        self.status = "available"
        self.assignment_order = None

         

courier = Courier(1,0,0,15)
print(courier.courier_id, courier.x, courier.y, courier.status)