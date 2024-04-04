HOWTO Release
############################################################

.. seealso::

   * https://packaging.python.org/
   * http://peterdowns.com/posts/first-time-with-pypi.html

.. contents:: :local:

.. role:: file(literal)

CHANGELOG
============================================================

:doc:`/CHANGELOG` Should contain entry for each change of syntax or behaviour.

This should be done as part of developing features, so it should be done
by the time of releasing. But check it just to be sure!

.. seealso:: :doc:`howto-finalize-new-feature`

Template
---------------------------------------------------

::

    ## [VERSION] - YYYY-MM-DD
    ## [Unreleased]

    ### Added
    ### Changed
    ### Deprecated
    ### Removed
    ### Fixed
    ### Security

HOWTO-UPGRADE
============================================================

:doc:`HOWTO-UPGRADE </HOWTO-UPGRADE>`
should contain a description of how to upgrade
each backwards incompatible change from the previous version.

README - Development info
============================================================

* Development status
* Future development

Make sure to be in line with the release.

doc/
============================================================

* TODOs
* BUGSs
* Developer documentation

  Check by generating the documentation via make in the root dir:

  .. code-block:: console

     $ make doc

COPYRIGHT - contact info
============================================================

Make sure the contact info at the end of the COPYRIGHT is correct.

Minimum Python version
============================================================

* :py:mod:`exactly_lib.program_info`
* :file:`pyproject.toml`

  * requires-python
  * classifiers

* README

github pages - Add Ref Man for release version
============================================================

Note: The version number in the doc has not been updated
yet, but this is ok: this allows us to update README
and test its link to the ref-man.
The manual on github pages can be updated any time later.

Set version number
============================================================

* code
  :py:mod:`exactly_lib.program_info`
* :file:`CHANGELOG.md`
* :file:`HOWTO-UPGRADE.md`
* :file:`README.rst` - update link to Ref Man on github pages

Test
============================================================

* run-test-suite.py
* Run tests towards installed program

  1. Build distribution

     .. code-block:: console

        $ make clean; make build
  2. Activate virtual environment "venv"

    #. If venv does not exist, create it with

       .. code-block:: console

          $ make venv
    #. Enter the venv

       .. code-block:: console

          $ . venv/bin/activate

  3. Install in venv

     .. code-block:: console

        $ make install

  4. Run tests

     .. code-block:: console

        $ python3 test/run-test-suite-towards-installed-program.py

  5. Exit the venv

     .. code-block:: console

        $ deactivate

  6. Remove install from venv

     .. code-block:: console

        $ make uninstall-venv

* Run exactly tests

  .. code-block:: console

     $ exactly suite test/exactly-cases

* Run on as many platforms as possible - on linux using docker

Make sure syntax of examples is correct
============================================================

Check by running the test suite of the examples.

README - link to Ref Man on github pages
============================================================

* Check that link from :file:`README.rst` shows Ref Man for correct version
* Validate syntax

  .. code-block:: console

     $ python3 -m rstvalidator README.rst

github pages - Add README for the new release
============================================================

exactly/version/Z-Y-Z/README.rst

Set release date
============================================================

* :file:`COPYRIGHT`

  Make sure release year is included in COPYRIGHT
* :file:`CHANGELOG.md`

Make release artifacts
============================================================

* Remove existing distributables

  .. code-block:: console

     $ make clean

* Make distributables

  Distribute source and wheel

  .. code-block:: console

     $ make build

Upload to PyPi test
============================================================

Account on PyPi test
---------------------------------------------------

First you must have access to an account on TestPyPI

.. seealso:: https://packaging.python.org/en/latest/guides/using-testpypi/

Add TestPyPI to your :file:`~/.pypirc`

.. parsed-literal::

    [distutils]

    index-servers = testpypi

    [testpypi]

    repository = https://test.pypi.org/legacy/
    username   = __token__
    password   = *TOKEN*

*TOKEN* should be replaced with a token generated on TestPyPI.

Be sure to use the same name for the repository in :file:`./pypirc` as in
:file:`Makefile`.

Upload
---------------------------------------------------

.. code-block:: console

   $ make upload-test

Check
---------------------------------------------------

* README: links to RefMan

Upload to PyPi prod
============================================================

.. code-block:: console

   $ make upload

github pages
============================================================

Make "latest" sym link point to latest release.

exactly/version/latest

github wiki
============================================================

Update examples.

Run tests in examples/wiki,
and if changes are needed to make these work,
make the same changes to wiki.

Tag repo with version
============================================================

Tag repo after upload to PyPi,
so that the release on PyPi is verified.

.. code-block:: console

   $ git tag vVERSION
   $ git push --tags

Make release on github
============================================================

Via the github site.
