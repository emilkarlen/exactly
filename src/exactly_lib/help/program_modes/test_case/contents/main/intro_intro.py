from exactly_lib.help.program_modes.test_case.contents.main.utils import Setup
from exactly_lib.program_info import PROGRAM_NAME
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.structures import para, literal_layout


def intro_intro_documentation(setup: Setup) -> doc.SectionContents:
    format_values = {
        'test_case_file': 'helloworld.case',
        'SHELLCHECK_EXECUTABLE': PROGRAM_NAME,
        'action_to_check': 'helloworld',
        'phase': setup.phase_names
    }
    ps = []
    ps.append(para(A_TEST_CASE_IS_A_PLAIN_TEXT_FILE))
    ps.append(literal_layout(EXAMPLE_TEST_CASE.format_map(format_values)))
    ps.extend(normalize_and_parse(A_TEST_CASE_IS_EXECUTED_BY_GIVING_THE_FILE_AS_THE_SINGLE_ARGUMENT
                                  .format_map(format_values)))
    ps.append(literal_layout(EXAMPLE_EXECUTION_OF_TEST_CASE.format_map(format_values)))
    ps.extend(normalize_and_parse(EXECUTION_EXPLANATION.format_map(format_values)))
    return doc.SectionContents(ps, [])


A_TEST_CASE_IS_A_PLAIN_TEXT_FILE = 'A test case is written as a plain text file:'

EXAMPLE_TEST_CASE = """\
[act]

{action_to_check}

[assert]

exitcode 0

stdout <<EOF
Hello, World!
EOF\
"""

A_TEST_CASE_IS_EXECUTED_BY_GIVING_THE_FILE_AS_THE_SINGLE_ARGUMENT = """\
If the file '{test_case_file}' contains this test case,
then {SHELLCHECK_EXECUTABLE} can execute it:
"""

EXAMPLE_EXECUTION_OF_TEST_CASE = """\
> {SHELLCHECK_EXECUTABLE} {test_case_file}
PASS
"""

EXECUTION_EXPLANATION = """\
"PASS" means that all assertions were satisfied.


What this means is that the action to check - the '{action_to_check}' program -
is in fact an executable program, and that this program is found in
the same directory as the test case file, and that it printed the expected text to stdout.
"""
