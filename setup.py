from setuptools import setup, find_packages


setup(
    name='pypgdev',
    packages=find_packages(),
    install_requires=['pexpect'],
    entry_points={
        'console_scripts': [
            'pg_docker = pypgdev.docker:psql_main',
            'pg_docker_schema_diff = pypgdev.docker:schema_diff_main',
        ]
    },
)
