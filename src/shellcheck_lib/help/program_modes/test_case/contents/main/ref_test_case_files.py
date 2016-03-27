from shellcheck_lib.default.program_modes.test_case.test_case_parser import DEFAULT_PHASE
from shellcheck_lib.document.syntax import section_header
from shellcheck_lib.help.program_modes.test_case.contents.main.setup import Setup
from shellcheck_lib.help.utils.formatting import AnyInstructionNameDictionary
from shellcheck_lib.util.textformat.parse import normalize_and_parse
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure.structures import *


def test_case_files_documentation(setup: Setup) -> doc.SectionContents:
    instruction_dict = AnyInstructionNameDictionary()
    phases_doc = PHASES_DOC.format(phase_declaration_for_NAME=section_header('NAME'),
                                   instruction=instruction_dict,
                                   default_phase=setup.phase_names[DEFAULT_PHASE.identifier].syntax)
    phases_paragraphs = (normalize_and_parse(phases_doc) +
                         [literal_layout(EXAMPLE_TEST_CASE_WITH_MULTIPLE_DECLARATIONS_OF_A_PHASE)]
                         )
    instructions_paragraphs = (
        normalize_and_parse(INSTRUCTIONS_DOC.format(instruction=instruction_dict)) +
        [literal_layout(INSTRUCTION_THAT_SPANS_MULTIPLE_LINES_EXAMPLE)]
    )
    other_paragraphs = (normalize_and_parse(OTHER_DOC.format(phase=setup.phase_names,
                                                             instruction=instruction_dict)) +
                        [literal_layout(EXAMPLE_OF_INSTRUCTION_THAT_CONTAINS_COMMENT_AND_EMPTY_LINES)]
                        )
    return doc.SectionContents(
        [],
        [
            doc.Section(text('Phases'),
                        doc.SectionContents(phases_paragraphs,
                                            [])),
            doc.Section(text('Instructions'),
                        doc.SectionContents(instructions_paragraphs,
                                            [])),
            doc.Section(text('Comments and empty lines'),
                        doc.SectionContents(other_paragraphs,
                                            [])),
        ])


PHASES_DOC = """\
"{phase_declaration_for_NAME}" on a single line declares the start of phase NAME.

The content on the following lines will belong to this phase.


File contents before the first phase declaration will belong to the default phase,
which is {default_phase}.


A phase can be declared more than once.

Contents of multiple declarations are merged, and executed in the order it appears in the file.

In following example, {instruction[exitcode]} is executed before {instruction[stderr]}:
"""

EXAMPLE_TEST_CASE_WITH_MULTIPLE_DECLARATIONS_OF_A_PHASE = """\
[assert]

exitcode 0

[act]

helloworld

[assert]

stderr empty
"""

INSTRUCTIONS_DOC = """\
Instructions start at the beginning of the line with a space separated identifier.

The identifier may optionally be followed by arguments.
The syntax depends on the particular instruction.


An instruction may span several lines, if its syntax allows this.
As with {instruction[stdout]} here:
"""

INSTRUCTION_THAT_SPANS_MULTIPLE_LINES_EXAMPLE = """\
stdout <<EOF
Hello, World!
EOF
"""

OTHER_DOC = """\
Lines beginning with # are comments.

Comments are not allowed on other lines.


Empty lines are ignored.


Note though that instructions themselves, and also the {phase[act]} phase,
can decide how lines are interpreted.

As {instruction[stdout]} does in this example:
"""

EXAMPLE_OF_INSTRUCTION_THAT_CONTAINS_COMMENT_AND_EMPTY_LINES = """\
stdout <<EOF
this instruction expects 4 lines of output
# this is the second line of the expected output

the above empty lines is part of the expected output
EOF
"""
