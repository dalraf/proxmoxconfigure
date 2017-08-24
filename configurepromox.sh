#/bin/bash
apt-get -y install python-pip
apt-get -y install python-dev
apt-get -y install sshpass
pip install ansible
ansible-playbook --ask-vault-pass -i "localhost," installproxmox.yml
