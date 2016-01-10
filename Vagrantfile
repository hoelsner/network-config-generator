# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure(2) do |config|
  config.vm.define "ncg", primary: true do |ncg|
    ncg.vm.box = "ubuntu/trusty64"
    ncg.vm.hostname = "network-config-generator"

    ncg.vm.network "forwarded_port", guest: 80, host: 10000

    ncg.vm.provider "virtualbox" do |vb|
      vb.memory = "1024"
    end

    ncg.vm.provision "shell", path: "deploy/stage_vagrant_vm.sh"
    ncg.vm.post_up_message = "The Network Configuration Generator is available at 'http://localhost:10000'"
  end
end
