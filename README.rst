Tests a command line program by executing it in a temporary sandbox directory and inspecting its result.

Supports individual test cases and test suites.


TEST CASES
==========

A test case is written as a plain text file::

    [setup]

    stdin a-test-address-book.txt

    [act]

    addressbook --get-email-of --name 'Test Testingson'

    [assert]

    exitcode 0

    stdout <<EOF
    expected@email.org
    EOF


If the file 'addressbook.case' contains this test case, then ``exactly`` can execute it::


    $ exactly addressbook.case
    PASS


``PASS`` means that the two assertions were satisfied.

It also means that the prerequisites for running the test were satisfied:

- the system under test - the ``addressbook`` program - is found in the same directory as the test case file
- the test input file ``a-test-address-book.txt`` is found in the same directory as the test case file


The following test case displays a potpurri of functionality. (Be aware that this test case does not make sense -
it just displays some of ``exactly``'s functionality.)

::

    [conf]


    mode SKIP
    # This will cause the test case to not be executed.


    [setup]


    install this-is-an-existing-file-in-same-dir-as-test-case.txt

    dir first/second/third

    file in/a/dir/file-name.txt <<EOF
    contents of the file
    EOF

    dir root-dir-for-act-phase

    cd root-dir-for-act-phase
    # This will be current directory for the "act" phase. 

    stdin <<EOF
    this will be stdin for the program in the "act" phase
    EOF
    # (It is also possible to have stdin redirected to an existing file.)

    env MY_VAR = 'value of my environment variable'

    env unset VARIABLE_THAT_SHOULD_NOT_BE_SET

    run my-prog--located-in-same-dir-as-test-case--that-does-some-more-setup 'with an argument'


    [act]


    the-system-under-test


    [before-assert]


    cd ..
    # Moves back to the original current directory.

    shell sort root-dir-for-act-phase/output-from-sut.txt > sorted.txt


    [assert]


    exitcode != 0

    stdout <<EOF
    This is the expected output from the-system-under-test
    EOF

    stderr empty

    contents a-file.txt empty

    contents a-second-file.txt ! empty

    contents another-file.txt --with-replaced-env-vars expected-content.txt

    type actual-file directory

    cd this-dir-is-where-we-should-be-for-the-following-assertions

    run my-prog--located-in-same-dir-as-test-case--that-does-some-assertions


    [cleanup]


    shell umount my-test-mount-point

    run my-prog-that-removes-database 'my test database'


[act] is the default phase
--------------------------


``[act]`` is not needed to indicate what is being checked, since the "act" phase is the default phase.
 
The following is a valid test case,
and if run by ``exactly``, it won't remove anything (since it is executed inside a temporary sandbox directory)::

    /bin/rm -rf *


Print output from the tested program
------------------------------------


If ``--act`` is used, the output of the tested program (the "act" phase) will become the output of ``exactly`` -
stdout, stderr and exit code.

The test case is executed in a sandbox, as usual.


Keeping the sandbox directory for later inspection
--------------------------------------------------


If ``--keep`` is used, the sandbox directory will not be deleted, and its name will be printed.

This can be used to inspect the outcome of the "setup" phase, e.g.


TEST SUITES
===========


Tests can be grouped in suites::


    [cases]

    helloworld.case
    *.case
    **/*.case
    

    [suites]

    subsuite.suite
    *.suite
    pkg/suite.suite
    **/*.suite


If the file ``mysuite.suite`` contains this text, then ``exactly`` can run it::

  $ exactly suite mysuite.suite


HELP
====


Use ``exactly --help`` or ``exactly help`` to get brief help.

``exactly help help`` displays a summary of help options.

``exactly help instructions`` lists the instructions that are available in each "phase".

``exactly help htmldoc`` outputs html that is an introduction and reference to the program.


EXAMPLES
========


The ``examples/`` directory of the source distribution contains examples.


INSTALLING
==========


``exactly`` is written entirely in Python and does not require any external libraries.

``exactly`` requires Python >= 3.4 (not tested on earlier version of Python 3).

Use ``pip`` to install::

    $ pip install exactly

The program can also be run from a source distribution::

    $ python3 src/default-main-program-runner.py


DEVELOPMENT STATUS
==================


Current version is fully functional, but syntax of test cases and instructions are experimental.

Comments are welcome!


AUTHOR
======


Emil Karlén

emil@member.fsf.org
