import argparse
import os
from os import path
import pty
import signal
import subprocess


def start_db(data_dir, name):
    uid = os.getuid()
    gid = os.getgid()
    os.makedirs(data_dir, exist_ok=True)
    abs_data_dir = path.abspath(data_dir)
    command = ['docker',
               'run',
               '-i',
               '--rm',
               '--user', '{uid}:{gid}'.format(uid=uid, gid=gid),
               '-v', '/etc/passwd:/etc/passwd:ro',
               '-v', '{abs_data_dir}:/var/lib/postgresql/data'.format(abs_data_dir=abs_data_dir),
               '--name', name,
               'postgres',
              ]
    pty.spawn(command)


def psql(name):
    command = ['docker',
               'run',
               '-it',
               '--rm',
               '--link', '{name}:postgres'.format(name=name),
               'postgres',
               'psql', '-h', 'postgres', '-U', 'postgres',
              ]
    pty.spawn(command)


def start_db_main():
    parser = argparse.ArgumentParser(description='Starts a PostgreSQL database using docker')
    parser.add_argument('data_dir', help='local path to PostgreSQL instance storage')
    parser.add_argument('name', help='container name')
    args = parser.parse_args()
    start_db(args.data_dir, args.name)


def psql_main():
    parser = argparse.ArgumentParser(description='Connects to a pg_docker_psql instance using docker')
    parser.add_argument('name', help='database container name')
    args = parser.parse_args()
    psql(args.name)
