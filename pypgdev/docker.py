import argparse
import os
from os import path
import signal
import subprocess
import uuid

from pypgdev import terminal


def start_db_command(data_dir, name):
    uid = os.getuid()
    gid = os.getgid()
    os.makedirs(data_dir, exist_ok=True)
    abs_data_dir = path.abspath(data_dir)
    return ['docker',
            'run',
            '-i',
            '--rm',
            '--user', '{uid}:{gid}'.format(uid=uid, gid=gid),
            '-v', '/etc/passwd:/etc/passwd:ro',
            '-v', '{abs_data_dir}:/var/lib/postgresql/data'.format(abs_data_dir=abs_data_dir),
            '--name', name,
            'postgres',
           ]


def start_db(data_dir, name):
    command = start_db_command(data_dir, name)
    terminal.start(command)


def psql(name):
    command = ['docker',
               'run',
               '-it',
               '--rm',
               '--link', '{name}:postgres'.format(name=name),
               'postgres',
               'psql', '-h', 'postgres', '-U', 'postgres',
              ]
    terminal.start(command)


def dump_schema(data_dir):
    container_name = str(uuid.uuid4())
    command = start_db_command(data_dir, container_name)
    db_process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        command = ['docker',
                   'run',
                   '-it',
                   '--rm',
                   '--link', '{container_name}:postgres'.format(container_name=container_name),
                   'postgres',
                   'pg_dump', '-h', 'postgres', '-U', 'postgres', '--schema-only',
                  ]
        output = subprocess.run(command, stdout=subprocess.PIPE).stdout
    finally:
        db_process.terminate()
    return output


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
