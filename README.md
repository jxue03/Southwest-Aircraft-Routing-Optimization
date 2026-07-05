# Southwest-Aircraft-Routing-Optimization
A network flow-based integer programming model was built to estimate the minimum fleet size required to operate a fixed schedule of Southwest Airlines flights on a selected day (1/25/2026). A connection is feasible when the destination airport of one flight matches the origin airport of another flight and the available ground time satisfies the minimum turnaround requirement.
Gurobi then solves this model by selecting a set of feasible connections that covers every non-cancelled flight while minimizing the number of aircraft route starts, which corresponds to the minimum number of aircraft required under the assumptions.

## Dataset
The data comes from the Bureau of Transportation Statistics, U.S. Department of Transportation. The dataset contains Southwest Airlines flight records for January 2026.

| Column | Description |
|---|---|
| `FL_DATE` | Flight date |
| `TAIL_NUM` | Aircraft tail number used in the original dataset |
| `OP_CARRIER_FL_NUM` | Southwest flight number |
| `ORIGIN` | Departure airport |
| `DEST` | Arrival airport |
| `CRS_DEP_TIME` | Scheduled departure time |
| `CRS_ARR_TIME` | Scheduled arrival time |
| `CRS_ELAPSED_TIME` | Scheduled elapsed flight time in minutes |
| `DISTANCE` | Flight distance in miles |
| `CANCELLED` | Cancellation indicator |

After filtering, the model uses:
- 2359 non-cancelled Southwest flights including 24 overnight flights (but treated as terminal flights for the day).

## Integer Programming Model
The model is formulated as a minimum path cover problem on a directed flight network. The list `edges` stores all feasible aircraft connections between flights. Each edge is represented as `(i, j, wait_time)`, where flight `j` can be operated after flight `i` by the same aircraft.

A feasible edge is created only when the destination airport of flight `i` matches the origin airport of flight `j`, and the available ground time is at least the required minimum turnaround time:   

DEST_i = ORIGIN_j   
DEP_j - ARR_i >= MIN_TURN   

Overnight flights are treated as terminal flights in the one-day model, so no outgoing edges are created from those flights.   
The model uses two sets of binary decision variables. For each feasible edge (i, j) in edges, the variable x[i,j] indicates whether that connection is selected:   
x[i,j] = 1 if flight j is assigned immediately after flight i on the same aircraft   
x[i,j] = 0 otherwise   

For each flight i, the variable start[i] indicates whether flight i begins a new aircraft route:   
start[i] = 1 if flight i starts a new aircraft route   
start[i] = 0 otherwise   

The objective is to minimize the number of aircraft required. Since each aircraft route has one starting flight, minimizing the total number of route starts minimizes the required aircraft count:   
minimize sum(start[i] for all flights i)   

Each flight must either start a new aircraft route or have exactly one selected predecessor flight:   
start[i] + sum(x[j,i] for all feasible predecessor flights j) = 1   
This ensures that every flight is covered exactly once.   

Each flight can have at most one selected successor flight:   
sum(x[i,j] for all feasible successor flights j) <= 1   
This prevents one aircraft from being assigned to multiple next flights.   

Together, these constraints form aircraft routes through the feasible connection network. After optimization, the selected x[i,j] variables are used to reconstruct each aircraft route, and the number of selected start[i] variables gives the minimum number of aircraft required under the stated assumptions.


## Results
The optimization was solved using Gurobi with a time limit of 10 seconds and a MIP gap of 0. For each turnaround-time scenario, Gurobi found an optimal solution with a 0.0000% optimality gap.

| Minimum Turnaround Time | Feasible Connection Pairs | Optimized Aircraft Required | Selected Connections | Aircraft Saved vs. Actual | Percent Reduction |
|---:|---:|---:|---:|---:|---:|
| 35 minutes | 80,981 | 552 | 1,807 | 87 | 13.6% |
| 40 minutes | 79,923 | 589 | 1,770 | 50 | 7.8% |
| 45 minutes | 78,349 | 623 | 1,736 | 16 | 2.5% |

The results show that the minimum aircraft requirement increases as the turnaround-time requirement becomes stricter. 

This pattern is expected because longer turnaround requirements reduce the number of feasible flight connections. As fewer flight pairs can be connected, more aircraft route starts are needed to cover all flights. Even under the most conservative tested assumption of 45 minutes, the optimized fleet size remains below the actual number of aircraft observed in the data, which is 639.

Overall, the results suggest that the January 25 schedule contains substantial connection flexibility under the model assumptions. The optimized aircraft count should be interpreted as a theoretical minimum fleet requirement for the selected day, rather than a direct replacement for Southwest's actual aircraft assignment, since the model does not include crew scheduling, maintenance, aircraft capacity, gate availability, or multi-day positioning constraints.

