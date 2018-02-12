from typing import Sequence, List

from exactly_lib.common.help.abs_or_rel_path import abs_or_rel_path_of_existing
from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, invokation_variant_from_args, \
    SyntaxElementDescription, cli_argument_syntax_element_description
from exactly_lib.help_texts.test_case.instructions import instruction_names
from exactly_lib.test_case.phases.assert_ import WithAssertPhasePurpose, AssertPhasePurpose
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class FileInclusionDirectiveDocumentation(InstructionDocumentation,
                                          WithAssertPhasePurpose):
    def __init__(self):
        super().__init__(instruction_names.FILE_INCLUSION_DIRECTIVE_NAME)
        self.file_argument = a.Named('FILE')
        self._tp = TextParser()

    @property
    def assert_phase_purpose(self) -> AssertPhasePurpose:
        return AssertPhasePurpose.HELPER

    def single_line_description(self) -> str:
        return 'Directive that includes a test case source file'

    def invokation_variants(self) -> Sequence[InvokationVariant]:
        return [
            invokation_variant_from_args([a.Single(a.Multiplicity.MANDATORY,
                                                   self.file_argument)])
        ]

    def syntax_element_descriptions(self) -> Sequence[SyntaxElementDescription]:
        return [
            cli_argument_syntax_element_description(self.file_argument,
                                                    abs_or_rel_path_of_existing(
                                                        'file',
                                                        self.file_argument.name,
                                                        _FILE_RELATIVITY_ROOT
                                                    ))
        ]

    def main_description_rest(self) -> List[ParagraphItem]:
        return self._tp.fnap(_MAIN_DESCRIPTION_REST)


_FILE_RELATIVITY_ROOT = 'directory of the source file'

_MAIN_DESCRIPTION_REST = """\
Includes instructions from an external file.


The effect of including a file is equivalent to having the
contents of the included file in the including file,
except that the current phase of the including file
cannot be changed by an included file.


The default phase of the external file is the phase
from which the file is included.


The included file may contain contents of
different phases, by switching phase.

But the phase of the including file is
not changed.
"""
