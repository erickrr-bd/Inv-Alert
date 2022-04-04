#! /usr/bin/env python3

from modules.Inv_Alert_Tool_Class import InvAlertTool

"""
Property that stores a object of InvAlertTool class.
"""
inv_alert_tool = InvAlertTool()

"""
Main function of the application
"""
if __name__ == "__main__":	
	while True:
		inv_alert_tool.mainMenu()