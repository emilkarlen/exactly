from typing import List

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, invokation_variant_from_args, \
    SyntaxElementDescription, cli_argument_syntax_element_description
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.argument_rendering import cl_syntax
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements, types, concepts
from exactly_lib.definitions.primitives import files_matcher as files_matcher_primitives
from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.processing import exit_values
from exactly_lib.test_case_utils import negation_of_predicate
from exactly_lib.test_case_utils.file_or_dir_contents_resources import EMPTY_ARGUMENT_CONSTANT
from exactly_lib.test_case_utils.files_matcher import config
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser

MATCHER_ARG_NAME = a.Named(syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.singular_name)

MATCHER_VARIANT_ARG_NAME = a.Named('MATCHER')


class _FilesMatcherDocumentation(SyntaxElementDocumentation):
    def __init__(self):
        super().__init__(TypeCategory.LOGIC,
                         syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT)
        self._tp = TextParser({
            'symbol_concept': concepts.SYMBOL_CONCEPT_INFO.name,
            'selection': instruction_arguments.SELECTION.name,
            'file_matcher': types.FILE_MATCHER_TYPE_INFO.name.singular,
            'any': instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT,
            'every': instruction_arguments.ALL_QUANTIFIER_ARGUMENT,
            'HARD_ERROR': exit_values.EXECUTION__HARD_ERROR.exit_identifier,
            'FILE_MATCHER': instruction_arguments.SELECTION_OPTION.argument,
            'FILE_MATCHER_SYNTAX_ELEMENT': syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.singular_name,
            'this_type': types.FILES_MATCHER_TYPE_INFO.name,
        })

    def main_description_rest_paragraphs(self) -> List[ParagraphItem]:
        return self._tp.fnap(_MAIN_DESCRIPTION_REST)

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            self._main_invokation_variant(),
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        negation = negation_of_predicate.matcher_syntax_element_description()

        selection = self._selection_syntax_element_description()

        return [
            self._matcher_sed(),
            selection,
            negation,
        ]

    def _selection_syntax_element_description(self) -> SyntaxElementDescription:
        return cli_argument_syntax_element_description(
            instruction_arguments.SELECTION,
            self._tp.fnap(_SELECTION_DESCRIPTION),
            [
                InvokationVariant(cl_syntax.arg_syntax(instruction_arguments.SELECTION_OPTION)),
            ]
        )

    def _matcher_sed(self) -> SyntaxElementDescription:
        mandatory_empty_arg = a.Single(a.Multiplicity.MANDATORY,
                                       EMPTY_ARGUMENT_CONSTANT)

        mandatory_num_files_arg = a.Single(a.Multiplicity.MANDATORY,
                                           config.NUM_FILES_ARGUMENT_CONSTANT)

        arguments_for_empty_check = [mandatory_empty_arg]

        arguments_for_num_files_check = [mandatory_num_files_arg,
                                         syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.single_mandatory]

        quantifier_arg = a.Choice(a.Multiplicity.MANDATORY,
                                  [
                                      a.Constant(
                                          instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT),
                                      a.Constant(
                                          instruction_arguments.ALL_QUANTIFIER_ARGUMENT),
                                  ])
        file_arg = a.Single(a.Multiplicity.MANDATORY,
                            a.Constant(
                                files_matcher_primitives.QUANTIFICATION_OVER_FILE_ARGUMENT))

        separator_arg = a.Single(a.Multiplicity.MANDATORY,
                                 a.Constant(
                                     instruction_arguments.QUANTIFICATION_SEPARATOR_ARGUMENT))

        file_contents_args = ([quantifier_arg,
                               file_arg,
                               separator_arg,
                               syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.single_mandatory
                               ]
        )
        symbol_argument = a.Single(a.Multiplicity.MANDATORY,
                                   syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.argument)

        invokation_variants = [
            invokation_variant_from_args(arguments_for_empty_check,
                                         self._tp.fnap(_CHECKS_THAT_PATH_IS_AN_EMPTY_DIRECTORY)),

            invokation_variant_from_args(arguments_for_num_files_check,
                                         self._tp.fnap(_CHECKS_THAT_DIRECTORY_CONTAINS_SPECIFIED_NUMBER_OF_FILES)),
            invokation_variant_from_args(file_contents_args,
                                         self._tp.fnap(_DESCRIPTION_OF_FILE_QUANTIFICATION)),

            invokation_variant_from_args([symbol_argument],
                                         self._tp.fnap(_SYMBOL_REF_DESCRIPTION)),

        ]
        return SyntaxElementDescription(
            MATCHER_VARIANT_ARG_NAME.name,
            [],
            invokation_variants
        )

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        name_and_cross_refs = [
            syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT,
            syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT,
            syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT,
        ]
        return cross_reference_id_list(name_and_cross_refs)

    def _main_invokation_variant(self) -> InvokationVariant:
        negation_argument = negation_of_predicate.optional_negation_argument_usage()
        selection_arg = a.Single(a.Multiplicity.OPTIONAL,
                                 instruction_arguments.SELECTION)
        dir_contents_matcher_arg = a.Single(a.Multiplicity.MANDATORY,
                                            MATCHER_VARIANT_ARG_NAME)

        arguments = [selection_arg,
                     negation_argument,
                     dir_contents_matcher_arg,
                     ]

        return invokation_variant_from_args(arguments)


DOCUMENTATION = _FilesMatcherDocumentation()

_MAIN_DESCRIPTION_REST = """\
Symbolic links are followed.
"""

_SELECTION_DESCRIPTION = """\
Makes the matcher apply to the sub set of files matched by {FILE_MATCHER}.
"""

_CHECKS_THAT_PATH_IS_AN_EMPTY_DIRECTORY = """\
Tests that the set of files is empty.
"""

_CHECKS_THAT_DIRECTORY_CONTAINS_SPECIFIED_NUMBER_OF_FILES = """\
Tests the number of files.
"""

_DESCRIPTION_OF_FILE_QUANTIFICATION = """\
Tests that {any}/{every} file satisfies the given {FILE_MATCHER_SYNTAX_ELEMENT}.
"""

_SYMBOL_REF_DESCRIPTION = """\
Reference to {symbol_concept:a},
that must have been defined as {this_type:a}.
"""
