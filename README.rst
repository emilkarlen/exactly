Tests a command line program by executing it in a temporary sandbox directory and inspecting its result.

Or tests properties of existing files, directories etc.


Supports individual test cases and test suites.

Exactly has a `Wiki
<https://github.com/emilkarlen/exactly/wiki>`_.
It also has a built in help system,
which can, among other things,
generate this `Reference manual
<https://emilkarlen.github.io/exactly/reference-manual.html>`_.


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

    exists output/good/a.txt : type file
    dir-contents output/good num-files == 1

    exists output/bad/b.txt : type file
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
non-timing lines that the test is not interested in,
and that timing lines contains a time stamp of the form
"NN:NN", who's exact value also is not interesting.

A "string transformer" is used to extract all timing lines
and to replace "NN:NN" time stamps with the constant string ``TIMESTAMP``::


    [setup]

    def line-matcher       IS_TIMING_LINE     = matches ^timing

    def string-transformer REPLACE_TIMESTAMPS = replace [0-9]{2}:[0-9]{2} TIMESTAMP

    def string-transformer GET_TIMING_LINES   = select IS_TIMING_LINE | REPLACE_TIMESTAMPS

    [act]

    program-that-writes-log-file

    [assert]

    contents log.txt
             -transformed-by GET_TIMING_LINES
             equals <<EOF
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


Print output from the tested program
------------------------------------


If ``--act`` is used, the output of the "act" phase (the "action to check")
will become the output of ``exactly`` -
stdout, stderr and exit code
::


    [setup]

    dir  a-dir
    file a-file

    [act]

    $ ls

    [assert]

    stdout num-lines == 314

::

    > exactly --act my-test.case
    a-dir
    a-file


The test case is executed in a temporary sandbox, as usual,
but assertions are ignored.


Testing existing OS environment - tests without ``[act]``
----------------------------------------------------------------------

A test case does not need to have an ``[act]`` phase.

For example, to just check that the names of some SQL files are correct::

    [assert]

    def path SQL_DIR = -rel-here sql

    exists @[SQL_DIR]@ : type dir


    'sql/ must only contain sql files'

    dir-contents @[SQL_DIR]@
                 -selection ! name *.sql
                 empty


Testing a git commit hook
------------------------------------------------------------

The following tests a git commit hook (`prepare-commit-msg`)::

    [setup]


    def program GET_LOG_MESSAGE_OF_LAST_COMMIT = % git log -1 --format=%s


    ## Setup a (non empty) git repo.

    $ git init

    file file-in-repo = "A file in the repo"

    $ git add file-in-repo

    $ git commit -m "commit of file already in repo"


    ## Install the commit hook to test.

    copy prepare-commit-msg .git/hooks


    ## Setup a branch, with issue number in its name,
    # and a file to commit.

    $ git checkout -b "AB-123-branch-with-issue-number"

    file file-to-add = "A file to add on the branch"

    $ git add file-to-add


    [act]


    $ git commit -m "commit message without issue number"


    [assert]


    stdout -from
           @ GET_LOG_MESSAGE_OF_LAST_COMMIT
           equals
    <<-
    AB-123 : commit message without issue number
    -


Note: Since a test is executed in a sandbox directory, it is ok
to create the git repo in CWD.

Note: Since the test is rather long, it would increase readability
to put part of it in external files, and including them using `including`.
E.g.::

    [setup]
    ...
    including repo-in-cwd-with-installed-commit-hook.setup


ORGANIZING TESTS
========================================

File inclusion
------------------------------------

Test case contents can be included from external files::

    [setup]

    including my-dir-symbols.def

    including my-common-setup-and-cleanup.xly



Test suites
------------------------------------


Tests can be grouped in suites::


    first.case
    second.case

or::

    [cases]

    helloworld.case
    *.case
    **/*.case
    

    [suites]

    sub-suite.suite
    *.suite
    pkg/suite.suite
    **/*.suite



If the file ``my-suite.suite`` contains this text, then Exactly can run it::

    > exactly suite my-suite.suite
    ...
    OK


The result of a suite can be reported as
simple progress information,
or JUnit XML.


Suites can contain test case functionality that is common
to all cases in the suite. For example::


    [cases]

    *.case

    [conf]

    act-home = ../bin/

    [setup]

    def string CONF_FILE = my.conf

    file @[CONF_FILE]@ =
    <<EOF
    common = configuration
    EOF


The common functionality is included in each test case.


MORE EXAMPLES
========================================

The ``examples/`` directory of the source distribution contains more examples.


INSTALLING
========================================


Exactly is written in Python and does not require any external libraries.

Exactly requires Python >= 3.5.4.

Use ``pip`` or ``pip3`` to install::

    > pip install exactly

or::

    > pip3 install exactly

The program can also be run from a source distribution::

    > python3 src/default-main-program-runner.py


DEVELOPMENT STATUS
========================================


Current version is fully functional, but some syntax and semantics is inconsistent:

* Some instructions allow arguments to span multiple lines, some do not.
* Most instructions interpret symbol references in arguments, some do not.
* Support for escapes characters in strings is missing.

Incompatible changes to syntax and semantics may occur in every release until v 1.0.


Comments are welcome!


Future development
------------------------------------

More functionality is needed, smaller and larger.
Including (but not limited to):

* More string transformers, file matchers etc
* Possibility to use "program" values in more places, e.g. in ``[act]``
* Improved string character escaping
* Remove setting of ``EXACTLY_...`` environment variables
* Separate sets of environment variables for "action to check" and other processes
* Possibility to set stdin for processes other than the "action to check"
* file-matcher: Add matcher: ``dir-contents``
* files-matcher: Add logical operators
* ``dir-contents``: Check contents of directory recursively.
* string-matcher: Add logical operators
* Symbol substitution in files
* Variables - corresponding to symbol definitions -
  but for variable values
* Macros and functions
* Ability to embed Python code in test cases
* Python library for running cases and suites from within Python as a DSEL


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
