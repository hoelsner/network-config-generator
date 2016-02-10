#!/usr/bin/env bash
echo "install Ansible on the VM"
sudo apt-add-repository ppa:ansible/ansible -y
sudo apt-get update
sudo apt-get install ansible -y

echo "create Network Configuration Generator user..."
sudo adduser ncg --home /home/ncg --disabled-password
sudo adduser ncg sudo

echo "copy source files to /var/www/network_config_generator"
source_dir="/var/www/network_config_generator"

if [ -d '$source_dir' ]; then
    # directory already exists, update codebase
    sudo -u ncg cp -ru /vagrant/* ${source_dir}
else
    sudo mkdir -p ${source_dir}
    sudo chown ncg ${source_dir}
    sudo chgrp ncg ${source_dir}
    sudo -u ncg cp -r /vagrant/* ${source_dir}
    # cleanup for initial setup
    sudo rm /var/www/network_config_generator/network_config_generator.key
    sudo rm /var/www/network_config_generator/ftp_user.key
    sudo rm /var/www/network_config_generator/log/application.log
    sudo rm /var/www/network_config_generator/*.db
fi

echo "stage the Network Configuration Generator Web service..."
cd ${source_dir}

ansible-playbook -i 'localhost,' -c local deploy/setup.yaml
ansible-playbook -i 'localhost,' -c local deploy/setup_local_services.yaml
