#!/usr/bin/env bash
echo "-------------------------------------------------------------------------------------------------"
echo " Network Configuration Generator - Ubuntu 14.04"
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
            extra_vars=""
            echo "Do you want to use systemd? (only with Ubuntu > 14.04)"
            select sub_result in Yes No
            do
                case ${sub_result} in
                    "Yes" )
                        extra_vars+=" use_systemd=true"
                        break
                        ;;
                    *)
                        break
                        ;;
                esac
            done

            echo "---------------------------------"
            echo "Do you want to configure the local services (FTP/TFTP)?"
            echo "---------------------------------"
            select sub_result in Yes No
            do
                case ${sub_result} in
                    "Yes" )
                        extra_vars+=" configure_local_services=true"
                        break
                        ;;
                    *)
                        break
                        ;;
                esac
            done

            echo "---------------------------------"
            echo "Install Ansible..."
            echo "---------------------------------"
            sudo apt-add-repository ppa:ansible/ansible -y
            sudo apt-get update
            sudo apt-get install ansible -y

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
            sudo chown ncg ${source_dir}
            sudo chgrp ncg ${source_dir}
            sudo -u ncg cp -r * ${source_dir}

            echo "---------------------------------"
            echo "Setup of the Network Configuration Generator Web service..."
            echo "---------------------------------"
            cd ${source_dir}

            ansible-playbook -i 'localhost,' -c local deploy/setup.yaml --ask-sudo-pass --extra-vars "${extra_vars}"

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