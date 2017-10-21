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
               '--user', '{uid}:{gid}'.format(uid=uid, gid=gid),
               '-v', '/etc/passwd:/etc/passwd:ro',
               '-v', '{abs_data_dir}:/var/lib/postgresql/data'.format(abs_data_dir=abs_data_dir),
               '--name', name,
               'postgres',
              ]
    try:
        subprocess.run(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, check=True)
    finally:
        subprocess.run(['docker', 'kill', name], check=True)
        subprocess.run(['docker', 'rm', name], check=True)


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
    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir')
    parser.add_argument('name')
    args = parser.parse_args()
    start_db(args.data_dir, args.name)


def psql_main():
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    args = parser.parse_args()
    psql(args.name)
