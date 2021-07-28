#! /usr/bin/env python3

from modules.InventoriesClass import Inventories

"""
	Property that stores an object of type Inventories.
	"""
inventories = Inventories()

"""
Main function of the application.
"""
if __name__ == "__main__":
	inventories.loadAllInventories()