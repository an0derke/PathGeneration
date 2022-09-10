from SingletonState.ReferenceFrame import PointRef

"""
Essentially a glorified list of list of PointRefs.
The list of PointRefs are a set of waypoints that are calculated by PointRefs
Between each set of waypoints is a point turn
"""

class Waypoints:

    def __init__(self):
        self.reset()

    # Clear the entire list of waypoints
    def reset(self):
        self.waypoints = [[]]

    # Whenever a new waypoint is calculated, append it to the last set of waypoints
    def addWaypoint(self, waypoint: PointRef):
        self.waypoints[-1].append(waypoint)

    # This happens when we reach a "Sharp" PathPoint. In this case, we want a point turn to happen
    # We store this by adding a new element to waypoints
    # The actual amount to turn is calculated later
    def addPointTurn(self):
        self.waypoints.append([])

    # Return an iterator through every single waypoint
    def iterator(self):

        for segment in self.waypoints:
            for waypoint in segment:
                yield waypoint

        # Weird python quirk to return empty iterator if self.waypoints is empty
        return
        yield