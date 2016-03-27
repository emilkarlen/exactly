from shellcheck_lib.help.program_modes.test_case.contents.main.setup import Setup
from shellcheck_lib.util.textformat.parse import normalize_and_parse
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure.structures import para, literal_layout


def test_case_intro_documentation(setup: Setup) -> doc.SectionContents:
    paragraphs = ([
                      para(a_test_case_is_a_plain_text_file),
                      literal_layout(example_test_case)
                  ] +
                  normalize_and_parse(description.format(phase=setup.phase_names))
                  )
    return doc.SectionContents(paragraphs, [])


a_test_case_is_a_plain_text_file = 'A test case is written as a plain text file:'

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


The {phase[act]} phase contains the program to test.

It is the only mandatory phase.

By default, it must contain a single command line.


All other phases contain “instructions”.
E.g., “exitcode” and “stdout” are instructions of the {phase[assert]} phase.


The instructions in the {phase[assert]} phase determines the outcome of the test case.
Each of these instructions either PASS or FAIL.
If any of the instructions FAIL, then the outcome of the test case as a whole will be FAIL.
Otherwise it will be PASS.
"""
