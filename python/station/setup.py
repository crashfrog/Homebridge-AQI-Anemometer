from setuptools import setup, find_packages

with open('requirements.txt') as req_file:
    requirements = req_file.read()

setup(
    author="Justin Payne",
    author_email="crashfrog@gmail.com",
    python_requires='>=3.7',
    entry_points={
        'console_scripts': ["aqi=station.aqi:cli", 'station=station.anemometer:cli']
    },
    install_requirements=requirements,
    name='station',
    version='0.1.0',
    zip_safe=False
)