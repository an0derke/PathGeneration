from Panel.AbstractButtons.ClickButton import ClickButton
import Utility, Graphics
from Simulation.ControllerRelated.ControllerManager import ControllerManager
from VisibleElements.Tooltip import Tooltip
from SingletonState.ReferenceFrame import PointRef
from FileInteraction.AbstractExporter import AbstractExporter
import tkinter
import tkinter.filedialog
import pygame

"""
Provides search and run functionality for exporting the path to various functionality
"""

class ExportButton(ClickButton):

    def __init__(self, exporter: AbstractExporter, position: tuple[int,int]):

        self.exporter: AbstractExporter = exporter

        self.tooltip = Tooltip("Export a "+exporter.getExtension()[1]+" file")

        imageHovered = Graphics.getImage("Images/Buttons/robot.png", 0.08)
        imageEnabled = Graphics.getImage("Images/Buttons/robot.png", 0.08)
        imageDisabled = Graphics.getLighterImage(imageEnabled, 0.33)
        super().__init__((Utility.SCREEN_SIZE+position[0], position[1]), imageDisabled, imageEnabled, imageHovered)

    # Draw export button tooltip
    def drawTooltip(self, screen: pygame.Surface, mousePosition: PointRef) -> None:
        self.tooltip.draw(screen, mousePosition)

    # No reason to disable this button
    def isDisabled(self) -> bool:
        return False


    # Runs the exporter (passed in during __init__)
    def clickEnabledButton(self) -> None:
        try:
            # Macs who try to use the tkinter module may encounter some issues. Wrapped in a try to avoid crashing
            top = tkinter.Tk()
            top.withdraw()
            #Extracts the file extension information
            fileExtension = self.exporter.getExtension()
            # Uses the tkinter module to allow the user to select a file name and location
            fileName = tkinter.filedialog.asksaveasfilename(parent=top, defaultextension=fileExtension[1], 
                filetypes=[(fileExtension[0],"*"+fileExtension[1])])
            # If no filename was set, do not export
            if fileName == "":
                return
            # Runs the exporter
            self.exporter.export(fileName)
        except:
            # Custom error message to spite Ansel
            print("We do not support Macs in this house. Sorry, but you cannot use the Exporter")