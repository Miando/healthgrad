# Automatically created by: shub deploy

from setuptools import setup, find_packages

setup(
    name         = 'project',
    version      = '1.0',
    packages     = find_packages(),
    include_package_data = True,
    entry_points = {'scrapy': ['settings = healthgrades.settings']},
    #data_files = [ ("input",  ["healthgrades/spiders/input/1.csv",
    #                             "healthgrades/spiders/input/2.csv"])]
)
