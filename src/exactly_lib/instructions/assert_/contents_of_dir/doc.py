from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering.path_syntax import the_path_of
from exactly_lib.help_texts.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.help_texts.entity.types import FILE_MATCHER_TYPE_INFO
from exactly_lib.instructions.assert_.utils.file_contents.syntax import file_contents_matcher as parts_cl_syntax, \
    file_contents_checker
from exactly_lib.instructions.assert_.utils.file_contents_resources import EMPTY_ARGUMENT_CONSTANT
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.instructions.utils.documentation.relative_path_options_documentation import path_element
from exactly_lib.processing import exit_values
from exactly_lib.test_case.phases.assert_ import WithAssertPhasePurpose
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils import negation_of_predicate
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.parse import rel_opts_configuration
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure import structures as docs
from . import config

DIR_CONTENTS_MATCHER = a.Named('DIR-CONTENTS-MATCHER')


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase,
                                  WithAssertPhasePurpose):

    def __init__(self, name: str):
        super().__init__(name, {
            'checked_file': _PATH_ARGUMENT.name,
            'selection': instruction_arguments.SELECTION.name,
            'dir_contents_matcher': DIR_CONTENTS_MATCHER.name,
            'file_matcher': FILE_MATCHER_TYPE_INFO.name.singular,
            'any': instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT,
            'every': instruction_arguments.ALL_QUANTIFIER_ARGUMENT,
            'HARD_ERROR': exit_values.EXECUTION__HARD_ERROR.exit_identifier,
        })
        self.file_contents_assertion_help = parts_cl_syntax.FileContentsMatcherHelp()
        self.actual_file = a.Single(a.Multiplicity.MANDATORY,
                                    _PATH_ARGUMENT)
        self.relativity_of_actual_arg = instruction_arguments.RELATIVITY_ARGUMENT
        self.actual_file_relativity = a.Single(a.Multiplicity.OPTIONAL,
                                               self.relativity_of_actual_arg)

    def single_line_description(self) -> str:
        return _SINGLE_LINE_DESCRIPTION

    def main_description_rest(self) -> list:
        return self._paragraphs(_MAIN_DESCRIPTION_REST)

    def invokation_variants(self) -> list:
        negation_argument = negation_of_predicate.optional_negation_argument_usage()
        selection_arg = a.Single(a.Multiplicity.OPTIONAL,
                                 instruction_arguments.SELECTION)
        dir_contents_matcher_arg = a.Single(a.Multiplicity.MANDATORY,
                                            DIR_CONTENTS_MATCHER)

        arguments = [self.actual_file,
                     selection_arg,
                     negation_argument,
                     dir_contents_matcher_arg,
                     ]

        return [
            InvokationVariant(self._cl_syntax_for_args(arguments),
                              self._paragraphs(_MAIN_INVOKATION_SYNTAX_DESCRIPTION)),

        ]

    def syntax_element_descriptions(self) -> list:
        negation = negation_of_predicate.syntax_element_description(_ADDITIONAL_TEXT_OF_NEGATION_SED)

        selection = parse_file_matcher.selection_syntax_element_description()

        actual_file_arg_sed = path_element(_PATH_ARGUMENT.name,
                                           ACTUAL_RELATIVITY_CONFIGURATION.options,
                                           docs.paras(the_path_of("the directory who's contents is checked.")))

        return [
            self._files_assertion_sed(),
            selection,
            actual_file_arg_sed,
            file_contents_checker.transformation_syntax_element_description('each file'),
            negation,
        ]

    def _files_assertion_sed(self) -> SyntaxElementDescription:
        mandatory_empty_arg = a.Single(a.Multiplicity.MANDATORY,
                                       EMPTY_ARGUMENT_CONSTANT)

        mandatory_num_files_arg = a.Single(a.Multiplicity.MANDATORY,
                                           config.NUM_FILES_ARGUMENT_CONSTANT)

        arguments_for_empty_check = [mandatory_empty_arg]

        arguments_for_num_files_check = [mandatory_num_files_arg,
                                         syntax_elements.INTEGER_COMPARISON_SYNTAX_ELEMENT.single_mandatory]

        quantifier_arg = a.Choice(a.Multiplicity.MANDATORY,
                                  [
                                      a.Constant(
                                          instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT),
                                      a.Constant(
                                          instruction_arguments.ALL_QUANTIFIER_ARGUMENT),
                                  ])
        file_arg = a.Single(a.Multiplicity.MANDATORY,
                            a.Constant(config.QUANTIFICATION_OVER_FILE_ARGUMENT))

        separator_arg = a.Single(a.Multiplicity.MANDATORY,
                                 a.Constant(
                                     instruction_arguments.QUANTIFICATION_SEPARATOR_ARGUMENT))

        file_contents_args = ([quantifier_arg,
                               file_arg,
                               separator_arg] + file_contents_checker.file_contents_checker_arguments()
                              )

        invokation_variants = [
            InvokationVariant(self._cl_syntax_for_args(arguments_for_empty_check),
                              self._paragraphs(_CHECKS_THAT_PATH_IS_AN_EMPTY_DIRECTORY)),

            InvokationVariant(self._cl_syntax_for_args(arguments_for_num_files_check),
                              self._paragraphs(_CHECKS_THAT_DIRECTORY_CONTAINS_SPECIFIED_NUMBER_OF_FILES)),
            InvokationVariant(self._cl_syntax_for_args(file_contents_args),
                              self._paragraphs(_DESCRIPTION_OF_FILE_QUANTIFICATION))
        ]
        return SyntaxElementDescription(
            DIR_CONTENTS_MATCHER.name,
            [],
            invokation_variants
        )

    def see_also_targets(self) -> list:
        from exactly_lib.help_texts.entity import types
        name_and_cross_refs = [types.FILE_MATCHER_TYPE_INFO,
                               types.LINES_TRANSFORMER_TYPE_INFO,
                               syntax_elements.FILE_CONTENTS_MATCHER,
                               syntax_elements.PATH_SYNTAX_ELEMENT,
                               syntax_elements.INTEGER_COMPARISON_SYNTAX_ELEMENT]
        name_and_cross_refs += rel_path_doc.see_also_name_and_cross_refs(ACTUAL_RELATIVITY_CONFIGURATION.options)
        return cross_reference_id_list(name_and_cross_refs)

    def _cls(self, additional_argument_usages: list) -> str:
        return self._cl_syntax_for_args([self.actual_file] + additional_argument_usages)


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
FAIL if {checked_file} is not an existing directory
(even when the assertion is negated).


Symbolic links are followed.
"""

_MAIN_INVOKATION_SYNTAX_DESCRIPTION = """\
Applies {dir_contents_matcher} to the files in the directory {checked_file},
or to a sub set of files, if {selection} is given.
"""

_CHECKS_THAT_PATH_IS_AN_EMPTY_DIRECTORY = """\
Tests that {checked_file} is an empty directory, or that the set of selected files is empty.
"""

_CHECKS_THAT_DIRECTORY_CONTAINS_SPECIFIED_NUMBER_OF_FILES = """\
Tests the number of files in {checked_file}.
"""

_DESCRIPTION_OF_FILE_QUANTIFICATION = """\
Tests that {any}/{every} file satisfies the given assertion
on the contents of an individual file.


The result is {HARD_ERROR} if a tested file is not a regular file.
"""

_PATH_SYNTAX_ELEMENT_DESCRIPTION_TEXT = "The directory who's contents is checked."

_ADDITIONAL_TEXT_OF_NEGATION_SED = ' (Except for the test of the existence of the checked directory.)'
