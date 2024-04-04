Guidelines for Version Control with Git
############################################################

.. contents:: :local:

Commits
============================================================

.. note::

   These are guidelines for commits on the "master" branch.

A *single commit* should accomplish a *single goal*
------------------------------------------------------------

End User Goals
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Goals that are relevant to end users are the easiest to define.
E.g.

* a new symbol type
* a new builtin symbol
* changed behaviour of an instruction
* improvements of builtin help of a previous release
* fix of typo in builtin help of a previous release
* setting the version of the next release
* packaging for new type of distribution of the program

Many of these goals consists of several parts:

* implementation
* builtin documentation (the Reference Manual and CLI help)
* tests
* example test cases
* test cases for checking error messages

Developer goals
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Goals relevant for developers are a bit more tricky to define.

Some examples are:

* New, or improvement of, Development guidelines (like this text)
* Improvement or change of build infrastructure

Refactorings
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

A refactoring of the source code is usually not a goal in itself
but a means to accomplish a goal,
and thus should not be a commit of its own.

But for practical reasons some refactorings may be treated as a
goal and thus appear in a commit of its own.
Such a refactoring probably affects several end user functionalities
so that it affects not only the end user goal that is being worked on.

For example:

* Renaming of a popular item
* Move of a popular item
* Improvement of popular infrastructure

Having such a large refactoring as a separate commit may make
it easier to understand a later commit that implements a feature
on top of it.

Size - num files and num lines - doesn't matter
------------------------------------------------------------

A commit may fix a single typo - changing a single character
in a single file. Or change the name of a popular module -
change many lines of many files.

Both of these commits are fine since each has a single clear goal.

All tests should pass
------------------------------------------------------------

Run relevant tests before committing!

Commit messages
============================================================

.. note::

   These are guidelines for commits on the "master" branch.

The format of a commit message is not written in stone,
but a recommendation for the first line is::

    SUBJECT: CHANGE-TYPE-TOKEN DESCRIPTION

For example:

* ``type/files-source: ADD dir-contents-of``
* ``assert/contents: syntax: CHANGE add colon between path, matcher``
* ``readme: IMPROVE examples``
* ``DELETE support for Python 3.5``
* ``regex: help: FIX missing form HERE-DOC``
* ``instr/file: test: REFACT modernize some tests``
* ``instr/timeout: REPLACE instruction in [conf] w instructions in later phases``
* ``instr/timeout: ADD ability to set no-timeout``
* ``test resources: MOVE source argument utils``
* ``string|files-matcher: RENAME matcher "empty" -> "is-empty"``

SUBJECT
    The functionality/part of the code that the commit affects.

    For work split into multiple commits, this text should be identical
    for grouping the commits together.

CHANGE-TYPE-TOKEN
    Description of the type of change.

    An uppercase string chosen from a set of (almost) predefined
    set of strings.

DESCRIPTION
    A single sentence describing the change.

    Written in present tense.

    The CHANGE-TYPE-TOKEN can be considered part of the sentence,
    although the result may not be grammatically correct.
    E.g. the token "ADD" can be read as "ADDs".

CHANGE-TYPE-TOKEN
------------------------------------------------------------

End User Goals
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The SUBJECT of the commit message may be e.g.

* a feature
* builtin help text (the Reference Manual)
* test case examples

Tokens:

* ``ADD``
* ``DELETE``
* ``FIX``

  Fixes a bug.

  Fixes a typo.
* ``IMPROVE``

  Optimization of a feature.

  Improves an error message.

  Improves builtin help.
* ``MOVE``
* ``RENAME``
* ``REPLACE``
* ``CHANGE``

Developer goals
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The SUBJECT of the commit message may be e.g.

* a source code module
* some arbitrary reusable code
* developer documentation (such as this file)
* a feature that is being refactored

Tokens:

* ``ADD``
* ``DELETE``
* ``IMPROVE``
* ``MOVE``

  Special kind of refactoring.
* ``RENAME``

  Special kind of refactoring.
* ``REPLACE``

  Special kind of refactoring.
* ``CHANGE``

  Special kind of refactoring.
* ``REFACT``

  Refactoring of any other kind.

Development in branches
============================================================

Use a Development Branch if useful
------------------------------------------------------------

It is up to the developer if a development branch should
be used or not.

The commits and commit messages
on development branch need not adhere to the guidelines
for the "master" branch,
since they can be changed via ``git rebase``.

If many commits are combined into a single commit - set the
commit time to the time of the latest commit (or at least
not before the time of the last commit).

To set the time of the last commit to the current time:

.. code-block:: console

   $ git commit --amend --reuse-message HEAD --date "$(date)"

Integrate using "rebase"
------------------------------------------------------------

Integrate branches into the "master" branch using git's "rebase"
from the master branch.

.. code-block:: console

   $ git checkout master
   $ git rebase <DEV-BRANCH>
