:file:`test/` :file:`Makefile` targets
############################################################

.. contents:: :local:


:command:`repo-py`
============================================================

Tests the repository version by running
Python unit, integration and system tests.

.. rubric:: Environment

Should be run from within the virtual environment
:file:`PRJROOT/venv-run`.


:command:`repo-xly`
============================================================

Tests the repository version by running
Exactly test cases.

.. rubric:: Environment

Should be run from within the virtual environment
:file:`PRJROOT/venv-run`.

.. rubric:: Prerequisite

All tests towards the source code in the repo passes.


:command:`install-py`
============================================================

Tests an installation by running
Python unit, integration and system tests.

Runs in a virtual environment where Exactly is installed.
The venv is created if it does not exist.

.. rubric:: Prerequisite

A distribution has been built.


:command:`containerized`
============================================================

Runs tests inside a clean container,
for all supported versions of Python.


For details, see the :file:`containerized/` dir
(:doc:`containerized/README`).

.. rubric:: Prerequisite

A distribution has been built.
