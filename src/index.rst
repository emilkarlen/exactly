Source code structure
############################################################

.. toctree::
   :maxdepth: 2

   doc/symbol/index
   doc/program_info

The ``src/`` directory contains the source code
that is included in an installation of the program.


An installation consists of two parts:

 - A Python package - ``exactly_lib``
 - An executable - ``exactly``

``exactly_lib`` is installed as a normal Python package.


The executable file ``exactly``
is installed in the system ``PATH``.
It runs ``default-main-program-runner.py``.
