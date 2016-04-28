Tests a command line program by executing it in a temporary sandbox directory and inspecting its result.


Current version is fully functional, and has a lot of features, including a help system.
But syntax may change in the future.

`exactly` is python program, and requires Python >= 3.4 (not tested on earlier version of Python 3).


Test Cases
==========


A test case is written as a plain text file:

    [act]

    helloworld

    [assert]

    exitcode 0

    stdout <<EOF
    Hello, World!
    EOF


If the file 'helloworld.case' contains this test case, then `exactly` can execute it:


    > exactly helloworld.case
    PASS


"PASS" means that all assertions were satisfied.

What this means is that the action to check - the 'helloworld' program - is in fact an executable program,
and that this program is found in the same directory as the test case file,
and also that it behaved as expected.


The following test case displays a potpurri of functionality. It does not make sense! but displays
what is currently supported.


    [conf]


    mode SKIP
    # This will case the test case to not be executed.


    [setup]


    install this-is-an-existing-file-in-same-dir-as-test-case.txt

    dir first/second/third

    file in/a/dir/file-name.txt <<EOF
    contents of the file
    <<EOF

    dir root-dir-for-act-phase

    pwd root-dir-for-act-phase
    # This will be PWD for the "act" phase. 

    stdin <<EOF
    this will be stdin for the program in the "act" phase
    EOF
    # (It is also possible to have stdin redirected to an existing file.)

    env MY_VAR = 'value of my environment variable'

    env unset VARIABLE_THAT_SHOULD_NOT_BE_SET

    run my-prog-in-same-dir-as-test-case-that-does-some-more-setup


    [act]


    the-system-under-test


    [before-assert]


    pwd ..
    # Moves back to the original PWD.

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

    pwd this-dir-is-where-we-should-be-for-the-following-assertions

    run my-prog-in-same-dir-as-test-case-that-does-some-assertions


    [cleanup]


    shell umount my-test-mount-point

    run my-prog-that-removes-database 'my test database'


[act] is the default phase
--------------------------

The [act] is not needed to indicate what is being checked, since [act] is the default "phase".
 
The following is a valid test case,
and if run by `exactly`, it won't remove anything (since it is executed inside a temporary sandbox directory):

    /bin/rm -rf *


Test Suites
===========


Tests can be grouped in suites:


    [cases]

    helloworld.case
    *.case
    **/*.case
    

    [suites]

    subsuite.suite
    *.suite
    pkg/suite.suite
    **/*.suite


Run a suite using `exactly suite mysuite.suite`


Help
====


The help system is fully functional, but some parts are incomplete.

Use `---help` and `help ...` to get help.

`help help` displays a summary of help options.

`help instructions` lists the instructions that are available in each "phase".

`help htmldoc` generates a html file that is an introduction to the program.


Installation, examples and testing
==================================

Install using setuptools (`python3 setup.py build; sudo python3 setup.py install`).

(The "setuptools" python package must be installed.)

See the `examples/` directory for examples.

To run `exactly`'s test suite:

    python3 test/run-test-suite.py

To run the test suite towards an installed program:

    python3 test/run-test-suite-towards-installed-program.py
