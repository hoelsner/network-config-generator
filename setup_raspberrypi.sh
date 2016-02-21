#!/usr/bin/env bash
echo "-------------------------------------------------------------------------------------------------"
echo " Network Configuration Generator - Raspbian"
echo "-------------------------------------------------------------------------------------------------"
echo ""
echo "This script stages the \"Network Configuration Generator\" Web service on the host. It installs"
echo "all dependencies, including nginx and gunicorn."
echo ""
echo "The script will create a new user \"ncg\", that is used to run the service."
echo ""
echo "PLEASE NOTE: This script assumes, that this Web service is the only application running on "
echo "the host."
echo ""
echo "-------------------------------------------------------------------------------------------------"

echo "Do you wish to continue?"
select result in Yes No
do
    case ${result} in
        "Yes" )
            extra_vars+=" use_systemd=true configure_local_services=true"

            echo "---------------------------------"
            echo "Install Ansible and other dependencies..."
            echo "---------------------------------"
            sudo apt-get install python-dev python3-dev
            sudo apt-get update
            sudo pip install ansible markupsafe

            echo "---------------------------------"
            echo "create Network Configuration Generator user..."
            echo "---------------------------------"
            sudo adduser ncg --home /home/ncg --disabled-password
            sudo adduser ncg sudo

            echo "---------------------------------"
            echo "copy source files to /var/www/network_config_generator"
            echo "---------------------------------"
            source_dir="/var/www/network_config_generator"

            sudo mkdir -p ${source_dir}
            sudo cp -r * ${source_dir}
            sudo chown -R ncg ${source_dir}
            sudo chgrp -R ncg ${source_dir}
            sudo chmod -R 775 ${source_dir}

            echo "---------------------------------"
            echo "Setup of the Network Configuration Generator Web service..."
            echo "---------------------------------"
            cd ${source_dir}

            sudo ansible-playbook -i 'localhost,' -c local deploy/setup.yaml --extra-vars "${extra_vars}"

            echo "---------------------------------"
            echo "Setup complete."
            echo ""
            break
            ;;
        * )
            echo "Okay, exit setup."
            break
            ;;
    esac
done