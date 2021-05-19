#!/bin/bash
sudo yum update -y
sudo yum install -y python37-devel python37-libs python37-pip
sudo yum install -y mysql57-devel
sudo yum install -y ruby
sudo yum install -y wget
sudo yum install -y docker
sudo yum groupinstall -y "Development Tools"
sudo echo "/usr/lib64/mysql57" >> /etc/ld.so.conf.d/mysql57-x86_64.conf
sudo /sbin/ldconfig
sudo update-alternatives --set python /usr/bin/python3.7
sudo service docker start
sudo chkconfig docker on
sudo curl -L "https://github.com/docker/compose/releases/download/1.23.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo usermod -aG docker ec2-user
