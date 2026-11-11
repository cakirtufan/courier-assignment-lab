import pulp

travel_minutes = [
                [4,5,14,16], 
                [5,19,17,20], 
                [16,15,4,7], 
                [18,17,6,11]
                 ]

assignment = [2,0,3,1]

def total_travel_time(travel_minutes, assignment):

    """Calculates the total travel time for a given assignment of couriers to delivery locations.

        input: travel_minutes - a 2D list where each row represents a courier and each column represents a delivery location.
               assignment - a list where the index represents the courier and the value at that index represents the order.

    """

    delivery_estimation = []

    for index, estimation in enumerate(travel_minutes):

        delivery_estimation.append(travel_minutes[index][assignment[index]])

    return sum(delivery_estimation)

def assign_orders(travel_minutes):

    """Assigns orders to couriers based on the minimum travel time.

        input: travel_minutes - a 2D list where each row represents a courier and each column represents a delivery location.

        output: assigned_orders - a list where the index represents the courier and the value at that index represents the order.

    """

    index_order = list(range(len(travel_minutes[0])))
    assigned_orders = []

    for courier in travel_minutes:

        if len(index_order) == len(travel_minutes):


            selected_order = courier.index(min(courier))
            index_order.remove(selected_order)
            assigned_orders.append(selected_order)
  
        else:

            time = []
            for order in index_order:
                time.append(courier[order])
            
            position = time.index(min(time))
            selected_order = index_order[position]
            index_order.remove(selected_order)

            
            assigned_orders.append(selected_order)

    return assigned_orders

def solve_assignment_problem(travel_minutes):

    """Solves the assignment problem using linear programming.

        input: travel_minutes - a 2D list where each row represents a courier and each column represents a delivery location.
        output: stats - the status of the optimization problem and the total travel time.

    """

    model = pulp.LpProblem("Courier_Assignment_Problem", pulp.LpMinimize)

    num_couriers = len(travel_minutes)
    num_orders = len(travel_minutes[0])

    X = {}
    for i in range(num_couriers):
        for j in range(num_orders):
            X[(i, j)] = model.add_variable(f"X_{i}_{j}", cat="Binary")
   

    model += pulp.lpSum(
        travel_minutes[x[0]][x[1]]*X[x]
        for x in X
    )

    for i in range(num_couriers):

        model += pulp.lpSum(X[i, j] for j in range(num_orders)) == 1

    for j in range(num_orders):

        model += pulp.lpSum(X[i, j] for i in range(num_couriers)) == 1

    stats = model.solve(pulp.COIN_CMD(msg=False))

    if stats.status_str != "Optimal":

        raise RuntimeError("Solver didn't find the optimal solution", f"Model status is {stats.status_str}")

    solution = []

    for i in range(num_couriers):
        for j in range(num_orders):
            if pulp.value(X[i, j]) == 1:
                solution.append(j)
    
    return stats, solution
  

def main():

    assigned_orders_greedy = assign_orders(travel_minutes)
    stats, assigned_orders_optimized = solve_assignment_problem(travel_minutes)
    total_travel_time_greedy = total_travel_time(travel_minutes, assigned_orders_greedy)
    total_travel_time_optimized = total_travel_time(travel_minutes, assigned_orders_optimized)
    print("=== Assignment Results ===")
    print(f"Total travel time in greedy search {total_travel_time_greedy} minutes") 
    print(f"Total travel time in MIP search {total_travel_time_optimized} minutes") 
    print(f"Difference is {abs(total_travel_time_greedy-total_travel_time_optimized)} minutes")
        

if __name__ == "__main__":
    main()