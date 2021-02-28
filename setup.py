import os
import sys

from setuptools import setup, find_packages


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


SRC_DIR_NAME = 'src'

prj_root_dir = sys.path[0]
src_dir = os.path.join(prj_root_dir, SRC_DIR_NAME)
sys.path.insert(0, src_dir)

from exactly_lib import program_info

setup(
    name=program_info.PROGRAM_NAME,
    version=program_info.VERSION,
    zip_safe=False,
    author='Emil Karlen',
    author_email="emil@member.fsf.org",
    description=('Tests a command line program by executing it in a temporary sandbox directory and '
                 'inspecting its result.'),
    license='GPLv3+',
    keywords='test case suite check assert script shell console command line program execute sandbox',
    url='https://github.com/emilkarlen/exactly',
    package_dir={
        '': 'src',
    },
    packages=find_packages(SRC_DIR_NAME),
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Topic :: Software Development :: Testing',
        'Topic :: System :: Systems Administration',
        'Environment :: Console',
        'Operating System :: POSIX',
    ],
    python_requires='>={}'.format(program_info.PYTHON_VERSION__MIN),
    entry_points={
        'console_scripts': [
            program_info.PROGRAM_NAME + ' = exactly_lib.cli_default.default_main_program_setup:main',
        ]
    }
)
