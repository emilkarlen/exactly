import os

from setuptools import setup, find_packages


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setup(
    name='shellcheck',
    version='0.7',
    author='Emil Karlen',
    # author_email="emil@member.fsf.org",
    author_email='emilkarlen@aim.com',
    description=('Checks a command line program by executing it in a temporary sandbox directory and '
                 'inspecting the result.'),
    license='GPLv3+',
    keywords='test case suite check script shell console command line program',
    url='https://github.com/emilkarlen/shellcheck',
    package_dir={
        '': 'src',
    },
    packages=find_packages('src'),
    long_description=read('README'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Topic :: Software Development :: Testing',
        'Topic :: System :: Systems Administration',
        'Environment :: Console',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
    ],
    entry_points={
        'console_scripts': [
            'shellcheck = shellcheck_lib.default.default_main_program_setup:main',
        ]
    }
)
