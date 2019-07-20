
#!/usr/bin/python
# -*- coding: ascii -*-
# $Id$
#
# Author:  Janitz
# Date:	   July 2019

__author__ = "Janitz"
__email__  = "janis-d@web.de"  #<<< here put an email where plugins users can contact you

#Here import the libraries you need, these are necessary to modify the code  
from CNC import CNC,Block
from ToolsPage import Plugin

#==============================================================================
# My plugin
#==============================================================================
class Tool(Plugin):
	# WARNING the __doc__ is needed to allow the string to be internationalized
	__doc__ = _("Create a spiral pool path")				#<<< This comment will be show as tooltip for the ribbon button
	def __init__(self, master):
		Plugin.__init__(self, master,"Spiral")
		#MYPlugin: is the name of the plugin show in the tool ribbon button
		self.icon = "spiral"			#<<< This is the name of gif file used as icon for the ribbon button. It will be search in the "icons" subfolder
		self.group = "CAM"	#<<< This is the name of group that plugin belongs
		#Here we are creating the widgets presented to the user inside the plugin
		#Name, Type , Default value, Description
		self.variables = [			#<<< Define a list of components for the GUI
			("name" , "db"   , ""    , _("Name")),			#used to store plugin settings in the internal database
			("Size" , "mm"   , 100.0 , _("Diameter")),		#a variable that will be converted in mm/inch based on bCNC settting
			("Rot"  , "int"  , 10    , _("Rotations")),		#an integer variable
			("CW"   , "bool" , True  , _("Clockwise"))		#a true/false check box
		]
		self.buttons.append("exe")  #<<< This is the button added at top to call the execute method below

	# ----------------------------------------------------------------------
	# This method is executed when user presses the plugin execute button 
	# ----------------------------------------------------------------------
	def execute(self, app):
		name = self["name"]
		if not name or name=="default": name="Spiral"
		
		#Retrive data from user imput
		Size = self.fromMm("Size")
		Rotation = self["Rot"]
		CW = self["CW"]

		#grwoth per arc
		if Rotation <= 0: Rotation = 1
		grow = Size / Rotation / 4

		#Clockwise
		g = 2 if CW else 3

		#Initialize blocks that will contain our gCode
		blocks = []
		block = Block(name)
		
		#use some useful bCNC functions to generate gCode movement, see CNC.py for more

		block.append("G0 Z3")			#<<< Move rapid Z axis to the safe height in Stock Material
		block.append("G0 X0 Y0")		#<<< Move rapid to X and Y coordinate
		block.append("G1 Z0 F100")		#<<< Enter in the material with Plunge Feed for current material
		block.append("F600")			#<<< Feedrate
		x, y = 0, 0
		while abs(x) < Size / 2:
			lx = x					#<<< Save last x value
			x = abs(x) + grow		#<<< Add the growing value
			if lx >= 0: x = -x		#<<< Alternate sign
			dx = x - lx				#<<< Calculate delta X (r = i = dx/2)
			block.append(CNC.garc(g=g, x = x, i = dx / 2))

		#Circle with final Size
		block.append(CNC.garc(g=g, x = -x, i = -x))
		block.append(CNC.garc(g=g, x = x, i = x))
		

		blocks.append(block)
		active = app.activeBlock()
		app.gcode.insBlocks(active, blocks, "MyPlugins inserted")	#<<< insert blocks over active block in the editor
		app.refresh()												#<<< refresh editor
		app.setStatus(_("Generated: Spiral"))						#<<< feed back result

