Tests a command line program by executing it in a temporary sandbox directory and inspecting its result.

Supports individual test cases and test suites.

Exactly has a `Wiki
<https://github.com/emilkarlen/exactly/wiki>`_,
and an `introduction by examples
<https://github.com/emilkarlen/exactly/wiki/Exactly-by-example>`_.

It also has a `Reference manual
<http://htmlpreview.github.io/?https://raw.githubusercontent.com/wiki/emilkarlen/exactly/Reference.html>`_.


TEST CASES
==========

A test case is written as a plain text file::

    [setup]

    stdin an-address-book.txt

    [act]

    addressbook --get-email-of --name 'Test Testingson'

    [assert]

    exitcode 0

    stdout equals <<EOF
    expected@email.org
    EOF


If the file 'addressbook.case' contains this test case, then Exactly can execute it::


    > exactly addressbook.case
    PASS


"PASS" means that the two assertions were satisfied.

This test assumes that

 * the system under test - the ``addressbook`` program - is is found in the same directory as the test case file
 * the file "an-address-book.txt" (that is referenced from the test case) is found in the same directory as the test case file

The ``home`` instruction can be used to change the directory where Exactly looks for files referenced from the test case.


Using shell commands
--------------------

Shell commands can be used both in the "act" phase (the system under test), and in other phases.

::

    [act]

    $ echo ${PATH}

    [assert]

    cd --rel-result
    $ tr ':' '\n' < stdout | grep '^/usr/local/bin$'


A shell command in the "assert" phase becomes an assertion that depends on the exit code
of the command.


[act] is the default phase
--------------------------


``[act]`` is not needed to indicate what is being checked, since the "act" phase is the default phase.
 
The following is a valid test case,
and if run by Exactly, it won't remove anything, since it is executed inside a temporary sandbox directory::

    $ rm -rf *


Print output from the tested program
------------------------------------


If ``--act`` is used, the output of the "act" phase (the tested program) will become the output of ``exactly`` -
stdout, stderr and exit code.
::

    $ echo Hello World

    [assert]

    stdout contains Hello

::

    > exactly --act hello-world.case
    Hello World


The test case is executed in the sandbox, as usual.

Keeping the sandbox directory for later inspection
--------------------------------------------------


If ``--keep`` is used, the sandbox directory will not be deleted, and its name will be printed.

This can be used to inspect the outcome of the "setup" phase, e.g::

    [setup]

    dir  my-dir
    file my-file.txt

    [act]

    my-prog my-file.txt

    [assert]

    exitcode 0

::

    > exactly --keep my-test.case
    /tmp/exactly-1strbro1

    > find /tmp/exactly-1strbro1
    /tmp/exactly-1strbro1
    /tmp/exactly-1strbro1/tmp
    /tmp/exactly-1strbro1/tmp/user
    /tmp/exactly-1strbro1/tmp/internal
    /tmp/exactly-1strbro1/testcase
    /tmp/exactly-1strbro1/act
    /tmp/exactly-1strbro1/act/my-dir
    /tmp/exactly-1strbro1/act/my-file.txt
    /tmp/exactly-1strbro1/result
    /tmp/exactly-1strbro1/result/exitcode
    /tmp/exactly-1strbro1/result/stderr
    /tmp/exactly-1strbro1/result/stdout
    /tmp/exactly-1strbro1/log

The ``act/`` directory is the current directory when the test starts.
The ``file`` instruction has put the file ``my-file.txt`` there.

The result of the "act" phase is saved in the ``result/`` directory.

``tmp/user/`` is a directory where the test can put temporary files.

TEST SUITES
===========


Tests can be grouped in suites::


    first.case
    second.case

or::

    [cases]

    helloworld.case
    *.case
    **/*.case
    

    [suites]

    subsuite.suite
    *.suite
    pkg/suite.suite
    **/*.suite


If the file ``mysuite.suite`` contains this text, then Exactly can run it::

  > exactly suite mysuite.suite
  ...
  OK


The result of a suite can also be reported as JUnit XML, by using ``--reporter junit``.


HELP
====


Use ``exactly --help`` or ``exactly help`` to get brief help.

``exactly help help`` displays a summary of help options.

``exactly help instructions`` lists the instructions that are available in each "phase".

``exactly help htmldoc`` outputs html that is an introduction and reference to the program.


EXAMPLES
========

The ``examples/`` directory of the source distribution contains examples.

A complex example
-----------------

The following test case displays a potpurri of features. (Beware that this test case does not make sense! -
it just displays some of Exactly's features.)
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

    run --python --interpret custom-setup.py 'with an argument'

    run ( --python -c ) --source print('Setting up things...')


    [act]


    the-system-under-test


    [before-assert]


    cd ..
    # Moves back to the original current directory.

    $ sort root-dir-for-act-phase/output-from-sut.txt > sorted.txt


    [assert]


    exitcode != 0

    stdout equals <<EOF
    This is the expected output from the-system-under-test
    EOF

    stdout --with-replaced-env-vars contains 'EXACTLY_ACT:[0-9]+'

    stderr empty

    contents a-file.txt empty

    contents a-second-file.txt ! empty

    contents another-file.txt --with-replaced-env-vars equals expected-content.txt

    contents file.txt contains 'my .* reg ex'

    type actual-file directory

    cd this-dir-is-where-we-should-be-for-the-following-assertions

    run my-prog--located-in-same-dir-as-test-case--that-does-some-assertions

    run --python --interpret custom-assertion.py


    cd --rel-result
    # Changes to the directory where the result of the act phase is stored (exitcode, stdout, stderr)

    $ sed '1,10d' stdout > modified-stdout.txt
    contents modified-stdout.txt equals <<EOF
    this should be the single line of modified-stdout.txt
    EOF


    [cleanup]


    $ umount my-test-mount-point

    run my-prog-that-removes-database 'my test database'


INSTALLING
==========


Exactly is written entirely in Python and does not require any external libraries.

Exactly requires Python >= 3.5 (not tested on earlier version of Python 3).

Use ``pip`` or ``pip3`` to install::

    > pip install exactly

or::

    > pip3 install exactly

The program can also be run from a source distribution::

    > python3 src/default-main-program-runner.py


DEVELOPMENT STATUS
==================


Current version is fully functional, but syntax and semantics are experimental.

Comments are welcome!


AUTHOR
======


Emil Karlén

emil@member.fsf.org


DEDICATION
==========


Aron Karlén

Tommy Karlsson
