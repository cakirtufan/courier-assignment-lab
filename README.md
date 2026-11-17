# Courier Assignment Lab

I am building this project step by step to learn courier assignment, mathematical optimisation, and delivery simulation, and to prepare for hiring manager and technical interviews for an Operations Research/Data Scientist role.

The project started with a small synthetic assignment problem solved with greedy search and PuLP/CBC. The next goal is a simulation in which orders arrive over time, couriers move, restaurants prepare food, and available couriers receive new assignments. I want to compare assignment methods on the same scenarios and understand their behaviour under changing demand.

The assignment algorithm chooses who serves each order. The simulation measures what happens after those decisions. A better result on one static matrix does not necessarily imply better performance over an entire delivery day.

## Current implementation — 17 November 2026

| File | Implemented | Still to connect or improve |
|---|---|---|
| `travel_times.py` | Random matrices, Euclidean distances, travel minutes, courier-to-restaurant matrices, per-order dropoff times, and preparation-aware delivery estimates | Input validation, reproducible random scenarios, and support for different courier speeds in the ETA calculation |
| `assignment.py` | Greedy assignment, binary optimisation with PuLP/CBC, objective calculation, and solver status checking | Unequal fleet/order counts, explicit courier–order result pairs, and simulation integration |
| `simulation.py` | `Courier` and `Order` classes; movement, pickup, waiting, delivery, and state updates; filtering by order arrival and courier availability | Automatic assignment, calls to courier updates in the main loop, completion conditions, and experiment metrics |

The current top-level loop in `simulation.py` runs six time steps and prints delivery-time matrices. It does **not yet assign orders or move couriers**. The lifecycle methods exist, but the loop still needs to connect them to the assignment solver. The example has two couriers and orders arriving at minutes 0 and 3, producing a 2×1 matrix followed by a 2×2 matrix.

`assignment.py` uses `constant_matrix_generator` from `travel_times.py` to generate random integer times from 1 to 30 for its comparison example.

## Delivery-time model

Positions are synthetic Cartesian `(x, y)` coordinates in kilometres, not latitude and longitude. Travel is along straight lines at a constant speed. Minutes are the simulation's time unit:

```text
travel_minutes = distance_km / speed_kmh * 60
ready_at = created_at + prep_minutes
remaining_prep_minutes = max(0, ready_at - current_time)
delivery_eta[i][j] = max(pickup_eta[i][j], remaining_prep_minutes[j]) + dropoff_minutes[j]
```

Preparation and travel to the restaurant happen in parallel. If a courier arrives in 8 minutes, food is ready in 12 minutes, and the customer is 6 minutes from the restaurant, delivery takes 18 minutes from now. The courier waits at the restaurant for 4 minutes.

Each matrix row represents an available courier; each column represents a waiting order. The restaurant and customer at the same order index belong together. Dropoff times are therefore a list with one value per order, rather than all restaurant–customer combinations. The current matrix calculation uses a shared speed of 15 km/h; it must be adapted before using different courier speeds.

An ETA here is a duration from the current decision time. It excludes time the order has already spent waiting. End-to-end delivery time will be measured separately as `delivered_at - created_at`.

## Courier and order lifecycle

`Courier` stores identity, position, speed, state, and a reference to its assigned `Order`. `Order` stores its restaurant, customer, arrival time, preparation duration, ready time, assignment, and delivery timestamp.

```text
Courier: available → to_restaurant → waiting_at_restaurant → to_customer → available
Order:   waiting → assigned → picked_up → delivered
```

The restaurant waiting state is skipped if the food is already ready. After delivery, the courier stays at the customer's location and becomes available again. Each courier carries at most one order, and the intended policy does not reassign an order once allocated.

`update(current_time, minutes)` treats `current_time` as the beginning of a step. It moves the courier or checks preparation, then records transitions at `current_time + minutes`. Only one state branch is processed per call. Unused time after reaching a destination is not carried into the next leg, so this discrete simulation can finish later than the continuous ETA estimate.

A small manual lifecycle check uses a courier at `(0, 0)`, restaurant at `(0.5, 0)`, customer at `(1, 0)`, speed 15 km/h, and preparation ending at minute 4. With one-minute updates, the courier reaches the restaurant at minute 2, waits until minute 4, and delivers at minute 6. This is a development check, not an automated test suite.

## Next steps: connect the simulation

The intended step order is:

1. Select orders with `created_at <= current_time` and status `waiting`.
2. Select couriers with status `available`.
3. If both groups are nonempty, calculate their delivery-time matrix and solve the assignment.
4. Map selected matrix indices back to the filtered objects and call `assign_order`.
5. Call `update(current_time, 1)` for **every courier**, including when no new assignment is possible.
6. Record results and advance the clock; eventually stop when all scheduled orders have been delivered, with a maximum horizon for incomplete runs.

The existing solver requires exactly one order per courier and exactly one courier per order. For unequal counts, the planned formulation will use at-most-one constraints on both sides and require a total of `min(available couriers, waiting orders)` assignments, assuming all pairs are feasible. Without that total, minimising nonnegative costs could select no assignments at all.

The solver, greedy baseline, and objective evaluator will need a consistent result format that supports unassigned couriers, such as explicit `(courier_index, order_index)` pairs. These indices refer to the filtered lists, not persistent object IDs.

## Experiments and later extensions

The aim is to replay the same order arrivals, preparation durations, initial positions, and fleet settings for each assignment method. Each run should start from fresh objects, and random scenario generation should use a recorded seed. Random preparation durations should be sampled once per order, rather than resampled at each decision.

Planned measurements include mean and maximum order-to-delivery time, time waiting for assignment, courier waiting time at restaurants, outstanding orders at the end of a run, and assignment computation time. Most of these metrics and event timestamps still need to be implemented. Comparing several scenarios will help explore demand peaks and fleet shortages without claiming that one small example proves general performance.

Map visualisation is a later goal: display restaurants, customers, courier movement, and assignment decisions. Real road travel times and routes would be a separate extension requiring geographic coordinates, a routing source, and movement along routes. No map or routing API is integrated yet.

This is currently preparation for dynamic assignment. A full vehicle routing problem, with multiple orders per courier and decisions about pickup/delivery sequence, remains a future extension.

## Running the current work

```powershell
python -m pip install -r requirements.txt
python simulation.py
```

The simulation command currently prints ETA matrices only. `python travel_times.py` runs its calculation example without printing results. `python assignment.py` runs the greedy-versus-MIP comparison on a random 4×4 matrix; results vary between runs and are not the fixed historical totals below. The example loop in `simulation.py` is currently at module level, so importing that module also runs it; moving it behind a main guard is still pending.

## Original static assignment exercise

The remaining sections preserve the original worked example and learning notes. Its fixed matrix and reported 45-versus-23-minute results are historical reference values, not output from the current simulation or random generator.

## The problem

I have four available couriers and four orders. I need to choose one courier for each order.

The table shows how many minutes each courier needs to reach the restaurant for each order. These are synthetic values created for this exercise.

| Courier | Order 1 | Order 2 | Order 3 | Order 4 |
|---|---:|---:|---:|---:|
| A | 4 | 5 | 14 | 16 |
| B | 5 | 19 | 17 | 20 |
| C | 16 | 15 | 4 | 7 |
| D | 18 | 17 | 6 | 11 |

## Initial assumptions

- Each courier must take exactly one order.
- Each order must be assigned to exactly one courier.
- Travel times are fixed, and I consider a single assignment decision.
- The times cover travel to the restaurant only.

## Objective and decision variables

My aim is to minimise the total travel time of the selected courier–order pairs. In this example, that means the time needed to reach the restaurants.

- `t_ij`: the travel time from courier i to the restaurant for order j. This comes from the table.
- `x_ij`: 1 if courier i is assigned to order j, and 0 otherwise. This is the decision the model makes.

The objective is:

$$
\min \sum_i \sum_j t_{ij} x_{ij}
$$

A selected pair contributes its travel time to the total. An unselected pair contributes zero. Adding up only the `x_ij` values would give 4 for every valid assignment, so the travel times need to be included too.

## Constraints

### Each courier takes exactly one order

For each courier, I sum the assignment decisions across all orders. The total must be 1:

$$
\sum_j x_{ij} = 1 \qquad \forall i
$$

This means each row of the assignment matrix contains exactly one 1. All other entries in that row are 0.

### Each order is assigned to exactly one courier

This time, I fix an order and sum across all couriers. The total must also be 1:

$$
\sum_i x_{ij} = 1 \qquad \forall j
$$

Each column therefore contains exactly one 1 as well.

### Assignment decisions are binary

$$
x_{ij} \in \{0,1\} \qquad \forall i,j
$$

Each possible pair is either selected or not selected.

## Calculating the travel time of an assignment

I represent the travel-time table as a list of lists in Python. An assignment is represented as another list:

```python
assignment = [2, 0, 3, 1]
```

The position in this list identifies the courier, and the value identifies the order index. Python indices start at 0.

In `total_travel_time`, I find each courier's assigned order using `assignment[index]`, then look up the corresponding time:

```python
travel_minutes[index][assignment[index]]
```

One loop over the couriers is enough. I collect the selected times in a separate list and return their sum.

For the example assignment, the times are `14, 5, 7, 17`, giving a total of **43 minutes**. I also checked that the function leaves the original travel-time table unchanged. Another example, `[0, 1, 2, 3]`, gives **38 minutes**.

## What happens if every courier chooses independently?

A first idea is to let every courier choose the shortest time in their own row. However, several couriers can choose the same order. In this table:

- A and B both choose Order 1.
- C and D both choose Order 3.

The resulting assignment, `[0, 0, 2, 2]`, is invalid. Orders 1 and 3 are each selected twice, while Orders 2 and 4 are not assigned at all. This breaks the constraint that each order must be assigned to exactly one courier.

## My greedy baseline

Once an order has been selected, I remove it from the options available to later couriers. I keep the original order indices in a separate list rather than modifying the travel-time table.

I process the couriers in the order A, B, C, D. For each courier, I select the remaining order with the shortest travel time and remove its index from the available list. This is a greedy approach: it makes the best available choice at each step.

On the example table, it produces `[0, 2, 3, 1]`. The selected times are `4, 17, 7, 17`, giving a total of **45 minutes**. This is a valid assignment, but it does not prove that the total is the smallest possible.

### Keeping the order indices correct

During checking, I found an indexing issue. After finding the shortest available time, searching the full courier row with `courier.index(...)` could return an order that had already been assigned if two times were equal.

I fixed this in two steps:

```python
position = time.index(min(time))
selected_order = index_order[position]
```

I build `time` in the same order as `index_order`. First, I find the position of the smallest available time. Then I use that position to retrieve the original order index.

The function is called `assign_orders` and returns its selected indices with `return assigned_orders`. I checked the corrected version in two cases:

| Case | Returned assignment | Total time |
|---|---|---:|
| Original travel-time table | `[0, 2, 3, 1]` | 45 minutes |
| B's time for Order 3 changed to 5 minutes, creating a tie with Order 1 | `[0, 2, 3, 1]` | 33 minutes |

In both cases, each order is selected once and the travel-time table remains unchanged.

## Why greedy does not guarantee the smallest total

Processing couriers one at a time does not guarantee the smallest total. One courier's nearest order can leave worse options for a later courier. Swapping two couriers' orders can improve the overall result.

On the original table, the greedy assignment is `[0, 2, 3, 1]`, with a total of 45 minutes. Consider swapping the orders assigned to B and D:

| Assignment | B's time | D's time | Combined time |
|---|---:|---:|---:|
| B → Order 3, D → Order 2 | 17 | 17 | 34 |
| B → Order 2, D → Order 3 | 19 | 6 | 25 |

A and C keep their assignments. The new assignment is `[0, 1, 3, 2]`, with a total of **36 minutes**. B's time increases by 2 minutes, but D's decreases by 11, reducing the total by 9 minutes.

This shows that a better valid assignment exists. At this stage, I had not yet proved that 36 minutes was optimal.

## Building the PuLP model

I use PuLP 4.2.0 and build the model inside `solve_assignment_problem(travel_minutes)`:

```python
model = pulp.LpProblem("Courier_Assignment_Problem", pulp.LpMinimize)
```

For every courier–order pair, I create a decision variable with `model.add_variable(..., cat="Binary")`. I store the variables in the `X` dictionary using `(i, j)` keys. This example has 16 variables in total.

I write the objective by iterating over the dictionary keys:

```python
model += pulp.lpSum(
    travel_minutes[x[0]][x[1]] * X[x]
    for x in X
)
```

Using `print(model)`, I checked that every variable had the correct travel-time coefficient. Binary variables appear as integers bounded between 0 and 1.

I add the courier and order constraints in two separate loops:

```python
for i in range(num_couriers):
    model += pulp.lpSum(X[i, j] for j in range(num_orders)) == 1

for j in range(num_orders):
    model += pulp.lpSum(X[i, j] for i in range(num_couriers)) == 1
```

The outer loop fixes one index while the inner sum runs over the other. Four couriers and four orders give 8 assignment constraints.

## Solving with CBC

PuLP describes the model, and CBC solves it. For the Windows setup, I use the `cbcbox` package to provide CBC:

```powershell
python -m pip install "pulp==4.2.0" cbcbox
```

I solve the model with:

```python
stats = model.solve(pulp.COIN_CMD(msg=False))
```

The result was `Status: Optimal` and `Total travel time: 23.0`. CBC read the model with 8 constraints and 16 binary variables without errors.

| Method | Total travel time to the restaurants |
|---|---:|
| Greedy, processing A, B, C, D in order | 45 minutes |
| CBC solution of the PuLP model | 23 minutes |

For this synthetic table and these constraints, the optimal total is **23 minutes**, which is **22 minutes less** than the greedy result. These results apply to this small example.

## Reading the selected assignments

After solving, I read each decision variable using `pulp.value(X[i, j])`. Selecting the pairs with a value of 1 gives the optimal assignment:

```python
[1, 0, 3, 2]
```

The order indices in the list start at 0. The corresponding assignments are:

| Courier | Order | Travel time to the restaurant |
|---|---|---:|
| A | Order 2 | 5 minutes |
| B | Order 1 | 5 minutes |
| C | Order 4 | 7 minutes |
| D | Order 3 | 6 minutes |

Each courier and each order appears exactly once. The selected times add up to `5 + 5 + 7 + 6 = 23`, matching the solver's objective value.

## Running the original example (historical)

I removed the debugging prints from the calculation functions. In `main()`, I obtain the greedy and solver assignments, evaluate both with `total_travel_time`, and print the comparison.

The file ends with:

```python
if __name__ == "__main__":
    main()
```

Running the file directly starts the comparison. Importing it from another Python file does not automatically run the example.

```powershell
python assignment.py
```

Example output:

```text
=== Assignment Results ===
Total travel time in greedy search 45 minutes
Total travel time in MIP search 23 minutes
Difference is 22 minutes
```

## Checking the solver status

After solving, I check `stats.status_str` before reading the variable values. If the status is not `Optimal`, I raise a `RuntimeError` that includes the solver status.

I checked this using two couriers and one order:

```powershell
python -c "from assignment import solve_assignment_problem; solve_assignment_problem([[4], [5]])"
```

Both couriers must receive an order, but the single order can only be assigned to one courier. The constraints conflict, so the solver reports `Infeasible`. As expected, the function raises a `RuntimeError` before extracting assignments.

An infeasible model has no assignment satisfying all its constraints. That is different from a search that stops before proving optimality.

## Static exercise milestone

The original exercise established a greedy baseline, a solver model, a shared objective calculation, and a check for infeasible inputs. The project is now extending these pieces into the dynamic simulation described at the top of this README.
