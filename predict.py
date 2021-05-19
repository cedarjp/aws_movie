#!/usr/bin/env python
import os
import sys
import subprocess


def main():
    container_id = subprocess.check_output(['docker', 'ps', '-aqf', 'name=water_abnormality_server_prediction'])
    container_id = container_id.decode().strip()
    bucket_name = sys.argv[1]
    key = sys.argv[2]
    homedir = '/home/ec2-user/'
    predict_docker_src = '/app/movie'
    os.chdir(homedir)
    command = 'docker exec {} python manage.py predict {} {} --pythonpath={}/'.format(container_id, bucket_name, key,
                                                                                      predict_docker_src)
    subprocess.check_call(['sudo', '/sbin/runuser', '-l', 'ec2-user', '-c', command])


if __name__ == '__main__':
    main()

