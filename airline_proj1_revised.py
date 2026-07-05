# ==================================================
# Aircraft Routing Assignment Optimization
# ==================================================

from bisect import bisect_left
import pandas as pd
from gurobipy import GRB, Model, quicksum


CSV_PATH = r"C:\Users\Jenny\Downloads\airlineproject1\WN_2026JAN.csv"
FLIGHT_DATE = pd.Timestamp("2026-01-25")
MIN_TURN = 35


def time_to_minutes(t):
    t = int(t)
    hour = t // 100
    minute = t % 100
    return 60 * hour + minute


def load_flights():
    df = pd.read_csv(CSV_PATH)
    df["FL_DATE"] = pd.to_datetime(df["FL_DATE"])

    flights = df[(df["FL_DATE"] == FLIGHT_DATE) & (df["CANCELLED"] == 0)].copy()
    flights = flights[
        [
            "TAIL_NUM",
            "OP_CARRIER_FL_NUM",
            "ORIGIN",
            "DEST",
            "CRS_DEP_TIME",
            "CRS_ARR_TIME",
            "CRS_ELAPSED_TIME",
            "DISTANCE",
        ]
    ].copy()

    flights["DEP_MIN"] = flights["CRS_DEP_TIME"].apply(time_to_minutes)
    flights["ARR_MIN"] = flights["CRS_ARR_TIME"].apply(time_to_minutes)

    # For this one-day model, overnight flight can have a predecessor, but not a successor.
    flights["IS_OVERNIGHT"] = (
        (flights["DEP_MIN"] >= 17 * 60)
        & (flights["ARR_MIN"] <= 8 * 60)
    )

    # sorting by the earliest departure first; 
    # if departure time ties, earlier arrival first; 
    # if still tied, sort by origin airport alphabetically; 
    # if still tied, sort by destination airport alphabetically; 
    # if still tied, sort by flight number
    flights.sort_values(
        ["DEP_MIN", "ARR_MIN", "ORIGIN", "DEST", "OP_CARRIER_FL_NUM"],
        inplace=True,
    )
    flights.reset_index(drop=True, inplace=True)
    flights["FLIGHT_ID"] = flights.index

    return flights


def build_feasible_connections(flights):
    # Creates an empty dictionary to store departures by airport. 
    # For every flight, put it into a group based on its origin airport. Sorts each airport’s departure list by time.
    departure_groups = {}

    for idx, row in flights.iterrows():
        departure_groups.setdefault(row["ORIGIN"], []).append((row["DEP_MIN"], idx))

    for departures in departure_groups.values():
        departures.sort()

    edges = []

    for i, row in flights.iterrows():
        # Overnight flights are terminal flights in this one-day model.
        # They may be reached by a previous flight, but cannot connect onward.
        if row["IS_OVERNIGHT"]:
            continue

        # find all flights that can happen after the current flight using the same aircraft.
        departures = departure_groups.get(row["DEST"], [])
        dep_times = [dep_time for dep_time, _ in departures]
        earliest_departure = row["ARR_MIN"] + MIN_TURN
        # This loops over all possible next flights starting from that first feasible departure.
        pos = bisect_left(dep_times, earliest_departure)

        for dep_time, j in departures[pos:]:
            wait_time = dep_time - row["ARR_MIN"]
            edges.append((i, j, wait_time)) # This saves a feasible connections.

    return edges


def solve_min_aircraft(flights, edges):
    model = Model("Southwest_Minimum_Aircraft_JAN25th")
    model.Params.TimeLimit = 30
    model.Params.MIPGap = 0.0


    # This creates one binary variable for each flight.
    # start[i] = 1 if flight i is the first flight of a new aircraft route
    # start[i] = 0 if flight i has a previous flight before it
    # The objective minimizes the number of starts, because each route start represents one aircraft needed.
    flight_ids = range(len(flights))
    x = model.addVars([(i, j) for i, j, _ in edges], vtype=GRB.BINARY, name="connect")
    start = model.addVars(flight_ids, vtype=GRB.BINARY, name="start")
    
    # creates a dictionary to store possible predecessor flights.
    incoming = {i: [] for i in flight_ids}
    # This creates a dictionary to store possible successor flights.
    outgoing = {i: [] for i in flight_ids}

    for i, j, _ in edges:
        outgoing[i].append(j)
        incoming[j].append(i)

    for i in flight_ids:
        model.addConstr(
            # every flight must "either starts a new aircraft route" or "it has exactly one previous flight".
            start[i] + quicksum(x[j, i] for j in incoming[i]) == 1,
            name=f"one_predecessor_or_start_{i}",
        )
        model.addConstr(
            # every flight can be followed by at most one next flight.
            quicksum(x[i, j] for j in outgoing[i]) <= 1,
            name=f"at_most_one_successor_{i}",
        )

    model.setObjective(quicksum(start[i] for i in flight_ids), GRB.MINIMIZE)
    model.optimize()

    selected_connections = [(i, j) for i, j, _ in edges if x[i, j].X > 0.5]
    start_flights = [i for i in flight_ids if start[i].X > 0.5]

    return model, start_flights, selected_connections


def build_routes(start_flights, selected_connections):
    next_flight = {i: j for i, j in selected_connections}
    routes = []

    for aircraft_id, start in enumerate(start_flights, start=1):
        current = start
        sequence = 1

        while current in next_flight:
            routes.append((aircraft_id, sequence, current))
            current = next_flight[current]
            sequence += 1

        routes.append((aircraft_id, sequence, current))
    # create a readable table showing the optimized route for each aircraft
    return pd.DataFrame(routes, columns=["AIRCRAFT_ID", "SEQUENCE", "FLIGHT_ID"])


def main():
    flights = load_flights()
    edges = build_feasible_connections(flights)
    model, start_flights, selected_connections = solve_min_aircraft(flights, edges)

    if model.Status not in (GRB.OPTIMAL, GRB.TIME_LIMIT):
        print(f"Model ended with Gurobi status {model.Status}")
        return

    routes = build_routes(start_flights, selected_connections)
    route_output = routes.merge(flights, on="FLIGHT_ID", how="left")
    route_output.to_csv(
    r"C:\Users\Jenny\Downloads\airlineproject1\SW_optimized_routes_2026_01_25.csv",
    index=False
    )

    print(f"Flights kept: {len(flights)}")
    print("Cancelled flights removed: yes")
    print(f"Overnight flights kept: {int(flights['IS_OVERNIGHT'].sum())}")
    print(f"Actual tail numbers in data: {flights['TAIL_NUM'].nunique()}")
    print(f"Feasible connection pairs: {len(edges)}")
    print(f"Minimum aircraft needed with {MIN_TURN}-minute turns: {model.ObjVal:.0f}")
    print(f"Selected connections: {len(selected_connections)}")
    print("Route assignment saved to airproject1/southwest_routes_2026_01_25.csv")


if __name__ == "__main__":
    main()
