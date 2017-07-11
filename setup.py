import os
from setuptools import setup, find_packages
import pytes
from pytes.examples import available

#Grab the README.md for the long description
with open('README.md', 'r') as f:
    long_description = f.read()

VERSION = pytes.__version__

def setup_package():
    examples = set()
    for i in available():
        if not os.path.isdir('pytes/examples/' + i):
            if '.' in i:
                glob_name = 'examples/*.' + i.split('.')[-1]
            else:
                glob_name = 'examples/' + i
        else:
            glob_name = 'examples/' + i + '/*'
        examples.add(glob_name)

    setup(
        name = "pytes",
        version = VERSION,
        author = "Kelvin Rodriguez",
        author_email = "kr788@nau.edu",
        description = ("An interface for MGS TES data"),
        long_description = long_description,
        license = "Public Domain",
        keywords = "MGS TES",
        url = "http://packages.python.org/pytes",
        packages=find_packages(),
        include_package_data=True,
        package_data={'pytes' : list(examples)},
        zip_safe=False,
        install_requires=[
            'pandas',
	    'geopandas',
            'plio',
            'scipy',
    	    'matplotlib',
            'angles'
        ],
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Topic :: Utilities",
            "License :: Public Domain",
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
        ],
    )

if __name__ == '__main__':
    setup_package()
