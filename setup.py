from setuptools import setup, find_packages


setup(
    name='pypgdev',
    packages=find_packages(),
    install_requires=['ipython', 'pexpect'],
    entry_points={
        'console_scripts': [
            'pg_docker = pypgdev.docker:start_db_main',
            'pg_docker_psql = pypgdev.docker:psql_main',
            'pg_docker_schema_diff = pypgdev.docker:schema_diff_main',
        ]
    },
)
