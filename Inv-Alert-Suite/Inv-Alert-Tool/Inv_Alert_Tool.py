#! /usr/bin/env python3.12

"""
Main function.
"""
from modules.Inv_Alert_Tool_Class import InvAlertTool

if __name__ == "__main__":
	inv_alert_tool = InvAlertTool()
	while True:
		inv_alert_tool.main_menu()
