import random
import math

def constant_matrix_generator(num_couriers, num_orders):

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
        Calculates the euclidean distance of two points
        inputs  x_start x position of the courier
                y_start y position of the courier
                x_end x position of the delivery
                y_end y position of the delivery
    
    """

    return math.sqrt((x_end-x_start)**2 + (y_end-y_start)**2)

def calculate_travel_minutes(distance, speed_kmh):

    """
        Calculates the travel duruation
        inputs  courier speed in kmh
                order distance in km

        output travel time in minutes       
    """
    return (distance/speed_kmh)*60

def courier_restorant_eta_matrix(courier_positions, restaurant_positions, travel_speed):

    """
    Calculates the eta matrix with position of the restaurant and the current position of the courier

    inputs  actual position of the courier
            restaurant position 
            travel speed of the courier

    output  eta matrix

    """

    courier_restorant_eta_matrix = []

    for courier in range(len(courier_positions)):

        travel_time = []

        for restaurant in range(len(restaurant_positions)):

            distance = calculate_distance(courier_positions[courier][0],
                                        courier_positions[courier][1],
                                        restaurant_positions[restaurant][0],
                                        restaurant_positions[restaurant][1])



            travel_t = calculate_travel_minutes(distance, travel_speed)
            travel_time.append(travel_t)

        courier_restorant_eta_matrix.append(travel_time)

    return courier_restorant_eta_matrix

def restaurant_delivery_eta_matrix(restaurant_positions, delivery_positions, travel_speed):

    """
    Calculates the eta matrix with position of the restaurant and the current position of the courier

    inputs  restaurant position
            dropoff position
            travel speed of the courier

    output  eta matrix

    """

    restaurant_delivery_eta_matrix = []

    for restaurant in range(len(restaurant_positions)):

        travel_time = []

        for delivery in range(len(delivery_positions)):

            distance = calculate_distance(restaurant_positions[restaurant][0],
                                        restaurant_positions[restaurant][1],
                                        delivery_positions[delivery][0],
                                        delivery_positions[delivery][1])



            travel_t = calculate_travel_minutes(distance, travel_speed)
            travel_time.append(travel_t)

        restaurant_delivery_eta_matrix.append(travel_time)

    return restaurant_delivery_eta_matrix

def calculate_delivery_time(pick_up_travel, remaining_prep_minutes, dropoff_travel_minutes):

    return max(remaining_prep_minutes, pick_up_travel) + dropoff_travel_minutes

def main(num_couriers, num_orders):

    matrix = constant_matrix_generator(num_couriers, num_orders)

if __name__ == "__main__":

    main(6, 6)
    #print(calculate_travel_minutes(calculate_distance(0,0,3,4), 15))
    #print(generate_eta_matrix([(0, 0), (3, 0)], [(3, 4), (0, 4)], 15))


    courier_restaurant = courier_restorant_eta_matrix([(0, 0), (3, 0)], [(3, 4), (0, 4)], 15)
    restaurant_delivery = restaurant_delivery_eta_matrix([(3, 4), (0, 4)], [(6, 4), (0, 7)], 15)

    print([[restaurant_delivery[i][j] + courier_restaurant[i][j] for j in range(len(restaurant_delivery[0]))] for i in range(len(restaurant_delivery))])

    #print(calculate_delivery_time(8,12,6))
