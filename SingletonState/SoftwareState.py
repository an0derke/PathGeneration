from enum import Enum

from AbstractClasses.Hoverable import Hoverable
from AbstractClasses.Draggable import Draggable


""" A class representing global state of the software."""

class Mode(Enum):
    EDIT = 1 # Modfying the path
    PLAY = 2 # Simulating the path with some path following algorithm with a virtual robot

class SoftwareState:

    def __init__(self):
        self.mode: Mode = Mode.EDIT # edit or simulation mode
        self.objectHovering: Hoverable = None # object the mouse is currently hovering over
        self.objectDragged: Draggable = None # object the mouse is currently dragging

        self.recomputeInterpolation = False # Whether to recompute bezier interpolation from modifying path

    def __str__(self):
        return "Software State:\nHovering: {}\nDragged: {}".format(self.objectHovering, self.objectDragged)

    

