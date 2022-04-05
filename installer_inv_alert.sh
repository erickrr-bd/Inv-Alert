#! /bin/bash

clear
echo -e "\e[96m@2022 Tekium. All rights reserved.\e[0m"
echo -e '\e[96mInstaller for Inv-Alert v3.1\e[0m'
echo -e '\e[96mAuthor: Erick Rodríguez\e[0m'
echo -e '\e[96mEmail: erickrr.tbd93@gmail.com, erodriguez@tekium.mx\e[0m'
echo -e '\e[96mLicense: GPLv3\e[0m'
echo -e '\e[1;33m--------------------------------------------------------------------------------\e[0m'
echo 'Do you want to install or update Inv-Alert on the computer (I/U)?'
read opc
if [ $opc = "I" ] || [ $opc = "i" ]; then
	echo ''
	echo -e '\e[96mStarting the Inv-Alert installation...\e[0m'
	echo ''
	echo 'Do you want to install the packages and libraries necessary for the operation of Inv-Alert (Y/N)?'
	read opc_lib
	if [ $opc_lib = "Y" ] || [ $opc_lib = "y" ]; then
		echo ''
		echo -e '\e[96mStarting the installation of the required packages and libraries...\e[0m'
		yum install python3-pip -y
		dnf install dialog -y
		dnf install gcc -y
		dnf install python3-devel -y
		dnf install libcurl-devel -y
		dnf install openssl-devel -y
		echo ''
		echo -e '\e[96mRequired installed libraries...\e[0m'
		sleep 3
		echo ''
	fi
	echo ''
	echo -e '\e[96mCreating user and group for Inv-Alert...\e[0m'
	groupadd inv_alert
	useradd -M -s /bin/nologin -g inv_alert -d /etc/Inv-Alert-Suite inv_alert
	echo ''
	echo -e '\e[96mUser and group created...\e[0m'
	sleep 3
	echo ''
	echo -e '\e[96mCreating the daemon for Inv-Alert...\e[0m'
	dir=$(sudo pwd)
	cd $dir
	cp inv-alert.service /etc/systemd/system/
	systemctl daemon-reload
	systemctl enable inv-alert.service
	echo ''
	echo -e '\e[96mDemon created...\e[0m'
	sleep 3
	echo ''
	echo -e '\e[96mCopying and creating the necessary files and directories...\e[0m'
	echo ''
	cp -r Inv-Alert-Suite /etc/
	mkdir /etc/Inv-Alert-Suite/Inv-Alert/configuration
	mkdir /var/log/Inv-Alert
	chown inv_alert:inv_alert -R /etc/Inv-Alert-Suite
	chown inv_alert:inv_alert -R /var/log/Inv-Alert
	echo -e '\e[96mFiles and directories created...\e[0m'
	sleep 3
	echo ''
	echo -e '\e[96mCreating passphrase...\e[0m'
	passphrase=$(cat /dev/urandom | head -n 30 | md5sum | head -c 30)
	cat << EOF > /etc/Inv-Alert-Suite/Inv-Alert/configuration/key 
$passphrase
EOF
	echo ''
	echo -e '\e[96mPassphrase created...\e[0m'
	sleep 3
	echo ''
	echo -e '\e[96mCreating aliases for Inv-Alert-Tool...\e[0m'
	alias Inv-Alert-Tool='/etc/Inv-Alert-Suite/Inv-Alert-Tool/Inv_Alert_Tool.py' >> ~/.bashrc
	echo ''
	sleep 3
	echo -e '\e[96mAliases created...\e[0m'
	echo ''
	echo -e '\e[96mInv-Alert has been installed...\e[0m'
	sleep 3	
	echo ''
	echo -e '\e[96mStarting Inv-Alert-Tool...\e[0m'
	sleep 3
	cd /etc/Inv-Alert-Suite/Inv-Alert-Tool
	python3 Inv_Alert_Tool.py
elif [ $opc = "U" ] || [ $opc = "u" ]; then
	echo ''
	echo -e '\e[96mStarting the Inv-Alert update...\e[0m'
	echo ''
	dir=$(sudo pwd)
	echo -e '\e[96mStopping and updating the Inv-Alert daemon...\e[0m'
	systemctl stop inv-alert.service
	cp inv-alert.service /etc/systemd/system/
	systemctl daemon-reload
	echo ''
	sleep 3
	echo -e '\e[96mSUpdated daemon...\e[0m'
	echo ''
	echo -e '\e[96mUpdating files and directories...\e[0m'
	echo ''
	cp -r Inv-Alert-Suite /etc/
	chown inv_alert:inv_alert -R /etc/Inv-Alert-Suite
	echo ''
	sleep 3
	echo -e '\e[96mUpdated files and directories...\e[0m'
	echo ''
	echo -e '\e[96mCreating aliases for Inv-Alert-Tool...\e[0m'
	alias Inv-Alert-Tool='/etc/Inv-Alert-Suite/Inv-Alert-Tool/Inv_Alert_Tool.py' >> ~/.bashrc
	echo ''
	sleep 3
	echo -e '\e[96mAliases created...\e[0m'
	echo ''
	echo -e '\e[96mInv-Alert updated...\e[0m'
	echo ''
	echo -e '\e[96mStarting Inv-Alert-Tool...\e[0m'
	sleep 5
	cd /etc/Inv-Alert-Suite/Inv-Alert-Tool
	python3 Inv_Alert_Tool.py
else
	clear
	exit
fi