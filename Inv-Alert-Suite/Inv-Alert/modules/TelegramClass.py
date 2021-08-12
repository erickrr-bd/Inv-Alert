from io import StringIO
from time import strftime
from modules.UtilsClass import Utils
from pycurl import Curl, RESPONSE_CODE, FORM_FILE

"""
Class that manages everything related to Telegram.
"""
class Telegram:
	"""
	Property that stores an object of type Utils.
	"""
	utils = None

	"""
	Constructor for the Telegram class.

	Parameters:
	self -- An instantiated object of the Telegram class.
	"""
	def __init__(self):
		self.utils = Utils()

	"""
	Method that sends a message to a Telegram channel with
	text and an attachment.

	Parameters:
	self -- An instantiated object of the Telegram class.
	telegram_chat_id -- Telegram channel identifier. 
	telegram_bot_token -- Telegram bot token.
	message_telegram -- Message that will be sent to the
						Telegram channel.
	file_attached -- Path of the file that will be attached
					 to the telegram channel.

	Return:
	HTTP Response code.
	"""
	def sendTelegramAlert(self, telegram_chat_id, telegram_bot_token, message_telegram, file_attached):
		url = "https://api.telegram.org/bot" + str(telegram_bot_token) + '/'
		data_telegram = [("chat_id", telegram_chat_id), ('document', (FORM_FILE, file_attached))]
		data_telegram.append(("caption", message_telegram))
		c = Curl()
		storage = StringIO()
		c.setopt(c.URL, url + 'sendDocument')
		c.setopt(c.HTTPPOST, data_telegram)
		c.perform_rs()
		return c.getinfo(RESPONSE_CODE)

	"""
	Method that generates the message that will be sent in
	the alert to Telegram.

	Parameters:
	self -- An instantiated object of the Telegram class.
	list_hosts_added -- List of hosts added.
	list_hosts_removed -- List of hosts removed.
	list_hosts_final -- Final host list.
	name_inv -- Inventory name.

	Return:
	message -- Message formed to be sent.
	"""
	def getTelegramMessage(self, list_hosts_added, list_hosts_removed, list_hosts_final, name_inv):
		message = "" + u'\u26A0\uFE0F' + " " + name_inv +  " " + u'\u26A0\uFE0F' + '\n\n' + u'\u23F0' + " Alert sent: " + strftime("%c") + "\n\n"
		message += u'\u270F\uFE0F' + " Total hosts added: " + str(len(list_hosts_added)) + '\n\n'
		if len(list_hosts_added) > 0:
			for host_to_add in list_hosts_added:
				message += u'\u2611\uFE0F' + ' ' + host_to_add + '\n'
		message += '\n' + u'\u270F\uFE0F' + " Total hosts removed: " + str(len(list_hosts_removed)) + '\n\n'
		if len(list_hosts_removed) > 0:
			for host_to_remove in list_hosts_removed:
				message += u'\u2611\uFE0F' + ' ' + host_to_remove + '\n'
		message += '\n\n' + "TOTAL HOSTS: " + str(len(list_hosts_final))
		if len(message) > 4096:
			message = u'\u26A0\uFE0F' + " " + name_inv +  " " + u'\u26A0\uFE0F' + u'\u23F0' + " Alert sent: " + strftime("%c") + "\n\n\n"
			message += u'\u270F\uFE0F' + " Total hosts added: " + str(len(list_hosts_added))
			message += u'\u270F\uFE0F' + " Total hosts removed: " + str(len(list_hosts_removed))
			message += "Total hosts: " + str(len(list_hosts_final))
		return message.encode('utf-8')

	"""
	Method that prints in the application log and on the
	screen the status of the alert sent to Telegram, when
	obtaining the inventory.

	Parameters:
	self -- An instantiated object of the Telegram class.
	telegram_response_code -- HTTP response code.
	name_inv -- Inventory name.
	"""
	def getStatusbyResponseCode(self, telegram_response_code, name_inv):
		if telegram_response_code == 200:
			self.utils.createInvAlertLog("Inventory: " + name_inv + ", Status: Telegram sent.", 1)
			print("\nInventory: " + name_inv + ", Status: Telegram sent.")
		elif telegram_response_code == 400:
			self.utils.createInvAlertLog("Inventory: " + name_inv + ", Status: Bad request.", 2)
			print("\nInventory: " + name_inv + ", Status: Bad request.")
		elif telegram_response_code == 401:
			self.utils.createInvAlertLog("Inventory: " + name_inv + ", Status: Unauthorized.", 2)
			print("\nInventory: " + name_inv + ", Status: Unauthorized.")
		elif telegram_response_code == 404:
			self.utils.createInvAlertLog("Inventory: " + name_inv + ", Status: Not found.", 2)
			print("\nInventory: " + name_inv + ", Status: Not found.")