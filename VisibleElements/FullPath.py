from SingletonState.ReferenceFrame import PointRef, Ref
from SingletonState.SoftwareState import SoftwareState, Mode
from VisibleElements.PathPoint import PathPoint, Shape
from VisibleElements.PathSegment import PathSegment
from Simulation.InterpolatedPoints import InterpolatedPoints
import BezierCurves, Utility, colors, pygame, Graphics


"""Store the full path of the robot. This consists of a list of PathPoint objects, as well as the interpolatedPoint objects
that would be generated as a bezier curve through all the PathPoints. The interpolatedPoints array will be recalculated at each
PathPoint change."""

class FullPath:

    def __init__(self):
        self.pathPoints: list[PathPoint] = [] # The user-defined points
        self.segments: list[PathSegment] = []
        self.waypoints: InterpolatedPoints = InterpolatedPoints()

        self.INTERPOLATED_POINT_DISTANCE = 0.75 # distance in inches between each interpolated bezier point

    # Append a PathPoint at at the specified position.
    # Index = -1 means that we'll add it at the end
    # A segment will also need to be inserted somewhere.
    def createPathPoint(self, position: PointRef, index: int = -1):

        # Passing an index of -1 indicates we're trying to add to the end
        if index == -1:
            index = len(self.pathPoints)

        if index == 1:
            # Set vector to be the inverse of the vector to the previous vector
            vectorAwayFromPrev = (position - self.pathPoints[index-1].position).normalize()
            controlVector = (vectorAwayFromPrev * 10).fieldRef

        elif index > 1:
            # Set vector to be the sum of the inverses to the previous two vectors
            vectorAwayFromPrev = (position - self.pathPoints[index-1].position).normalize()
            vectorAwayFromPrev2 = (position - self.pathPoints[index-2].position).normalize()
            controlVector = ((vectorAwayFromPrev - vectorAwayFromPrev2).normalize() * 10).fieldRef
        else: # index == 0
            controlVector = (3,3)

        newPoint = PathPoint(position.copy(), controlVector)

        self.pathPoints.insert(index, newPoint)

        if len(self.pathPoints) == 1: # no segment
            return
        elif index == len(self.pathPoints) - 1: # added a node at the end, so segment links last two nodes
            self.segments.append(PathSegment(self.pathPoints[-2], self.pathPoints[-1]))
        else: # added a node between two segments
            self.segments[index-1].pointB = newPoint
            self.segments.insert(index, PathSegment(newPoint, self.pathPoints[index+1]))

    # Delete a path point given the point object. Finds and deeltes the segment as well
    def deletePathPoint(self, point: PathPoint):
        
        index = self.pathPoints.index(point)
        del self.pathPoints[index]
        
        if len(self.segments) == 0: # don't delete anything if no segments
            pass
        elif index == 0: # deleting first item, easiest case and just delete first segment as well
            del self.segments[0]
        elif index == len(self.pathPoints): # deleting last item, just delete last segment
            del self.segments[-1]
        else: # delete some intermediate item, need to merge two segments together
            self.segments[index-1].pointB = self.segments[index].pointB
            del self.segments[index]

    
    # Interpolate between two given PathPoints and their ControlPoints using bezier spline curve
    def interpolateSplineCurve(self, point1: PathPoint, point2: PathPoint, spillover: float) -> int:

        P1 = point1.position.fieldRef
        V1 = point1.controlA.vector.fieldRef
        P2 = point2.position.fieldRef
        V2 = point2.controlB.vector.fieldRef
        
        if spillover == 0:
            ns = 0
        else:
            dxds,dyds = BezierCurves.getBezierGradient(0, P1, [V1[0], V1[1]], [V2[0], V2[1]], P2)
            dsdt = spillover / Utility.hypo(dxds, dyds)
            ns = dsdt # s normalized from 0 to 1 for this specific spline
            if ns > 1:
                return ns - 1 # no points on this spline segment

        while ns < 1:
            x, y = BezierCurves.getBezierPoint(ns, P1, [V1[0], V1[1]], [V2[0], V2[1]], P2)
            self.waypoints.addPoint(PointRef(Ref.FIELD, (x,y)))

            dxds, dyds = BezierCurves.getBezierGradient(ns, P1, [V1[0], V1[1]], [V2[0], V2[1]], P2)
            dsdt = self.INTERPOLATED_POINT_DISTANCE / Utility.hypo(dxds, dyds)
            ns += dsdt

        spillover = self.INTERPOLATED_POINT_DISTANCE - Utility.distance(x,y,*P2)
        return spillover


    # Based on the location of the PathPoint and ControlPoints, recalculate the beizer curve points
    def calculateInterpolatedPoints(self):

        # Reset the list
        self.waypoints.reset()

        # Nothing to interpolate if there aren't at least two PathPoints
        if len(self.pathPoints) < 2:
            return

        spillover = 0 # the distance before the first interpolated point, spilled over from the previous curve
        for i in range(len(self.pathPoints) - 1):

            # If the two pathpoints are practically in the same location (<0.1 inches), ignore the pathpoint
            if (self.pathPoints[i+1].position - self.pathPoints[i].position).magnitude(Ref.FIELD) < 0.1:
                continue

            # Actually interpolate between these two points
            spillover = self.interpolateSplineCurve(self.pathPoints[i], self.pathPoints[i+1], spillover)

            # If the PathPoint is sharp, do not spillover to the next path
            # Also, add a point turn
            if self.pathPoints[i+1].shape == Shape.SHARP:
                spillover = 0
                self.waypoints.addPointTurn()



    # Draw a segment from each path to the next. This will be drawn under the points themselves
    def drawPathSegments(self, screen: pygame.Surface):
        
        for segment in self.segments:
            segment.draw(screen)

    # Iterate through each PathPoint and draw it
    def drawPathPoints(self, screen: pygame.Surface, drawControl: bool):
        index = 0
        for pathPoint in self.pathPoints:
            
            if drawControl:
                # draw line that goes from control to path point
                pathPoint.controlA.drawOwnershipLine(screen)
                pathPoint.controlB.drawOwnershipLine(screen)

            # Draw the path point itself
            pathPoint.draw(screen, index)

            # Then draw the control point on top
            if drawControl:
                pathPoint.controlA.draw(screen)
                pathPoint.controlB.draw(screen)
            
            index += 1

    # Draw all the interpolated points that have been calculated from PathPoint and ControlPoints
    def drawInterpolatedPoints(self, screen: pygame.Surface):

        radius = 2
        
        for point in self.waypoints.iterator(): # point is a PointRef
            Graphics.drawCircle(screen, *point.screenRef, colors.RED, radius)

    # Draw the path on the screen, including the user-defined points, interpolated points, and segments
    def draw(self, screen: pygame.Surface, state: SoftwareState):
        
        # Draw ControlPoints only in Edit mode
        drawControl = (state.mode == Mode.EDIT)

        # Pointless for segments to be shown in PLAY mode, so draw only in Edit mode
        if drawControl:
            self.drawPathSegments(screen)
        
        self.drawInterpolatedPoints(screen)
        self.drawPathPoints(screen, drawControl)
    