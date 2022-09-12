from Panel.TabButtons import AIButton, EditButton, OdomButton, RobotButton, SimulateButton
from Panel.AbstractButtons.AbstractButton import AbstactButton
from Panel import AbstractTab, AITab, EditTab, OdomTab, RobotTab, SimulationTab
from SingletonState.SoftwareState import SoftwareState, Mode
from VisibleElements.FullPath import FullPath
from MouseInterfaces.Hoverable import Hoverable
from Simulation.ControllerManager import ControllerManager
import pygame
from typing import Iterator

"""
A class that handles all the stuff that's drawon on the panel to the right of the vex field
Stores all the Tab objects and draws all the UI from the selected Tab onto the screen
"""

class Panel:

    def __init__(self, state: SoftwareState, path: FullPath, controllers: ControllerManager):

        self.state: SoftwareState = state
        
        self.tabButtons: list[AbstactButton] = [
            
            AIButton.AIButton(state),
            EditButton.EditButton(state),
            SimulateButton.SimulateButton(state, path.waypoints),
            RobotButton.RobotButton(state, path.waypoints),
            OdomButton.OdomButton(state)
        ]

        self.aiTab: AITab.AITab = AITab.AITab()
        self.editTab: EditTab.EditTab = EditTab.EditTab()
        self.simulationTab: SimulationTab.SimulationTab = SimulationTab.SimulationTab(controllers)
        self.robotTab: RobotTab.RobotTab = RobotTab.RobotTab(controllers)
        self.odomTab: OdomTab.OdomTab = OdomTab.OdomTab()

    # Given the mode, get the tab oject associated with that mode
    def getTab(self, mode: Mode) -> AbstractTab.AbstractTab:
        if mode == Mode.AI:
            return self.aiTab
        elif mode == Mode.EDIT:
            return self.editTab
        elif mode == Mode.SIMULATE:
            return self.simulationTab
        elif mode == Mode.ROBOT:
            return self.robotTab
        else:
            return self.odomTab

    # Returns a generator of all the hoverable objects for the panel
    def getHoverables(self) -> Iterator[Hoverable]:

        # Yield each tab button
        for tabButton in self.tabButtons:
            yield tabButton
        
        # yield each ui object that would appear in the selected panel tab
        for uiObject in self.getTab(self.state.mode).getHoverables():
            yield uiObject

    # Draw the panel buttons and all the ui objects that would appear in the seleced tab
    def draw(self, screen: pygame.Surface):
        # draw the tab buttons
        for button in self.tabButtons:
            button.draw(screen)

        # draw the ui objects that would appear in the selected panel tab
        self.getTab(self.state.mode).draw(screen)