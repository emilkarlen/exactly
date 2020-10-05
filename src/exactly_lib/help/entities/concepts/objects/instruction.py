from typing import List

from exactly_lib import program_info
from exactly_lib.common.help.headers import FORMS_PARA
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, invokation_variant_from_string
from exactly_lib.definitions import formatting, misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.formatting import InstructionName
from exactly_lib.definitions.test_case import phase_infos
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help.program_modes.common.render_syntax_contents import invokation_variants_paragraphs
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser


class _InstructionConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(concepts.INSTRUCTION_CONCEPT_INFO)
        self._tp = TextParser({
            'instruction': self.name(),
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'symbol': concepts.SYMBOL_CONCEPT_INFO.name,
            'def': InstructionName(instruction_names.SYMBOL_DEFINITION_INSTRUCTION_NAME),
            'act': phase_infos.ACT.name,
            'atc': concepts.ACTION_TO_CHECK_CONCEPT_INFO.name,
            'assert': phase_infos.ASSERT.name,
            'cleanup': phase_infos.CLEANUP.name,
            'shell_command_line': formatting.misc_name_with_formatting(misc_texts.SHELL_COMMAND_LINE),
        })

    def purpose(self) -> DescriptionWithSubSections:
        return DescriptionWithSubSections(
            self.single_line_description(),
            docs.section_contents(
                self._tp.fnap(_DESCRIPTION_REST),
                [
                    docs.section(
                        'Semantics',
                        self._tp.fnap(_SEMANTICS)
                    ),
                    docs.section(
                        'Syntax',
                        [FORMS_PARA] +
                        self._invokation_variants_paragraphs() +
                        self._tp.fnap(_SYNTAX),
                    ),
                ]
            ))

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return [
            concepts.TYPE_CONCEPT_INFO.cross_reference_target,
            concepts.SYMBOL_CONCEPT_INFO.cross_reference_target,
        ]

    def _invokation_variants_paragraphs(self) -> List[docs.ParagraphItem]:
        return invokation_variants_paragraphs(
            None,
            [self._invokation_variant_set_property(),
             self._invokation_variant_name_argument(), ],
            [])

    def _invokation_variant_set_property(self) -> InvokationVariant:
        return invokation_variant_from_string(
            'PROPERTY = VALUE',
            self._tp.fnap(_SET_PROPERTY_DESCRIPTION),
        )

    def _invokation_variant_name_argument(self) -> InvokationVariant:
        return invokation_variant_from_string(
            'INSTRUCTION-NAME ARGUMENT...',
            self._tp.fnap(_NAME_AND_ARGUMENT_DESCRIPTION),
        )


INSTRUCTION_CONCEPT = _InstructionConcept()

############################################################
# MENTION
#
# - Executable
# - Building block of all phases except [act]
# - Can succeed or cause in error - test case execution halts
#   when an instruction causes an error
# - Meaning of executing a phase (see description of test case:
#   ("executing a test case means executing all of its phases"
#    add - executing a phase means executing all of its instructions,
#    and halt at the first that causes an error)
#
# - Semantics:
#    - all phases except [assert]: is a side-effect
#    - [act]: some instructions are assertions
#      (more info in description of [act])
#
# - Syntax
#   - starts on new line
#   - have a name/identifier
#   - can span multiple lines
#   - syntax is defined by each instruction
#   - arguments are often type values
############################################################
_DESCRIPTION_REST = """\
All phases except {act:syntax} is a sequence of {instruction:s/q},
zero or more.


Executing a phase means executing all {instruction:s} in the phase,
in the order they appear in the test case source file.


Each phase has its own {instruction} set.
"""

_SEMANTICS = """\
In {assert:syntax}, {instruction:s} serve as assertions by representing boolean expressions.

E.g. asserting that the {atc} did not output anything to stdout:


```
stdout empty
```


In all other phases, and also for some of the {instruction:s} in {assert:syntax},
the purpose of {instruction:a} is its side effects for
setting up the execution environment of {act:syntax}, {assert:syntax},
or cleaning up after the test ({cleanup:syntax}).

E.g. creating a file:


```
file my-file.txt = "contents of my file"
```
"""

_SYNTAX = """\
{instruction:a/u} starts on a new line, beginning with the name of the {instruction},
followed by arguments.


Each {instruction} has its own syntax for arguments.

Most common syntax is that of options and arguments resembling the
Unix {shell_command_line} interface.

One difference though, is that the order of options is usually significant.


Some {instruction:s} may span multiple lines,
while some must use only a single line.

The syntax is not always consistent.


Most arguments are values of one of {program_name}'s type system,
and thus use a common syntax.


Arguments may refer to {symbol:s} defined by the {def} {instruction}.


Comments may not appear inside {instruction:s}.
"""

# EXAMPLE CASES exist in examples/builtin-help
_SET_PROPERTY_DESCRIPTION = """\
For example:


```
timeout = 10

stdin   = "contents of stdin"
```
"""

# EXAMPLE CASES exist in examples/builtin-help
_NAME_AND_ARGUMENT_DESCRIPTION = """\
For example:


```
file my-file.txt = "contents of my file"

run % python -c :> import sys; sys.stdout.write("Hello world")
```

"""
