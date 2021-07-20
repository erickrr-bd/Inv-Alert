from datetime import datetime
from modules.UtilsClass import Utils

"""
"""
class Inventories:
	"""

	"""
	form_dialog = None


	utils = None

	"""
	Property that contains the options for the alert rule level.
	"""
	options_frequency_inventory = [["Daily", "Daily execution", 0]]

	"""

	"""
	def __init__(self, form_dialog):
		self.utils = Utils(form_dialog)
		self.form_dialog = form_dialog

	"""
	"""
	def createInventory(self):
		data_inventory = []
		now = datetime.now()
		name_inventory = self.form_dialog.getDataInputText("Enter the inventory name:", "inv_name")
		data_inventory.append(name_inventory)
		frequency_inventory = self.form_dialog.getDataRadioList("Select a option:", self.options_frequency_inventory, "Inventory Frequency")
		data_inventory.append(frequency_inventory)
		time_execution = self.form_dialog.getDataTime("Choose the time it will run:", now.hour, now.minute)
		data_inventory.append(str(time_execution[0]) + ':' + str(time_execution[1]))
		index_name = self.form_dialog.getDataInputText("Enter the index pattern where the inventory will be obtained:", "audit-*")
		data_inventory.append(index_name)
		field_name = self.form_dialog.getDataInputText("Enter the name of the index field which stores to the hostname:", "info.host")
		data_inventory.append(field_name)
		telegram_bot_token = self.utils.encryptAES(self.form_dialog.getDataInputText("Enter the Telegram bot token:", "751988420:AAHrzn7RXWxVQQNha0tQUzyouE5lUcPde1g"))
		telegram_chat_id = self.utils.encryptAES(self.form_dialog.getDataInputText("Enter the Telegram channel identifier:", "-1002365478941"))
		data_inventory.append(telegram_bot_token.decode('utf-8'))
		data_inventory.append(telegram_chat_id.decode('utf-8'))
		self.createFileInventory(data_inventory)
		self.form_dialog.mainMenu()

	"""
	"""
	def createFileInventory(self, data_inventory):
		data_json = {'name_inv' : data_inventory[0],
					'frequency_inv' : data_inventory[1],
					'time_execution' : data_inventory[2],
					'index_name' : data_inventory[3],
					'field_name' : data_inventory[4],
					'telegram_bot_token' : data_inventory[5],
					'telegram_chat_id' : data_inventory[6]}

		inv_folder = self.utils.getPathInvAlert(data_inventory[0])
		self.utils.createNewFolder(inv_folder)
		self.utils.createYamlFile(data_json, inv_folder + '/' + data_inventory[0] + '.yaml', 'w')