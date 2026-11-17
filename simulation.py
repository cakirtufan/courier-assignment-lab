import math

class Courier():

    def __init__(self, courier_id, x, y, speed_kmh):

        self.courier_id = courier_id 
        self.x = x
        self.y = y
        self.speed_kmh = speed_kmh
        self.status = "available"
        self.assigned_order = None

    def assign_order(self,order):

        """
        Assigning order to courier
        """

        self.assigned_order = order
        self.status = "to_restaurant"
        order.assigned_courier_id = self.courier_id
        order.status = "assigned"

    def calculate_distance(self, x_end, y_end):

        """
            Calculates the euclidean distance of two points
            inputs  x_start x position of the courier
                    y_start y position of the courier
                    x_end x position of the delivery
                    y_end y position of the delivery
        
        """

        x_start, y_start = self.x, self.y 

        return math.sqrt((x_end-x_start)**2 + (y_end-y_start)**2)


    def move_towards(self, target_position, minutes):

        """
        Simulates the movement of the courier to pick up order it updates the position of the courier in given minutes
        
        inputs  target_position: restaurant position 
                minutes: duration of the drive

        output  updates the current position of the courier
        """


        x_target, y_target = target_position

        distance = self.calculate_distance(x_target, y_target)

        travel_distance = self.speed_kmh * (minutes / 60)

        if travel_distance >= distance:

            self.x, self.y = x_target, y_target

            return True

        else:

            ratio = travel_distance/distance
            x_new = self.x + (x_target-self.x) * ratio
            y_new = self.y + (y_target-self.y) * ratio

            self.x, self.y = x_new, y_new

            return False

    def try_pickup(self, current_time):

        if current_time >= self.assigned_order.ready_at:

            self.status = "to_customer"
            self.assigned_order.status = "picked_up"

        else:

            self.status = "waiting_at_restaurant"
            self.assigned_order.status = "assigned"

    def complete_delivery(self, current_time):

        self.assigned_order.status = "delivered"
        self.assigned_order.delivered_at = current_time
        self.assigned_order = None
        self.status = "available"

    def update(self, current_time, minutes):

        if self.status == "to_restaurant":

            target_position = self.assigned_order.restaurant_position
            
            if self.move_towards(target_position, minutes) is True:

                self.try_pickup(current_time+minutes)

        elif self.status == "waiting_at_restaurant":

            self.try_pickup(current_time+minutes)

        elif self.status == "to_customer":

            delivery_position = self.assigned_order.delivery_position

            arrived = self.move_towards(delivery_position, minutes)

            if arrived:

                self.complete_delivery(current_time+minutes)


class Order():

    def __init__(self, order_id, restaurant_position, delivery_position, created_at, prep_minutes):

        
        self.status = "waiting"
        self.assigned_courier_id = None
        self.order_id = order_id
        self.restaurant_position = restaurant_position
        self.delivery_position = delivery_position
        self.created_at = created_at
        self.prep_minutes = prep_minutes
        self.ready_at = created_at + prep_minutes
        self.delivered_at = None



class RouteProgress():

    def __init__(self, edge_lengths_m, speed_kmh):

        self.edge_lengths_m = edge_lengths_m
        self.speed_kmh = speed_kmh
        self.courier_edge_index = 0
        self.distance_on_edge_m = 0
        self.finished = False


    def calculate_travel_distance(self, minutes):

        return self.speed_kmh * (minutes/60) * 1000

    def calculate_rest_distance(self):

        return self.edge_lengths_m[self.courier_edge_index] - self.distance_on_edge_m

    def advance(self,minutes):

        travel_distance = self.calculate_travel_distance(minutes)
        rest_distance = self.calculate_rest_distance()

        if travel_distance < rest_distance:
        
            self.distance_on_edge_m += travel_distance


from travel_times import courier_restorant_eta_matrix, calculate_dropoff_times, calculate_delivery_time

couriers = [Courier(1,0,0,15), Courier(2,0,0,15)]
orders = [Order(101,(3,2),(5,7),0,4), Order(102,(2,4),(5,9),3,2)]



for current_time in range(6):

    waiting_orders = []
    available_couriers = []

    for order in orders:

        if order.created_at <= current_time and order.status == "waiting":

            waiting_orders.append(order)

    # print(current_time, [order.order_id for order in waiting_orders])

    for courier in couriers:

        if courier.status == "available":

            available_couriers.append(courier)

    # print(current_time, [courier.courier_id for courier in available_couriers])

    if available_couriers and waiting_orders:

        courier_positions = [(courier.x, courier.y) for courier in available_couriers]
        restaurant_positions = [order.restaurant_position for order in waiting_orders]
        delivery_positions = [order.delivery_position for order in waiting_orders]
        remaining_prep_minutes = [max(0, order.ready_at - current_time) for order in waiting_orders]

        courier_restaurant = courier_restorant_eta_matrix(courier_positions, restaurant_positions, 15)
        restaurant_deliver = calculate_dropoff_times(restaurant_positions, delivery_positions, 15)

        print(
                calculate_delivery_time(courier_restaurant, remaining_prep_minutes, restaurant_deliver)
            )
