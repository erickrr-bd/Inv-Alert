#! /bin/bash

clear
echo -e "\e[96m@2021 Tekium. All rights reserved.\e[0m"
echo ''
echo -e '\e[96mInstaller for Telk-Alert v3.0\e[0m'
echo ''
echo -e '\e[96mAuthor: Erick Rodríguez erickrr.tbd93@gmail.com\e[0m'
echo ''
echo -e '\e[96mLicense: GPLv3\e[0m'
echo ''
echo -e '\e[1;33m--------------------------------------------------------------------------------\e[0m'
echo ''
echo 'Do you want to install or update Telk-Alert on the computer (I/U)?'
read opc
if [ $opc = "I" ] || [ $opc = "i" ]; then
	echo -e '\e[96mStarting the Telk-Alert installation...\e[0m'
	echo ''
	echo 'Do you want to install the packages and libraries necessary for the operation of Telk-Alert (Y/N)?'
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
		pip3 install pythondialog 
		pip3 install pycryptodome
		pip3 install pyyaml 
		pip3 install pycurl 
		pip3 install elasticsearch-dsl 
		pip3 install requests 
		echo ''
		echo -e '\e[96mRequired installed libraries...\e[0m'
		sleep 3
		echo ''
	fi
	echo -e '\e[96mCreating user and group for Telk-Alert...\e[0m'
	groupadd telk_alert
	useradd -M -s /bin/nologin -g telk_alert -d /etc/Telk-Alert-Suite telk_alert
	echo ''
	echo -e '\e[96mUser and group created...\e[0m'
	sleep 3
	echo ''
	echo -e '\e[96mCreating the necessary services for Telk-Alert...\e[0m'
	dir=$(sudo pwd)
	cd $dir
	cp telk-alert.service /etc/systemd/system/
	cp telk-alert-agent.service /etc/systemd/system
	systemctl daemon-reload
	systemctl enable telk-alert.service
	systemctl enable telk-alert-agent.service
	echo ''
	echo -e '\e[96mCreated services...\e[0m'
	sleep 3
	echo ''
	echo -e '\e[96mCopying and creating the required directories for Telk-Alert...\e[0m'
	echo ''
	cp -r Telk-Alert-Suite /etc/
	mkdir /etc/Telk-Alert-Suite/Telk-Alert/conf
	mkdir /etc/Telk-Alert-Suite/Telk-Alert-Agent/conf
	mkdir /var/log/Telk-Alert
	echo -e '\e[96mDirectories copied and created...\e[0m'
	sleep 3
	echo ''
	echo -e '\e[96mCreating passphrase...\e[0m'
	passphrase=$(cat /dev/random | tr -dc '[:alpha:]' | head -c 30; echo)
	cat << EOF > /etc/Telk-Alert-Suite/Telk-Alert/conf/key 
$passphrase
EOF
	echo ''
	echo -e '\e[96mPassphrase created...\e[0m'
	sleep 3
	echo ''
	chown telk_alert:telk_alert -R /etc/Telk-Alert-Suite
	chown telk_alert:telk_alert -R /var/log/Telk-Alert
	echo -e '\e[96mTelk-Alert installed on the computer...\e[0m'
	sleep 3	
	echo ''
	echo -e '\e[96mStarting Telk-Alert-Tool...\e[0m'
	sleep 5
	cd /etc/Telk-Alert-Suite/Telk-Alert-Tool
	python3 Telk_Alert_Tool.py
elif [ $opc = "U" ] || [ $opc = "u" ]; then
	echo ''
	echo -e '\e[96mStarting the Telk-Alert update...\e[0m'
	echo ''
	dir=$(sudo pwd)
	cp -r Telk-Alert-Suite /etc/
	chown telk_alert:telk_alert -R /etc/Telk-Alert-Suite
	sleep 3
	echo -e '\e[96mTelk-Alert updated...\e[0m'
	echo ''
	echo -e '\e[96mStarting Telk-Alert-Tool...\e[0m'
	sleep 5
	cd /etc/Telk-Alert-Suite/Telk-Alert-Tool
	python3 Telk_Alert_Tool.py
else
	clear
	exit
fi 
