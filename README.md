# Southwest-Aircraft-Routing-Optimization
A network flow-based integer programming model was built based on airport continuity and minimum turnaround time and solved using Gurobi to optimize the fleet size required to cover all non-cancelled flights of a one-day schedule of Southwest Airlines.

A network flow-based integer programming model was built to estimate the minimum fleet size required to operate a fixed schedule of Southwest Airlines flights on a selected day. A connection is feasible when the destination airport of one flight matches the origin airport of another flight and the available ground time satisfies the minimum turnaround requirement.
Gurobi then solves this model by selecting a set of feasible connections that covers every non-cancelled flight while minimizing the number of aircraft route starts, which corresponds to the minimum number of aircraft required under the assumptions.
