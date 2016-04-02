from shellcheck_lib.help.program_modes.test_case.contents.main.utils import Setup
from shellcheck_lib.util.textformat.parse import normalize_and_parse
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure.structures import para, literal_layout


def test_case_intro_documentation(setup: Setup) -> doc.SectionContents:
    paragraphs = ([
                      para(A_TEST_CASE_IS_A_PLAIN_TEXT_FILE),
                      literal_layout(EXAMPLE_TEST_CASE)
                  ] +
                  normalize_and_parse(DESCRIPTION.format(phase=setup.phase_names))
                  )
    return doc.SectionContents(paragraphs, [])


A_TEST_CASE_IS_A_PLAIN_TEXT_FILE = 'A test case is written as a plain text file:'

EXAMPLE_TEST_CASE = """\
[act]

helloworld

[assert]

exitcode 0

stdout <<EOF
Hello, World!
EOF\
"""

DESCRIPTION = """\
A test case file contains a sequence of “phases”.


The {phase[act]} phase contains the action to check.

It is the only mandatory phase.

By default, it must contain a single command line.


All other phases contain “instructions”.
E.g., “exitcode” and “stdout” are instructions of the {phase[assert]} phase.


The instructions in the {phase[assert]} phase determines the outcome of the test case.
Each of these instructions either PASS or FAIL.
If any of the instructions FAIL, then the outcome of the test case as a whole will be FAIL.
Otherwise it will be PASS.
"""
