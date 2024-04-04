Development Environment
############################################################

.. contents:: :local:


Building
============================================================

Build distribution and documentation in a
Python virtual environment.

Create this environment via the ``Makefile`` in the root dir:

.. code-block:: console

   $ make venv-build

Then activate it when starting to work:

.. code-block:: console

   $ . venv-build/bin/activate


Running tests
============================================================

Run tests in a Python virtual environment.

Create this environment via the ``Makefile`` in the root dir:

.. code-block:: console

   $ make venv-run

Then activate it when starting to work:

.. code-block:: console

   $ . venv-run/bin/activate

If working from an IDE, point it to
the interpreter in the virtual environment.


Leaving a Python virtual environment
============================================================

.. code-block:: console

   $ deactivate
