from shellcheck_lib.help.program_modes.test_case.contents.main.setup import Setup
from shellcheck_lib.util.textformat.parse import normalize_and_parse
from shellcheck_lib.util.textformat.structure.structures import para, literal_layout


def introduction_documentation(setup: Setup) -> list:
    return ([
                para(a_test_case_is_a_plain_text_file),
                literal_layout(example_test_case)
            ] +
            normalize_and_parse(description.format(phase=setup.phase_names))
            )


a_test_case_is_a_plain_text_file = 'A test case is written as plain text file:'

example_test_case = """\
[act]

helloworld

[assert]

exitcode 0

stdout <<EOF
Hello, World!
EOF\
"""

description = """\
A test case file contains a sequence of “phases”.


The {phase[act]} phase contains the program/action to test.


By default, the {phase[act]} phase must contain a single command line.

(For other options, see help for {phase[act]} phase.)


All other phases contain “instructions”.
E.g., “exitcode” and “stdout” are instructions of the {phase[assert]} phase.


The {phase[act]} phase is mandatory. All other phases are optional.


Executing a test case means “executing” all of it’s phases.


The phases are always executed in the same order,
regardless of the order they appear in the test case file.
"""
