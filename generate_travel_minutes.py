import random

def matrix_generator(num_couriers, num_orders):

    """
        Generates the ETA matrix with given number of couriers and orders
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

def main(num_couriers, num_orders):

    matrix = matrix_generator(num_couriers, num_orders)

if __name__ == "__main__":

    main(6, 6)
