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
The model is formulated as a minimum path cover problem on a directed flight network.
The decision variables are:
x[i,j] = 1 if flight j is operated immediately after flight i by the same aircraft
x[i,j] = 0 otherwise
and:
start[i] = 1 if flight i is the first flight of an aircraft route
start[i] = 0 otherwise
The objective is to minimize the number of aircraft used. Since each aircraft route has exactly one first flight, minimizing the number of route starts is equivalent to minimizing the number of aircraft:
Minimize sum(start[i])
The first major constraint ensures that every flight is either the first flight of an aircraft route or has exactly one predecessor flight:
start[i] + sum(x[j,i]) = 1
This guarantees that every flight is covered exactly once.
The second major constraint ensures that each flight has at most one successor:
sum(x[i,j]) <= 1
This prevents one aircraft from splitting into multiple routes.

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

