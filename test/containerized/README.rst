Execution of tests in a clean environment, for all supported Python versions
##############################################################################

This is implemented by executing the tests in OCI containers using Docker.

.. attention::

   Obviously, Docker must be installed, and it must be executable by the current user.

.. contents:: :local:


Running the tests
============================================================

First, make container images
------------------------------------------------------------

.. code-block:: console

   $ make images

Then, run tests towards all supported Python versions
------------------------------------------------------------

.. code-block:: console

   $ make all

See :file:`Makefile` for details.

.. rubric:: Prerequisite

A distribution has been built.


What is tested
============================================================


The tests tries to test as much as possible:

* Python unit, integration and system tests

  * towards the source code in the repository
  * towards an installation

* Exactly test cases
* Exactly examples in ``PRJROOT/examples``

See the implementation for details.


The :program:`run` utility program
============================================================

:program:`run` is used to run things in a container
designed for executing tests towards a given Python version.
It is used to run the tests,
but can also be used to open a shell in a container etc.

For details:

.. code-block:: console

   $ ./run -h


Test of development tools in :file:`test/`
============================================================

The :file:`test/` directory contains tests of
the tools used and implemented in this directory.

.. note:: These tests are not executed by the commands above
   because they test Exactly and not the tools used for testing Exactly.
