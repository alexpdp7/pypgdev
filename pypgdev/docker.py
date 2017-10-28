import argparse
import contextlib
import difflib
import os
from os import path
import signal
import subprocess
import time
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


@contextlib.contextmanager
def database_process(data_dir):
    container_name = str(uuid.uuid4())
    command = start_db_command(data_dir, container_name)
    db_process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    while True:
        command = ['docker',
                   'run',
                   '-it',
                   '--rm',
                   '--link', '{name}:postgres'.format(name=container_name),
                   'postgres',
                   'psql', '-h', 'postgres', '-U', 'postgres', '-c', 'select 1',
                  ]
        if subprocess.run(command, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).returncode == 0:
            break
        print('Waiting for database to be up...')
        time.sleep(1)
    yield container_name
    db_process.terminate()


def psql(data_dir):
    with database_process(data_dir) as container_name:
        command = ['docker',
                   'run',
                   '-it',
                   '--rm',
                   '--link', '{name}:postgres'.format(name=container_name),
                   'postgres',
                   'psql', '-h', 'postgres', '-U', 'postgres',
                  ]
        terminal.start(command)


def dump_schema(data_dir):
    with database_process(data_dir) as container_name:
        command = ['docker',
                   'run',
                   '-it',
                   '--rm',
                   '--link', '{container_name}:postgres'.format(container_name=container_name),
                   'postgres',
                   'pg_dump', '-h', 'postgres', '-U', 'postgres', '--schema-only',
                  ]
        return subprocess.run(command, stdout=subprocess.PIPE).stdout


def schema_diff(data_dir_a, data_dir_b, context_lines=10):
    schema_a = dump_schema(data_dir_a).decode().split('\n')
    schema_b = dump_schema(data_dir_b).decode().split('\n')
    diff = difflib.context_diff(schema_a, schema_b, n=context_lines)
    return '\n'.join(diff)


def start_db_main():
    parser = argparse.ArgumentParser(description='Starts a PostgreSQL database using docker')
    parser.add_argument('data_dir', help='local path to PostgreSQL instance storage')
    parser.add_argument('name', help='container name')
    args = parser.parse_args()
    start_db(args.data_dir, args.name)


def psql_main():
    parser = argparse.ArgumentParser(description='Starts a PostgreSQL database instance and connects to it')
    parser.add_argument('data_dir', help='local path to PostgreSQL instance storage')
    args = parser.parse_args()
    psql(args.data_dir)


def schema_diff_main():
    parser = argparse.ArgumentParser(description='Extracts an schema diff from two data dirs')
    parser.add_argument('data_dir_a', help='local path to PostgreSQL instance storage a')
    parser.add_argument('data_dir_b', help='local path to PostgreSQL instance storage b')
    args = parser.parse_args()
    print(schema_diff(args.data_dir_a, args.data_dir_b))
