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
- 2359 non-cancelled Southwest flights 
* 24 overnight flights (included but treated as terminal flights for the day)
