from exactly_lib.help.concepts.names_and_cross_references import ACTOR_CONCEPT_INFO
from exactly_lib.help.program_modes.test_case.contents.main.utils import Setup
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.formatting import AnyInstructionNameDictionary
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.section_document.syntax import section_header
from exactly_lib.test_case.phase_identifier import DEFAULT_PHASE
from exactly_lib.util.textformat.structure import structures as docs


def test_case_files_documentation(setup: Setup) -> docs.SectionContents:
    parser = TextParser({
        'phase_declaration_for_NAME': section_header('NAME'),
        'instruction': AnyInstructionNameDictionary(),
        'default_phase': setup.phase_names[DEFAULT_PHASE.identifier].syntax,
        'phase': setup.phase_names,
        'actor': formatting.concept(ACTOR_CONCEPT_INFO.singular_name),
    })
    return docs.SectionContents(
        [],
        [
            parser.section('Phases', PHASES_DOC),
            parser.section('Phase contents', PHASES_CONTENTS_DOC),
            parser.section('Instructions', INSTRUCTIONS_DOC),
            parser.section('Comments and empty lines', OTHER_DOC),
        ])


PHASES_DOC = """\
"{phase_declaration_for_NAME}" on a single line declares the start of phase NAME.

The following lines will belong to this phase.


File contents before the first phase declaration belong to the default phase,
which is {default_phase}.


The order of the different phases in the test case file is irrelevant.
The phases are always executed in the same order,
regardless of the order they appear in the test case file.


A phase can be declared more than once.

Contents of multiple declarations are merged, and executed in the order it appears in the file.

In following example, {instruction[exitcode]} is executed before {instruction[stderr]}:


```
[assert]

exitcode 0

[act]

helloworld

[assert]

stderr empty
```
"""

PHASES_CONTENTS_DOC = """\
All phases except the {phase[act]} phase consist of a sequence of "instructions" (see below).


The contents of the {phase[act]} phase depends on which {actor} is used.

By default, it consists of a single command line.
"""

INSTRUCTIONS_DOC = """\
Instructions start at the beginning of the line with a space separated identifier.


The identifier may optionally be followed by arguments. Most instructions use a syntax for
options, arguments and quoting that resembles the unix shell.

The exact syntax depends on the particular instruction, though.


An instruction may span several lines, as this form of {instruction[stdout]} does:


```
stdout <<EOF
Hello, World!
EOF
```
"""

OTHER_DOC = """\
Lines beginning with "#" are comments.

Comments are not allowed on other lines.


Empty lines are ignored.


Note though that instructions themselves, and also the {phase[act]} phase,
can decide how lines are interpreted.
As {instruction[stdout]} does here:


```
stdout <<EOF
this assertion expects 4 lines of output
# this is the second line of the expected output

the above empty line is part of the expected output
EOF
```
"""
