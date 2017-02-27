from exactly_lib.common.help import cross_reference_id as cross_ref
from exactly_lib.help.concepts.names_and_cross_references import ACTOR_CONCEPT_INFO
from exactly_lib.help.program_modes.test_case.contents.main.utils import TestCaseHelpRendererBase, Setup
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.formatting import AnyInstructionNameDictionary
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.instructions.assert_.utils.file_contents import instruction_options as contents_opts
from exactly_lib.section_document.syntax import section_header
from exactly_lib.test_case.phase_identifier import DEFAULT_PHASE
from exactly_lib.util.textformat.structure import structures as docs


class TestCaseFileDocumentationRenderer(TestCaseHelpRendererBase):
    def __init__(self, setup: Setup,
                 target_factory: cross_ref.CustomTargetInfoFactory):
        super().__init__(setup.test_case_help)
        self.setup = setup

        self._PHASES_TI = target_factory.sub('Phases', 'phases')
        self._PHASE_CONTENTS_TI = target_factory.sub('Phase contents', 'phase-contents')
        self._INSTRUCTIONS_TI = target_factory.sub('Instructions', 'instructions')
        self._COM_EMPTY_TI = target_factory.sub('Comments and empty lines', 'com-empty')

    def target_info_hierarchy(self) -> list:
        return [
            cross_ref.target_info_leaf(self._PHASES_TI),
            cross_ref.target_info_leaf(self._PHASE_CONTENTS_TI),
            cross_ref.target_info_leaf(self._INSTRUCTIONS_TI),
            cross_ref.target_info_leaf(self._COM_EMPTY_TI),
        ]

    def apply(self, environment: RenderingEnvironment) -> docs.SectionContents:
        parser = TextParser({
            'phase_declaration_for_NAME': section_header('NAME'),
            'instruction': AnyInstructionNameDictionary(),
            'default_phase': self.setup.phase_names[DEFAULT_PHASE.identifier].syntax,
            'phase': self.setup.phase_names,
            'actor': formatting.concept(ACTOR_CONCEPT_INFO.singular_name),
            'CONTENTS_EQUALS_ARGUMENT': contents_opts.EQUALS_ARGUMENT,
            'CONTENTS_EMPTY_ARGUMENT': contents_opts.EMPTY_ARGUMENT,
        })
        return docs.SectionContents(
            [],
            [
                docs.section(self._PHASES_TI.anchor_text(), parser.fnap(PHASES_DOC)),
                docs.section(self._PHASE_CONTENTS_TI.anchor_text(), parser.fnap(PHASES_CONTENTS_DOC)),
                docs.section(self._INSTRUCTIONS_TI.anchor_text(),
                             parser.fnap(INSTRUCTIONS_DOC),
                             [parser.section('Instruction descriptions',
                                             INSTRUCTIONS_DESCRIPTION_DOC)]),
                docs.section(self._COM_EMPTY_TI.anchor_text(), parser.fnap(OTHER_DOC)),
            ])


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

exitcode 0

[act]

helloworld

[assert]

stderr {CONTENTS_EMPTY_ARGUMENT}
```
"""

PHASES_CONTENTS_DOC = """\
All phases except the {phase[act]} phase consist of a sequence of "instructions" (see below).


The contents of the {phase[act]} phase depends on which {actor} is used.

By default, it consists of a single command line.
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
The instruction name may optionally be preceded by a "description" -
a free text within quotes that is
displayed together with the instruction source line in error messages.

The purpose of a description is to describe the meaning of the instruction using
text that is easier to understand than the source line.

A description is a quoted string using shell syntax.


For example, a free text may be easier to understand than a shell command:


```
'my-dir should be empty'
$ test $(ls my-dir | wc -l) -eq 0
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
