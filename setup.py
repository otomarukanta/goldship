from setuptools import setup, find_packages

setup(
    name='goldship',
    version='0.0.1',
    description='goldship',
    author='otomarukanta',
    author_email='kanta208@gmail.com',
    url='http://otomarukanta.com/',
    packages=find_packages(),
    install_requires=[
        'staygold',
        'kurofune'
        ],
    entry_points={
        "console_scripts": [
            "goldship_race_result = goldship.cmd:race_result",
            "goldship_race_result_year = goldship.cmd:race_result_year"
        ]
      }
    )
