from setuptools import setup, find_packages

setup(
    name='r53',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'click==6.6',
        'boto3==1.3.1'
    ],
    entry_points='''
        [console_scripts]
        r53=r53.cmd:cmd_cli
    ''',
)
