#! /bin/bash

# Date: 06/11/2025
# Author: Erick Roberto Rodriguez Rodriguez
# Installation script. 

# Usage: $ ./inv_alert_installer.sh

clear

# Function that prints a banner.
banner()
{
	echo "+------------------------------------------+"
  	printf "| %-40s |\n" "`date`"
  	echo "|                                          |"
  	printf "|`tput bold` %-40s `tput sgr0`|\n" "$@"
  	echo "+------------------------------------------+"
}

# Application folders and files.
BASE_DIR=/etc/Inv-Alert-Suite
INV_ALERT_CONFIGURATION=/etc/Inv-Alert-Suite/Inv-Alert/configuration
INV_ALERT_LOGS=/var/log/Inv-Alert
INV_ALERT_KEY=/etc/Inv-Alert-Suite/Inv-Alert/configuration/key
INVENTORIES_FOLDER="/etc/Inv-Alert-Suite/Inv-Alert/inventories"

# Print banner
echo -e "\e[1;33m--------------------------------------------------------------------------------\e[0m\n"
echo "
  _____                          _           _   
 |_   _|                   /\   | |         | |  
   | |  _ ____   ________ /  \  | | ___ _ __| |_ 
   | | | '_ \ \ / /______/ /\ \ | |/ _ \ '__| __|
  _| |_| | | \ V /      / ____ \| |  __/ |  | |_ 
 |_____|_| |_|\_/      /_/    \_\_|\___|_|   \__|v3.3                                          
"
echo -e "\e[1;33m--------------------------------------------------------------------------------\e[0m\n"
echo -e "[*] Author: Erick Roberto Rodriguez Rodriguez"
echo -e "[*] Email: erodriguez@tekium.mx, erickrr.tbd93@gmail.com"
echo -e "[*] GitHub: https://github.com/erickrr-bd/Inv-Alert"
echo -e "[*] Installer for Inv-Alert v3.3 - November 2025\n"

echo "Do you want to install or update Inv-Alert? (I/U)"
read opc

if [ $opc = "I" ] || [ $opc = "i" ]; then
	# "inv_alert" user and group creation.
	banner "Creating user and group"
	echo ''
	if grep -w ^inv_alert /etc/group > /dev/null; then
		echo -e "[*] \e[0;31m\"inv_alert\" already exists\e[0m"
	else
		groupadd inv_alert
		echo -e "[*] \e[0;32m\"inv_alert\" group created\e[0m"
	fi
	if id inv_alert &> /dev/null; then
		echo -e "[*] \e[0;31m\"inv_alert\" already exists\e[0m\n"
	else
		useradd -M -s /bin/nologin -g inv_alert -d /opt/Inv-Alert-Suite inv_alert
		echo -e "[*] \e[0;32m\"inv_alert\" user created\e[0m\n"
	fi
	# Copy directories and files.
	banner "Installing Inv-Alert"
	echo ''
	cp -r Inv-Alert-Suite /opt
	echo -e "[*] \e[0;32mInstallation completed\e[0m\n"
	# Creation of folders and files.
	banner "Creation of folders and files"
	echo ''
	mkdir -p $INV_ALERT_CONFIGURATION
	mkdir -p $INV_ALERT_LOGS
	mkdir -p $INVENTORIES_FOLDER
	encryption_key=$(cat /dev/urandom | head -n 30 | md5sum | head -c 30)
	cat << EOF > $INV_ALERT_KEY
$encryption_key
EOF
	echo -e "[*] \e[0;32mFolders and files created\e[0m\n"
	# Assignment of permits and owner.
	banner "Change of permissions and owner"
	echo ''
	chown inv_alert:inv_alert -R $BASE_DIR
	find $BASE_DIR -type f -exec chmod 640 {} \;
	find $BASE_DIR -type d -exec chmod 750 {} \;
	chown inv_alert:inv_alert -R /opt/Inv-Alert-Suite
	find /opt/Inv-Alert-Suite -type f -exec chmod 640 {} \;
	find /opt/Inv-Alert-Suite -type d -exec chmod 750 {} \;
	chmod +x /opt/Inv-Alert-Suite/Inv-Alert/Inv_Alert.py
	chmod +x /opt/Inv-Alert-Suite/Inv-Alert-Tool/Inv_Alert_Tool.py
	chown inv_alert:inv_alert -R $INV_ALERT_LOGS
	chmod 750 $INV_ALERT_LOGS
	echo -e "[*] \e[0;32mChanges made\e[0m\n"
	# Creation of Inv-Alert's service.
	banner "Creation of Inv-Alert's service"
	echo ''
	cp inv-alert.service /etc/systemd/system/
	systemctl daemon-reload
	systemctl enable inv-alert.service
	echo ''
	echo -e "[*] \e[0;32mService created\e[0m\n"
	# Creating aliases.
	banner "Creating aliases for Inv-Alert-Tool"
	echo ''
	echo "alias Inv-Alert-Tool='/opt/Inv-Alert-Suite/Inv-Alert-Tool/Inv_Alert_Tool.py'" >> ~/.bashrc
	echo -e "[*] \e[0;32mCreated alias\e[0m\n"
elif [ $opc = "U" ] || [ $opc = "u" ]; then
	# Stop service or daemon.
	banner "Stopping service"
	echo ''
	systemctl stop inv-alert.service
	echo -e "[*] \e[0;32mService stopped\e[0m\n"
	# Copy directories and files.
	banner "Updating Inv-Alert"
	echo ''
	cp -r Inv-Alert-Suite /opt
	echo -e "[*] \e[0;32mUpdate completed\e[0m\n"
	# Assignment of permits and owner.
	banner "Change of permissions and owner"
	echo ''
	chown inv_alert:inv_alert -R $BASE_DIR
	find $BASE_DIR -type f -exec chmod 640 {} \;
	find $BASE_DIR -type d -exec chmod 750 {} \;
	chown inv_alert:inv_alert -R /opt/Inv-Alert-Suite
	find /opt/Inv-Alert-Suite -type f -exec chmod 640 {} \;
	find /opt/Inv-Alert-Suite -type d -exec chmod 750 {} \;
	chmod +x /opt/Inv-Alert-Suite/Inv-Alert/Inv_Alert.py
	chmod +x /opt/Inv-Alert-Suite/Inv-Alert-Tool/Inv_Alert_Tool.py
	echo -e "[*] \e[0;32mChanges made\e[0m\n"
	# Start service or daemon.
	banner "Starting Inv-Alert service"
	echo ''
	systemctl start inv-alert.service
	echo -e "[*] \e[0;32mService started\e[0m\n"
else
	clear
	exit
fi