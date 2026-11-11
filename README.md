# Courier Assignment Lab

I built this small project to learn how to turn an assignment problem into a mathematical model and solve it with PuLP and CBC. I compare a simple greedy approach with a binary integer programming model using synthetic travel times.

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

## Running the example

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

## Current progress

I have implemented the greedy and solver approaches, separated calculations from output, and compared both methods using the same travel-time function. I have run the normal example and checked the error handling on an infeasible input. The next step is to record the dependencies and finish preparing the repository for sharing.
