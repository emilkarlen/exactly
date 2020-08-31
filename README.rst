Tests a command line program by executing it in a temporary sandbox directory and inspecting its result.

Or tests properties of existing files, directories etc.

Supports individual test cases and test suites.

Support for referencing predefined files and files created in the temporary sandbox.

Exactly has a  built in help system,
which can, among other things,
generate this `Reference manual
<https://emilkarlen.github.io/exactly/version/next/reference-manual.html>`_.


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


If the file 'contacts.case' contains this test case, then Exactly can execute it:

.. parsed-literal::
   :class: terminal

    > exactly contacts.case
    **PASS**


"PASS" means that all assertions were satisfied.


If the actual email address of "Pablo Gauss" is not the expected one,
then Exactly will *report failure*. For example:

.. parsed-literal::
   :class: terminal

    > exactly contacts.case
    **FAIL**
    In [assert]
    contacts.case, line 13

      stdout equals <<EOF
      pablo\@gauss.org
      EOF


    Unexpected contents of stdout from [act]

      @[EXACTLY_RESULT]@/stdout


    **(F) equals**
          *Expected*
            STRING
              'pablo\@gauss.org\\n'
          *Diff*
    --- Expected

    +++ Actual

    @@ -1 +1 @@

    -pablo\@gauss.org

    +pablo.gauss\@masters.org


This test assumes that

 * the system under test - ``my-contacts-program`` - is is found in the same directory as the test case file
 * the file "some-test-contacts.txt" (that is referenced from the test case) is found in the same directory as the test case file

.. note:: The ``home`` and ``act-home`` instructions can be used to change the directories where Exactly looks for files referenced from the test case.


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

    file input/a.txt     = 'GOOD contents'
    file input/b.txt     = 'bad contents'
    file input/sub/c.txt = 'more bad contents'

    dir output/good
    dir output/bad

    [act]

    classify-files-by-moving-to-appropriate-dir GOOD input/ output/

    [assert]

    dir-contents input        empty

    dir-contents output/good  matches -full { a.txt : type file }

    dir-contents output/bad   matches -full
        {
            b.txt : type file
            sub   : type dir && dir-contents matches -full
                    {
                        c.txt : type file
                    }
        }


``file`` and ``dir`` makes files in the current directory (by default).


Referencing files
------------------------------------------------------------

The **home directory structure** is directories containing
predefined files involved in a test case:

*act-home*
 Location of the program file being tested

*home*
  Location of arbitrary test resources


Both of them defaults to the directory
that contains the test case file,
but can be changed via ``[conf]``.


The **sandbox directory structure** is temporary directories for
files involved in a single execution of a test case:

*act*
 The current directory, when execution begins

*result*
  Stores the output from the tested program

*tmp*
  A directory for arbitrary temporary files


There are options for making paths relative to all of these.

``-rel-home`` refers to the *home* directory,
and ``-rel-act`` to the *act* directory, for example::


    [conf]

    act-home = ../bin/

    home     = data/

    [setup]

    copy  -rel-home input.txt  -rel-act actual.txt

    [act]

    my-grep-tool "text to find" actual.txt

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

    my-grep-tool "text to find" actual.txt

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

    def string-transformer GET_TIMING_LINES   = filter IS_TIMING_LINE | REPLACE_TIMESTAMPS

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



Using external programs
------------------------------------------------------------

External programs can help with setup, assertions etc.

Exactly can run executable files, shell commands and programs in the OS PATH,
using ``run``, ``$``, ``%``.

The following case shows some examples, but *doesn't make sense* tough::

    [setup]

    run my-setup-helper-program first "second arg"

    def list DB_ARGS = -uu -pp -hlocalhost -Dd

    run % mysql @[DB_ARGS]@ --batch --execute "create table my_table(id int)"

    def list MYSQL_BATCH = @[DB_ARGS]@ --batch --execute

    file interesting-records.txt =
         -stdout-from
          % mysql @[MYSQL_BATCH]@ :> select * from a_table where name = "interesting"

    $ touch file

    file root-files.txt =
         -stdout-from
          % ls /
          -transformed-by
              run my-string-transformer-program

    run  -ignore-exit-code  % stat optional-file.txt

    [act]

    $ echo ${PATH} > output.txt

    [assert]

    run my-assert-helper-program

    $ test -f root-files.txt

    exists output.txt : (
           type file
           &&
           run -python @[EXACTLY_HOME]@/my-file-matcher.py arg1
           &&
           contents run -python @[EXACTLY_HOME]@/my-string-matcher.py arg1 "arg 2"
           )

    stdout -from
           $ echo 'Interesting output'
           equals
    <<EOF
    Interesting output
    EOF

    [cleanup]

    run % mysql @[MYSQL_BATCH]@ :> drop table my_table


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

    run @ EXECUTE_SQL :> drop table my_table


Testing existing OS environment - tests without ``[act]``
----------------------------------------------------------------------

A test case does not need to have an ``[act]`` phase.
This way, Exactly can be used to check existing files and directories, for example.

The following case checks your hierarchy of software projects.

The projects are rooted at the directory 'my-projects'.
Each 'project' sub directory contains a project,
and must contain a 'Makefile' with a target 'all'::

    [assert]

    exists @[MY_PROJECTS_ROOT_DIR]@ : type dir && @[ALL_PROJECT_DIRS_ARE_VALID]@

    [setup]

    def path   MY_PROJECTS_ROOT_DIR = -rel-act-home my-projects
    def string MY_PROJECT_DIR_NAME  = project

    def file-matcher IS_VALID_MAKEFILE =

        type file &&
        contents
          -transformed-by
            filter matches '^all:'
            num-lines == 1


    def file-matcher IS_VALID_PROJECT_DIR =

        type dir &&
        dir-contents
           matches { Makefile : @[IS_VALID_MAKEFILE]@ }


    def file-matcher ALL_PROJECT_DIRS_ARE_VALID =

        dir-contents -recursive
          -selection name @[MY_PROJECT_DIR_NAME]@
            every file : @[IS_VALID_PROJECT_DIR]@


Testing source code files
-------------------------

The ``actor`` instruction can specify an interpreter to test a source code file::

    [conf]

    actor = -file % python

    [act]

    my-python-program.py 'an argument' second third

    [assert]

    stdout equals
    <<EOF
    Argument: an argument
    Argument: second
    Argument: third
    EOF


Testing source code
-------------------------

The ``actor`` instruction can specify an interpreter to test source code in ``[act]``::

    [conf]

    actor = -source % python

    [act]

    import sys
    sys.stdout.write('Hello\n')
    sys.stdout.write('world!\n')

    [assert]

    stdout equals
    <<-
    Hello
    world!
    -


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


.. parsed-literal::
   :class: terminal

    > exactly --act my-test.case
    a-dir
    a-file


The test case is executed in a temporary sandbox, as usual,
but assertions are ignored.


Testing a git commit hook
------------------------------------------------------------

The following tests a git commit hook (`prepare-commit-msg`).

The hook should add the issue id in the branch name,
to commit messages::

    [setup]


    def string ISSUE_ID            = ABC-123
    def string MESSAGE_WO_ISSUE_ID = "commit message without issue id"

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

    $ git checkout -b "@[ISSUE_ID]@-branch-with-issue-id"

    file file-to-add = "A file to add on the branch"

    $ git add file-to-add


    [act]


    $ git commit -m "@[MESSAGE_WO_ISSUE_ID]@"


    [assert]


    stdout -from
           @ GET_LOG_MESSAGE_OF_LAST_COMMIT
           equals
    <<-
    @[ISSUE_ID]@ : @[MESSAGE_WO_ISSUE_ID]@
    -


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



If the file ``my-suite.suite`` contains this text, then Exactly can run it:

.. parsed-literal::
   :class: terminal

    > exactly suite my-suite.suite
    ...
    **OK**


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

Use ``pip`` or ``pip3`` to install:

.. parsed-literal::
   :class: terminal

    > pip3 install exactly

The program can also be run from a source distribution:

.. parsed-literal::
   :class: terminal

    > python3 src/default-main-program-runner.py


DEVELOPMENT STATUS
========================================


Current version is fully functional, but some syntax and semantics is inconsistent:

* Some instructions allow arguments to span multiple lines, some do not.
* Support for escapes characters in strings is missing.

Incompatible changes to syntax and semantics may occur in every 0.x release.


Comments are welcome!


Future development
------------------------------------

More functionality is needed, smaller and larger.
Including (but not limited to):

* Possibility to set stdin for processes other than the "action to check"
* Separate sets of environment variables for "action to check" and other processes
* Improved string character escaping
* Type `REG-EX`
* Type `INTEGER-MATCHER`
* Support for non-terminating programs (e.g. as ``string-transformer``)
* Symbol substitution in files
* Dynamic symbol values - e.g. contents of dir, current date
* Macros and functions
* More string transformers, matchers, etc
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


Thanks for the great

* Python language
* GNU/Linux
* GNU Emacs
* git
* Docker
* Rembrandt Harmenszoon van Rijn's "De Staalmeesters"


DEDICATION
========================================


Aron Karlén

Tommy Karlsson

Götabergsgatan 10, lägenhet 4
