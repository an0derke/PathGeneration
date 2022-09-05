
from pathlib import Path
from SingletonState.FieldTransform import FieldTransform
from SingletonState.ReferenceFrame import PointRef, Ref
from VisibleElements.PathPoint import PathPoint
from VisibleElements.ControlPoint import ControlPoint
from VisibleElements.PathSegment import PathSegment
import Utility, pygame


"""Store the full path of the robot. This consists of a list of PathPoint objects, as well as the interpolatedPoint objects
that would be generated as a bezier curve through all the PathPoints. The interpolatedPoints array will be recalculated at each
PathPoint change."""

class FullPath:

    def __init__(self, transform: FieldTransform):
        self.transform = transform
        self.pathPoints: list[PathPoint] = [] # The user-defined points
        self.segments: list[PathSegment] = []
        self.interpolatedPoints: list[PointRef] = [] # the beizer-interpolated points generated from the user-defined points

    # Return the location of the shadow PathPoint where the mouse is.
    # This is exactly equal to the location of the mouse if the mouse is not hovering on a segment,
    # but if the mouse is near a segment the shadow will "snap" to it
    def getShadowPosition(self, mousePosition: PointRef):

        return mousePosition # temporary

    # Given a segment object, find its location in self.segments and return its index
    def getSegmentIndex(self, segment: PathSegment):
        index = 0
        for s in self.segments:
            if segment is s:
                return index
            index += 1
        return -1

    # Append a PathPoint at at the specified position.
    # A segment will also need to be inserted somewhere.
    def createPathPoint(self, position: PointRef, index: int = -1):

        if index == -1:
            index = len(self.pathPoints)

        newPoint = PathPoint(position.copy())
        self.pathPoints.insert(index, newPoint)

        if len(self.pathPoints) == 1: # no segment
            return
        elif index == len(self.pathPoints) - 1: # added a node at the end, so segment links last two nodes
            self.segments.append(PathSegment(self.pathPoints[-2], self.pathPoints[-1]))
        else: # added a node between two segments
            self.segments[index-1].pointB = newPoint
            self.segments.insert(index, PathSegment(newPoint, self.pathPoints[index+1]))
        

    # Draw a segment from each path to the next. This will be drawn under the points themselves
    def drawPathSegments(self, screen: pygame.Surface):
        
        for segment in self.segments:
            segment.draw(screen)

    # Iterate through each PathPoint and draw it
    def drawPathPoints(self, screen: pygame.Surface):
        index = 0
        for pathPoint in self.pathPoints:
            
            # draw line that goes from control to path point
            pathPoint.controlA.drawOwnershipLine(screen)
            pathPoint.controlB.drawOwnershipLine(screen)

            # Draw the path point itself
            pathPoint.draw(screen, index)

            # Then draw the control point on top
            pathPoint.controlA.draw(screen)
            pathPoint.controlB.draw(screen)
            index += 1

    # Draw the path on the screen, including the user-defined points, interpolated points, and segments
    def draw(self, screen: pygame.Surface):
        self.drawPathSegments(screen)
        self.drawPathPoints(screen)
    