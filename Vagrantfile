# Vagrantfile
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  
  # 1. Sistema Operativo
  config.vm.box = "bento/ubuntu-24.04" 
  
  # 2. Mapear puerto de Flask (5000)
  config.vm.network "forwarded_port", guest: 5000, host: 5000

  config.vm.provider "virtualbox" do |vb|
    vb.memory = "4096"  # Asignar 4GB de RAM
    vb.cpus = 4         # Asignar 4 CPUs
  end

  # 3. Provisionamiento: Ejecuta el script completo
  config.vm.provision "shell", path: "bootstrap.sh"
end
