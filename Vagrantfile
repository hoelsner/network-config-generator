# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure(2) do |config|
  config.vm.define "ncg", primary: true do |ncg|
    ncg.vm.box = "ubuntu/xenial64"
    ncg.vm.hostname = "network-config-generator"

    ncg.vm.network "public_network"
    ncg.vm.network "forwarded_port", guest: 80, host: 10000, protocol: "tcp"

    ncg.vm.provider "virtualbox" do |vb|
      vb.memory = "1024"
    end

    ncg.vm.provision "shell", path: "deploy/stage_vagrant_vm_debian.sh"
    ncg.vm.post_up_message = "The Network Configuration Generator is available at 'http://localhost:10000'"
  end
  config.vm.define "ncg_debian", primary: true do |ncg_debian|
    ncg_debian.vm.box = "debian/jessie64"
    ncg_debian.vm.hostname = "network-config-generator"

    ncg_debian.vm.network "public_network"
    ncg_debian.vm.network "forwarded_port", guest: 80, host: 11000, protocol: "tcp"

    ncg_debian.vm.provider "virtualbox" do |vb|
      vb.memory = "1024"
    end

    ncg_debian.vm.provision "shell", path: "deploy/stage_vagrant_vm_debian.sh"
    ncg_debian.vm.post_up_message = "The Network Configuration Generator is available at 'http://localhost:11000'"
  end
end
