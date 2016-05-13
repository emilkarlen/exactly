Tests a command line program by executing it in a temporary sandbox directory and inspecting its result.

Supports individual test cases and test suites.


# TEST CASES


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


"PASS" means that the two assertions were satisfied.

It also means is that the action to check - the 'helloworld' program -
is is found in the same directory as the test case file,
and also that it behaved as expected.


The following test case displays a potpurri of functionality. (Beware that this test case does not make sense! -
it just displays some of `exactly`'s functionality.)


    [conf]


    mode SKIP
    # This will case the test case to not be executed.


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


#### [act] is the default phase


`[act]` is not needed to indicate what is being checked, since the "act" phase is the default "phase".
 
The following is a valid test case,
and if run by `exactly`, it won't remove anything (since it is executed inside a temporary sandbox directory):

    /bin/rm -rf *


#### Print output from the tested program


If `--act` is used, the output of the tested program (the "act" phase) will become the output of `exactly` -
stdout, stderr and exit code.

The test case is executed in the sandbox, as usual.


#### Keeping the sandbox directory for later inspection


If `--keep` is used, the sandbox directory will not be deleted, and its name will be printed. 

This can be used to inspect the outcome of the "setup" phase, e.g.


# TEST SUITES


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


# HELP


The help system is fully functional, but some parts of the documentation are incomplete.

Use `---help` and `help ITEM` to get help.

`help help` displays a summary of help items.

`help instructions` lists the instructions that are available in each "phase".

`help htmldoc` generates a html file that is an introduction and reference to the program.


# EXAMPLES


See the `examples/` directory for examples.


# BUILDING, TESTING, INSTALLING


`exactly` is python program, and requires Python >= 3.4 (not tested on earlier version of Python 3).

The "setuptools" python package must be installed in order to build and install in the normal way.

    python3 setup.py build

    sudo python3 setup.py install


`exactly` can also be run directly from sources:

    python3 src/main-program-executor-for-test.py


To run `exactly`'s test suite:

    python3 test/run-test-suite.py

To run the test suite towards an installed program:

    python3 test/run-test-suite-towards-installed-program.py


# DEVELOPMENT STATUS


Current version is fully functional, but syntax of test cases and instructions may change.

Comments are welcome!


# AUTHOR


Emil Karlén

emil@member.fsf.org
