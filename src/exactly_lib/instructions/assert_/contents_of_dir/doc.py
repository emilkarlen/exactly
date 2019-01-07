from typing import List

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription, \
    invokation_variant_from_args
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.argument_rendering.path_syntax import the_path_of
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.instructions.utils.documentation.relative_path_options_documentation import path_element
from exactly_lib.processing import exit_values
from exactly_lib.test_case.phases.assert_ import WithAssertPhasePurpose
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.parse import rel_opts_configuration
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem


class TheInstructionDocumentation(InstructionDocumentationWithTextParserBase,
                                  WithAssertPhasePurpose):

    def __init__(self, name: str):
        super().__init__(name, {
            'checked_file': _PATH_ARGUMENT.name,
            'FILES_MATCHER': syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.singular_name,
            'HARD_ERROR': exit_values.EXECUTION__HARD_ERROR.exit_identifier,
        })
        self.actual_file = a.Single(a.Multiplicity.MANDATORY,
                                    _PATH_ARGUMENT)
        self.relativity_of_actual_arg = instruction_arguments.RELATIVITY_ARGUMENT
        self.actual_file_relativity = a.Single(a.Multiplicity.OPTIONAL,
                                               self.relativity_of_actual_arg)

    def single_line_description(self) -> str:
        return _SINGLE_LINE_DESCRIPTION

    def main_description_rest(self) -> List[ParagraphItem]:
        return self._tp.fnap(_MAIN_DESCRIPTION_REST)

    def invokation_variants(self) -> List[InvokationVariant]:
        files_matcher_arg = a.Single(a.Multiplicity.MANDATORY,
                                     syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.argument)

        arguments = [self.actual_file,
                     files_matcher_arg,
                     ]

        return [
            invokation_variant_from_args(arguments,
                                         self._tp.fnap(_MAIN_INVOKATION_SYNTAX_DESCRIPTION)),

        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        actual_file_arg_sed = path_element(_PATH_ARGUMENT.name,
                                           ACTUAL_RELATIVITY_CONFIGURATION.options,
                                           docs.paras(the_path_of("the directory who's contents is checked.")))

        return [
            actual_file_arg_sed,
        ]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        name_and_cross_refs = [
            syntax_elements.PATH_SYNTAX_ELEMENT,
            syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT,
        ]
        name_and_cross_refs += rel_path_doc.see_also_name_and_cross_refs(ACTUAL_RELATIVITY_CONFIGURATION.options)
        return cross_reference_id_list(name_and_cross_refs)


_PATH_ARGUMENT = instruction_arguments.PATH_ARGUMENT

ACTUAL_RELATIVITY_CONFIGURATION = rel_opts_configuration.RelOptionArgumentConfiguration(
    rel_opts_configuration.RelOptionsConfiguration(
        rel_opts_configuration.PathRelativityVariants({
            RelOptionType.REL_CWD,
            RelOptionType.REL_HOME_ACT,
            RelOptionType.REL_TMP,
            RelOptionType.REL_ACT,
        },
            True),
        RelOptionType.REL_CWD),
    _PATH_ARGUMENT.name,
    True)

_SINGLE_LINE_DESCRIPTION = 'Tests the contents of a directory'

_MAIN_DESCRIPTION_REST = """\
FAIL if {checked_file} is not an existing directory.


Symbolic links are followed.
"""

_MAIN_INVOKATION_SYNTAX_DESCRIPTION = """\
Asserts that the files in the directory {checked_file} satisfies {FILES_MATCHER}.
"""

_PATH_SYNTAX_ELEMENT_DESCRIPTION_TEXT = "The directory who's contents is checked."

_ADDITIONAL_TEXT_OF_NEGATION_SED = ' (Except for the test of the existence of the checked directory.)'
