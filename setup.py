import os
import sys
from setuptools import setup

try:
    import CloudCarrot
except ImportError:
    print("error: CloudCarrot requires Python 3 or greater.")
    sys.exit(1)

base_path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(base_path, 'requirements.txt'), 'r') as f:
    requirements = f.read().split('\n')

#with open(os.path.join(base_path, 'README.md'), 'r') as f:
#    description = f.read()

VERSION = CloudCarrot.__version__
#DOWNLOAD = "https://github.com/foozzi/CloudCarrot/archive/%s.tar.gz" % VERSION

setup(
    name='cloudcarrot',
    version=VERSION,
    author='Tkachenko Igor',
    author_email='foozzione@gmail.com',
    description='',
    packages=['CloudCarrot', 'CloudCarrot.modules'],
    install_requires=requirements,
    entry_points={
            'console_scripts':
                ['cloudcarrot = CloudCarrot.__main__:main']
        },
    #long_description=description,
    #long_description_content_type='text/markdown',
    keywords='',
    license='GNU',
    url='https://github.com/foozzi/CloudCarrot',
    #download_url=DOWNLOAD,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3 :: Only"
    ]
    #test_suite="tests"
)
