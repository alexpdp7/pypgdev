from setuptools import setup, find_packages


setup(
    name='pypgdev',
    packages=find_packages(),
    install_requires=['ipython'],
    entry_points={
        'console_scripts': [
            'pg_docker = pypgdev.docker:start_db_main'
        ]
    },
)
