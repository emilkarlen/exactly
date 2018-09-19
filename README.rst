Tests a command line program by executing it in a temporary sandbox directory and inspecting its result.

Or tests properties of existing files, directories etc.


Supports individual test cases and test suites.

Exactly has a `Wiki
<https://github.com/emilkarlen/exactly/wiki>`_,
and an `introduction by examples
<https://github.com/emilkarlen/exactly/wiki/Exactly-by-example>`_.

It also has a built in help system,
which can, among other things,
generate this `Reference manual
<http://htmlpreview.github.io/?https://raw.githubusercontent.com/wiki/emilkarlen/exactly/Reference.html>`_.


.. contents::


TEST CASES
========================================

A test case is written as a plain text file.


Testing stdin, stdout, stderr, exit code
------------------------------------------------------------

The following checks that your new ``my-contacts-program`` reads a contact list from stdin,
and is able to find the email of a person::

    [setup]

    stdin = -file some-test-contacts.txt

    [act]

    my-contacts-program get-email-of --name 'Pablo Gauss'

    [assert]

    exit-code == 0

    stdout equals <<EOF
    pablo@gauss.org
    EOF

    stderr empty


If the file 'contacts.case' contains this test case, then Exactly can execute it::


    > exactly contacts.case
    PASS


"PASS" means that all assertions were satisfied.

This test assumes that

 * the system under test - ``my-contacts-program`` - is is found in the same directory as the test case file
 * the file "some-test-contacts.txt" (that is referenced from the test case) is found in the same directory as the test case file

The ``home`` and ``act-home`` instructions
can be used to change the directories where Exactly looks for files referenced from the test case.


Testing side effects on files and directories
------------------------------------------------------------

When the execution of a test case starts,
the current directory is set to a temporary directory.
This gives the test case a sandbox where it can create and manipulate files.

The sandbox - and all files within it - are removed when the execution ends.


The following tests a program that classifies
files as either good or bad, by moving them to the
appropriate directory::

    [setup]

    dir input
    dir output/good
    dir output/bad

    file input/a.txt = <<EOF
    GOOD contents
    EOF

    file input/b.txt = <<EOF
    bad contents
    EOF

    [act]

    classify-files-by-moving-to-appropriate-dir GOOD input/ output/

    [assert]

    dir-contents input empty

    exists -file output/good/a.txt
    dir-contents output/good num-files == 1

    exists -file output/bad/b.txt
    dir-contents output/bad num-files == 1


``file`` and ``dir`` makes files in the current directory (by default).


Using predefined source files
------------------------------------------------------------

The *home directory structure* is directories containing
predefined files involved in a test case:

*act-home*
 Location of the program file being tested

*home*
  Location of arbitrary test resources


Both of them defaults to the directory
that contains the test case file,
but can be changed via ``[conf]``.


There are options for making paths relative to them,
and also to the temporary sandbox directories.

``-rel-home`` refers to the *home* directory,
and ``-rel-act`` to the temporary directory
that is the current directory at the start of the execution::


    [conf]

    act-home = ../bin/

    home     = data/

    [setup]

    copy  -rel-home input.txt  -rel-act actual.txt

    [act]

    filter-lines "text to find" actual.txt

    [assert]

    contents -rel-act actual.txt
             equals
             -file -rel-home expected.txt


These "relativity" options have defaults designed to minimize the
need for them.
The following case does the same thing as the one above::

    [conf]

    act-home = ../bin/

    home     = data/

    [setup]

    copy input.txt actual.txt

    [act]

    filter-lines "text to find" actual.txt

    [assert]

    contents actual.txt
             equals
             -file expected.txt


Testing and transforming the contents of files
------------------------------------------------------------

Use ``contents`` to test the contents of a file,
or a transformed version of it,
by applying a "string transformer".

Such a "string transformer" may be given a name
using the ``def`` instruction
to make the test easier to read.

The following case
tests that "timing lines" are output as part of a log file "log.txt".

The challenge is that the (fictive) log file contains
non-timing lines that we are not interested in,
and that timing lines contains a time stamp of the form
"NN:NN", who's exact value we are also not interested in.

A "string transformer" is used to extract all timing lines
and to replace "NN:NN" time stamps with the constant string ``TIMESTAMP``::


    [setup]

    def line-matcher       IS_TIMING_LINE     = regex ^timing

    def string-transformer REPLACE_TIMESTAMPS = replace [0-9]{2}:[0-9]{2} TIMESTAMP

    def string-transformer GET_TIMING_LINES   = select IS_TIMING_LINE | REPLACE_TIMESTAMPS

    [act]

    $ python @[EXACTLY_HOME]@/program-that-writes-log-file.py

    [assert]

    contents log.txt -transformed-by GET_TIMING_LINES equals <<EOF
    timing TIMESTAMP begin
    timing TIMESTAMP preprocessing
    timing TIMESTAMP validation
    timing TIMESTAMP execution
    timing TIMESTAMP end
    EOF


The ``-transformed-by`` option does not modify the tested file,
it just applies the assertion to a transformed version of it.



Using external helper programs
------------------------------------------------------------

External programs can with help with setup and assertions etc.

Exactly can run executable files, shell commands  and programs in the OS PATH,
using ``run``, ``$``, ``%``.

The following case shows some examples, but doesn't make sense tough::

    [setup]

    run my-setup-helper-program first "second arg"

    run % mysql -uu -pp -hlocalhost -Dd --batch --execute "create table my_table(id int)"

    $ touch file

    file root-files.txt = -stdout-from $ ls /

    [act]

    $ echo ${PATH}

    [assert]

    run my-assert-helper-program

    $ test -f root-files.txt

    stdout -from
           % echo 'Interesting output'
           equals
    <<EOF
    Interesting output
    EOF

    [cleanup]

    run % mysql -uu -pp -hlocalhost -Dd --batch --execute "drop table my_table"


A program executed in ``[assert]`` becomes an assertion that depends on the exit code.


Program values can be defined for reuse using ``def`` and run using ``@``::

    [setup]

    def program RUN_MYSQL   = % mysql -uu -pp -hlocalhost -Dd
    def program EXECUTE_SQL = @ RUN_MYSQL --skip-column-names --batch --execute


    run @ EXECUTE_SQL "create table my_table(id int)"

    [act]

    system-under-test

    [assert]

    stdout -from
           @ EXECUTE_SQL "select * from my_table"
           ! empty

    [cleanup]

    run @ EXECUTE_SQL "drop table my_table"


Testing source code files
-------------------------

The ``actor`` instruction can specify an interpreter to test a source code file::

    [conf]

    actor = -file python

    [act]

    my-python-program.py 'an argument' second third

    [assert]

    stdout equals
    <<EOF
    Argument: an argument
    Argument: second
    Argument: third
    EOF



Experimenting with source code
------------------------------

The "source interpreter" actor treats the contents of the "act" phase as source code.
It's probably most useful as a tool for experimenting::

    [conf]

    actor = -source bash

    [act]

    var='hello world'
    echo ${var:5}

    [assert]

    stdout equals <<EOF
    world
    EOF

or for running a source file in a sandbox::

    > exactly --actor bash my-script.sh
    PASS


This is more useful combined with ``--act`` (see below).


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

    stdout any line : matches regex Hello

::

    > exactly --act hello-world.case
    Hello World


The test case is executed in a sandbox, as usual.
And all phases are executed, not just the "act" phase.
But the outcome of tha "assert" phase is ignored.


Keeping the sandbox directory for later inspection
--------------------------------------------------


If ``--keep`` is used, the sandbox directory will not be deleted, and its name will be printed.

This can be used to inspect the outcome of the "setup" phase, e.g::

    [setup]

    file my-file.txt

    file -rel-tmp my-tmp-file.txt

    dir  my-dir

    cd my-dir

    [act]

    hello-world -o output-from-action-to-check.txt

    [assert]

    exit-code == 0

::

    > exactly --keep my-test.case
    /tmp/exactly-68jn8c08
    PASS

    > find /tmp/exactly-68jn8c08
    /tmp/exactly-68jn8c08/
    /tmp/exactly-68jn8c08/act/
    /tmp/exactly-68jn8c08/act/my-file.txt
    /tmp/exactly-68jn8c08/act/my-dir/
    /tmp/exactly-68jn8c08/act/my-dir/output-from-action-to-check.txt
    /tmp/exactly-68jn8c08/tmp/
    /tmp/exactly-68jn8c08/tmp/my-tmp-file.txt
    /tmp/exactly-68jn8c08/result/
    /tmp/exactly-68jn8c08/result/stdout
    /tmp/exactly-68jn8c08/result/stderr
    /tmp/exactly-68jn8c08/result/exitcode
    /tmp/exactly-68jn8c08/internal/
    /tmp/exactly-68jn8c08/internal/tmp/
    /tmp/exactly-68jn8c08/internal/testcase/
    /tmp/exactly-68jn8c08/internal/log/

The ``act/`` directory is the current directory when the test starts.
The ``file`` instruction has put the file ``my-file.txt`` there.

The result of the "act" phase is saved in the ``result/`` directory.

``tmp/`` is a directory where the test can put temporary files.

TEST SUITES
========================================


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


If the file ``my-suite.suite`` contains this text, then Exactly can run it::

  > exactly suite my-suite.suite
  ...
  OK


The result of a suite can also be reported as JUnit XML, by using ``--reporter junit``.


HELP
========================================


Exactly has a built in help system.


Use ``exactly --help`` or ``exactly help`` to get brief help.

``exactly help help`` displays a summary of help options.

``exactly help instructions`` lists the instructions that are available in each "phase".

``exactly help htmldoc`` outputs all built in help as html, which serves as Exactly's reference manual.


EXAMPLES
========================================

The ``examples/`` directory of the source distribution contains examples.

A complex example
-----------------

The following test case displays a potpurri of features. (Beware that this test case does not make sense! -
it just displays some of Exactly's features.)
::

    [conf]


    status = SKIP
    # This will cause the test case to not be executed.


    [setup]


    copy this-is-an-existing-file-in-same-dir-as-test-case.txt

    dir first/second/third

    file in/a/dir/file-name.txt = <<EOF
    contents of the file
    EOF

    file output-from-git.txt = -stdout $ git status

    file git-branch-info.txt = -stdout
                               $ git status
                               -transformed-by select line-num == 1

    dir root-dir-for-act-phase

    cd root-dir-for-act-phase
    # This will be current directory for the "act" phase.

    stdin = <<EOF
    this will be stdin for the program in the "act" phase
    EOF
    # (It is also possible to have stdin redirected to an existing file.)

    env MY_VAR = 'value of my environment variable'

    env PATH   = '${PATH}:/my-dir'

    env unset VARIABLE_THAT_SHOULD_NOT_BE_SET

    run my-prog--located-in-same-dir-as-test-case--that-does-some-more-setup 'with an argument'

    run -python -existing-file custom-setup.py 'with an argument'

    run -python -c :> print('Setting up things...')


    [act]


    the-system-under-test


    [before-assert]


    cd ..
    # Moves back to the original current directory.

    $ sort root-dir-for-act-phase/output-from-sut.txt > sorted.txt


    [assert]


    exit-code != 0

    stdout equals <<EOF
    This is the expected output from the-system-under-test
    EOF

    stdout -transformed-by REPLACE_TEST_CASE_DIRS
           any line : matches regex 'EXACTLY_ACT:[0-9]+'

    stderr empty

    contents a-file.txt empty

    contents a-second-file.txt ! empty

    contents another-file.txt
             -transformed-by REPLACE_TEST_CASE_DIRS
             equals -file expected-content.txt

    contents file.txt any line : matches regex 'my .* reg ex'

    exists actual-file

    exists -dir actual-file

    cd this-dir-is-where-we-should-be-for-the-following-assertions

    run my-prog--located-in-same-dir-as-test-case--that-does-some-assertions

    run -python -existing-file custom-assertion.py


    file -rel-tmp modified-stdout.txt = -file -rel-result stdout
                                        -transformed-by select line-num >= 10

    contents -rel-tmp modified-stdout.txt
             equals
    <<EOF
    this should be line 10 of original stdout.txt
    this should be line 11 of original stdout.txt
    EOF


    stdout  -transformed-by ( select line-num >= 10 )
            equals
    <<EOF
    this should be line 10 of original stdout.txt
    this should be line 11 of original stdout.txt
    EOF


    [cleanup]


    $ umount my-test-mount-point

    run my-prog-that-removes-database 'my test database'


INSTALLING
========================================


Exactly is written in Python and does not require any external libraries.

Exactly requires Python >= 3.5 (not tested on earlier version of Python 3).

Use ``pip`` or ``pip3`` to install::

    > pip install exactly

or::

    > pip3 install exactly

The program can also be run from a source distribution::

    > python3 src/default-main-program-runner.py


DEVELOPMENT STATUS
========================================


Current version is fully functional, but syntax and semantics are experimental.

Comments are welcome!


AUTHOR
========================================


Emil Karlén

emil@member.fsf.org


THANKS
========================================


The Python IDE
`PyCharm
<https://www.jetbrains.com/pycharm/>`_
from
`JetBrains
<https://www.jetbrains.com/>`_
has greatly helped the development of this software.


DEDICATION
========================================


Aron Karlén

Tommy Karlsson

Götabergsgatan 10, lägenhet 4
