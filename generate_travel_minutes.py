import random
import math

def matrix_generator(num_couriers, num_orders):

    """
        Generates the ETA matrix with given number of couriers and orders
        Order eta boundaries are 1, 30
        inputs num_couriers: Number of couriers
               num_orders: Number of orders
               
        output ETA_matrix
    
    """

    travel_minutes = []

    for courier in range(num_couriers):

        courier_orders = []

        for order in range(num_orders):

            courier_orders.append(random.randint(1,30))


        travel_minutes.append(courier_orders)

    return travel_minutes

def calculate_distance(x_start,y_start, x_end, y_end):

    """
        Calculates the oklidian distance of two points
        inputs  x_start x position of the courier
                y_start y position of the courier
                x_end x position of the delivery
                y_end y position of the delivery
    
    """

    return math.sqrt((x_end-x_start)**2 + (y_end-y_start)**2)

def calculate_travel_minutes():

    pass

def main(num_couriers, num_orders):

    matrix = matrix_generator(num_couriers, num_orders)

if __name__ == "__main__":

    main(6, 6)
    print(calculate_distance(0,0,3,4))
