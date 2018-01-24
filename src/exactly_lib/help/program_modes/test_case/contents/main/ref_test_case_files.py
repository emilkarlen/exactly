from exactly_lib.help.program_modes.test_case.contents.main.utils import Setup
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.entity.concepts import ACTOR_CONCEPT_INFO
from exactly_lib.help_texts.formatting import AnyInstructionNameDictionary
from exactly_lib.instructions.assert_.utils.file_contents import instruction_options as contents_opts
from exactly_lib.section_document.syntax import section_header
from exactly_lib.test_case.phase_identifier import DEFAULT_PHASE
from exactly_lib.util.textformat.construction.section_contents_constructor import ConstructionEnvironment, \
    SectionContentsConstructor
from exactly_lib.util.textformat.construction.section_hierarchy import structures, hierarchy
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser


def generator(header: str, setup: Setup) -> structures.SectionHierarchyGenerator:
    text_parser = _text_parser(setup)
    return hierarchy.parent(
        header, [],
        [
            ('phases', hierarchy.leaf('Phases', _PhaseRenderer(text_parser))),
            ('phase-contents', hierarchy.leaf('Phase contents', _PhaseContentsRenderer(text_parser))),
            ('instructions', hierarchy.parent(
                'Instructions',
                text_parser.fnap(INSTRUCTIONS_DOC),
                [('description',
                  hierarchy.leaf('Instruction descriptions',
                                 _InstructionsRenderer(
                                                 text_parser)))])
             ),
            ('com-empty', hierarchy.leaf('Comments and empty lines', _OtherContentsRenderer(text_parser))),
        ]
    )


def _text_parser(setup: Setup) -> TextParser:
    return TextParser({
        'phase_declaration_for_NAME': section_header('NAME'),
        'instruction': AnyInstructionNameDictionary(),
        'default_phase': setup.phase_names[DEFAULT_PHASE.identifier].syntax,
        'phase': setup.phase_names,
        'actor': formatting.concept_(ACTOR_CONCEPT_INFO),
        'CONTENTS_EQUALS_ARGUMENT': contents_opts.EQUALS_ARGUMENT,
        'CONTENTS_EMPTY_ARGUMENT': contents_opts.EMPTY_ARGUMENT,
    })


class _ConstructorBase(SectionContentsConstructor):
    def __init__(self, parser: TextParser):
        self.parser = parser


class _PhaseRenderer(_ConstructorBase):
    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        return docs.section_contents(self.parser.fnap(PHASES_DOC))


class _PhaseContentsRenderer(_ConstructorBase):
    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        return docs.section_contents(self.parser.fnap(PHASES_CONTENTS_DOC))


class _InstructionsRenderer(_ConstructorBase):
    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        return docs.section_contents(self.parser.fnap(INSTRUCTIONS_DESCRIPTION_DOC))


class _OtherContentsRenderer(_ConstructorBase):
    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        return docs.section_contents(self.parser.fnap(OTHER_DOC))


PHASES_DOC = """\
"{phase_declaration_for_NAME}" on a single line declares the start of phase NAME.

This line marks the start the {phase[assert]} phase, for example:


```
[assert]
```


The following lines will belong to this phase.


File contents before the first phase declaration belong to the default phase,
which is {default_phase}.


The order of the different phases in the test case file is irrelevant.
The phases are always executed in the same order,
regardless of the order they appear in the test case file.


A phase can be declared more than once.

Contents of multiple declarations are merged, and executed in the order it appears in the file.

Here, {instruction[exitcode]} is executed before {instruction[stderr]}:


```
[assert]

exitcode == 0

[act]

helloworld

[assert]

stderr {CONTENTS_EMPTY_ARGUMENT}
```
"""

PHASES_CONTENTS_DOC = """\
All phases except the {phase[act]} phase consist of a sequence of "instructions" (see below).


The contents of the {phase[act]} phase depends on which {actor} is used.

By default, it is expected to contain a single command line.
"""

INSTRUCTIONS_DOC = """\
Instructions start at the beginning of the line with a space separated identifier that
is the name of the instruction.


The name may optionally be followed by arguments. Most instructions use a syntax for
options, arguments and quoting that resembles the unix shell.

The exact syntax depends on the particular instruction, though.


An instruction may span several lines, as this form of {instruction[stdout]} does:


```
stdout {CONTENTS_EQUALS_ARGUMENT} <<EOF
Hello, World!
EOF
```
"""

INSTRUCTIONS_DESCRIPTION_DOC = """\
An instruction may optionally be preceded by a "description" -
a free text within quotes that is
displayed together with the instruction source line in error messages.

The purpose of a description is to describe the meaning of the instruction using
text that is easier to understand than the source line.

A description is a quoted string using shell syntax.


For example, a free text may be easier to understand than a shell command:


```
{phase[assert]:syntax}

'PATH should contain /usr/local/bin'

$ tr ':' '\\n' < ../result/stdout | grep '^/usr/local/bin$'
```


A description may span several lines.
"""

OTHER_DOC = """\
Lines beginning with "#" are comments.

Comments are not allowed on other lines.


Empty lines are ignored.


Note though that instructions themselves, and also the {phase[act]} phase,
can decide how lines are interpreted.
As {instruction[stdout]} does here:


```
stdout {CONTENTS_EQUALS_ARGUMENT} <<EOF
this assertion expects 4 lines of output
# this is the second line of the expected output

the above empty line is part of the expected output
EOF
```
"""
