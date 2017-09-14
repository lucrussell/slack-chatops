from setuptools import setup, find_packages


setup(
    name='slackbot',
    version='1.0.0',
    description='Expose Kafka lag statistics over HTTP',
    author='Luc Russell',
    license='',
    classifiers=[
        'Programming Language :: Python :: 3.4'
    ],
    keywords='',
    packages=find_packages(exclude=['contrib', 'docs', 'spec*']),
    install_requires=[
        'docopt',
        'falcon>=1.0',
        'gunicorn>=19.4.5',
        'pykafka',
        'pyyaml',
        'slackclient'
    ],
    package_data={},
    data_files=[],
    entry_points={
        'console_scripts': [
            'slackbot = slackbot.app:main'
        ],
    },
)
