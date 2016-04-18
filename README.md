Checks command line program by executing them in a temporary sandbox directory and inspecting the result.

UNDER CONSTRUCTION
==================

shellcheck is under construction.

Current version is fully functional, and has a lot of features, including a help system.
But syntax may change in the future.

Install using setuptools (`python3 setup.py build; sudo python3 setup.py install`).

A first version is planned to be released this year.

See the `examples/` directory for examples.

To run the test suite:

    python3 test/run-test-suite.py

To run the test suite towards an installed program:

    python3 test/run-test-suite-towards-installed-program.py


Test Cases
==========

The following test case (and more) is supported by the current version.



A test case is written as a plain text file:

    [act]

    helloworld

    [assert]

    exitcode 0

    stdout <<EOF
    Hello, World!
    EOF


If the file 'helloworld.case' contains this test case, then shellcheck can execute it:


    > shellcheck helloworld.case
    PASS


"PASS" means that all assertions were satisfied.

What this means is that the action to check - the 'helloworld' program - is in fact an executable program,
and that this program is found in the same directory as the test case file,
and also that it behaved as expected.

The "act" phase is default
--------------------------

The [act] is not needed to indicate what is being checked, since [act] is the default "phase".
 
The following is a valid shellcheck test case,
and if run by shellcheck, it won't remove anything:

    /bin/rm -rf *


Test Suites
===========


Tests can be grouped in suites:


    [cases]

    helloworld.case
    *.case
    

    [suites]

    subsuite.suite
    *.suite
    pkg/suite.suite


Run a suite using `shellcheck suite mysuite.suite`


Help
====


The help system is fully functional, but some parts are incomplete.

Use `---help` and `help ...` to get help.

`help help` displays a summary of help options.

`help instructions` lists the instructions that are available in each "phase".

`help htmldoc` generates a html file that is an introduction to the program.
