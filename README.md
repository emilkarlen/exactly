Checks command line program by executing them in a temporary sandbox directory and inspecting the result.

UNDER CONSTRUCTION
==================

shellcheck is under construction.

Current version is fully functional, though, but syntax may change in the future.

Alo lacks an installer.

A first version is planned to be released before summer.

shellcheck is a Python 3 application. `src/shellcheck.py` is the man program.


Example
=======

The following test case is supported by the current version.



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
and that it printed the expected text to stdout.



Help
====

Use `---help` and `help ...` to get help.

`help help` displays a summary of help options.

`help htmldoc` generates a html file that is an introduction to the program (under construction).
