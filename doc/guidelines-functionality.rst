Guidelines for the functionality of the program
############################################################

.. contents:: :local:


Main purpose
============================================================

Exactly is aimed at testing ...

* programs that are executed via the OS shell
* programs that are executed via other programs
* programs who's input is command line arguments
* programs who's input is stdin
* programs who's input is environment variables
* programs who's input is files (including stdin)
* programs who's output is exitcode and stdout, stderr
* programs who's output is side effect on files
* programs who's output is side effect on external resources, such as databases


Dependencies
============================================================

Exactly (base version) DOES not depend on anything not included in the
standard library of it's implementation language.

.. rubric:: MOTIVATION

It should be easy to install Exactly together with other tools.

It should be easy to include the implementation of Exactly (except for the
implementation of the language it uses (Python 3)) in a project that uses
Exactly.

The implementation language is chosen to be a language that contains a large
standard library that does not make this restriction a great limitation.


Portability
============================================================

Portability of Exactly itself
------------------------------------------------------------

The goal is that Exactly is ported to (in order of priority):

* Linux
* OS X
* Windows

The implementation language Python 3 is the generic interface towards all
these systems.

.. rubric:: MOTIVATION

Usefulness.

Portability of test cases
------------------------------------------------------------

Individual test cases, on the other hand, should not be limited to the portability
requirements of Exactly itself.

The functionality for running OS shell commands is the main source of non-portability.

.. rubric:: MOTIVATION

The requirement of having all tests to be portable to all systems that
Exactly itself is ported to would prevent usage of many useful features
that are available only on a specific system.

Many programs are not required to be portable.

E.g. a utility program is developed on a Linux Debian system and is only
intended to be used on a Debian Linux production system.
Thus one can use all utility programs available on this system.  This can make
the tests much more easy to write, and more easy to read.


Instruction set
============================================================

An ideal instruction set may be infinitely large, since there are infinitely
many properties that can be tested.  But this ideal instruction set is
is not ideal in practice, since the size of the program also would be
infinitely large.

Core instruction set
------------------------------------------------------------

Functionality for working with files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The program should supply a "core" instruction set that covers the
most common needs of tests covered by Exactly's main purpose.
This means that the "core" instruction set mostly covers working with:

* programs
* the environment in which programs are executed

  * files
  * environment variables

Functionality for invoking external helper programs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The core instruction set makes it possible to extend the "built-in"
functionality by executing external programs.

This is useful both as a way of incorporating functionality offered by
existing programs (so that it does not have to be duplicated by Exactly),
and as a convenient way to extend Exactly's functionality by writing custom
external programs (when this is more convenient than implementing the
functionality as custom instructions).

Extending the instruction set
------------------------------------------------------------

It should be easy to extend the instruction set by custom instructions.
What this means is that it should be easy to specify the instruction set as
the union of the core instruction set and a custom instruction set.

This means writing source code and implementing a new variant of
Exactly that incorporates this source code.


Preprocessing of test cases
============================================================

Exactly allows preprocessing of test cases as a way to reuse test-code and to
avoid test-code duplication.

It should be easy to use a custom preprocessor in the form av an executable
program.

Exactly also could offer a built-in preprocessor that (of course) works
identically on all supported platforms.  Currently, this is a TODO.


Instructions in the assert phase
============================================================

Form: ACTUAL EXPECTED

.. rubric:: MOTIVATION

Although the opposite form - EXPECTED ACTUAL - often is more easy to read and
understand, Exactly uses the opposite form.  Reasons for this is
possibility to have shorter (=more readable) assertions.  The reason for this
is that the instruction name must start the line.  And the instruction may specify
what is tested, i.e. the ACTUAL value.

Examples:

.. code-block::

   exit-code == 1

   stdout    is-empty
   stderr    ! is-empty

   contents actual-file.txt : equals -contents-of expected-file.txt

The order could be switched. ``stdout`` and ``stderr`` instructions could be a variant
of the "contents" instruction. E.g.

.. code-block::

    contents expected-file.txt : equals stdout

    number 1 == exit-code

But this is much longer, and a bit contrived.

The goal is a short and clean syntax for common tests.  And one that is easy
to implement using the instruction-name-at-start-of-line parser.
If an assertion becomes difficult to read it might be appropriate to express
it using a macro with a more readable name.

Noteworthy is that mathematical "assertions" are often written in the
ACTUAL EXPECTED form:

* n > 1
* Im(z) = 0
