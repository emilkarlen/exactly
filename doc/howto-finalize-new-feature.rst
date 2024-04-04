HOWTO Finalize a new feature
############################################################

.. contents:: :local:


Reference Manual
============================================================

Make sure documentation exists and is correct.

:file:`err-msg-tests/`
============================================================

If the feature "turns up" in error messages,
make sure they are

* informative
* readable
* consistent with existing error messages and their structure

Check this by reading the output from existing test cases and suites.

Add new test cases and suites if relevant.

:file:`examples/`
============================================================

Add informative examples if relevant for the feature.

Make sure all existing examples work by running the test suite.

:file:`CHANGELOG.md`
============================================================

.. seealso::

   https://keepachangelog.com/en/1.0.0/

:file:`HOWTO-UPGRADE.md`
============================================================

If the feature changes syntax or behaviour,
add instructions for how to upgrade from the previous version.

:file:`README.rst`
============================================================

Check especially

* Examples
* Development status

Make sure all examples work by running the test suite for
the examples in :file:`README.rst` found under
:file:`examples/`.

If any of the existing tests has to be changed, make the same change
to :file:`README.rst` - the tests are hard coded there.
Note that some examples may differ in "technical" details to make
the example in :file:`README.rst` clearer.

Make sure program version is :literal:`next`
============================================================

Set this in :py:mod:`exactly_lib.program_info`.

Check this right before rebasing into the :literal:`master` branch
and make the change only if necessary.

git commit log
============================================================

Often a feature should be a single commit.
Relevant refactorings can be separate commits, though.

Check existing commit log to be consistent.

.. seealso::

   :doc:`guidelines-vc`

Test
============================================================

Run all tests on all supported platforms, for all supported
versions of Python.

.. seealso::

   :doc:`/test/index`

emilkarlen.github.io
============================================================

Optional.

This site/repo contains the Reference Manual etc for the
latest release and the latest development version.

Generate info about the development version,
commit it and push it.

See the repo's ``Makefile`` for Exactly for info about how to do this.

.. seealso::

   * https://github.com/emilkarlen/emilkarlen.github.io
   * https://emilkarlen.github.io
