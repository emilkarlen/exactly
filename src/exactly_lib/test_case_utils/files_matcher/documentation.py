from typing import Sequence

from exactly_lib.definitions import instruction_arguments, matcher_model
from exactly_lib.definitions.entity import syntax_elements, concepts, types
from exactly_lib.processing import exit_values
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class EmptyDoc(grammar.SimpleExpressionDescription):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return ()

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TP.fnap(_CHECKS_THAT_PATH_IS_AN_EMPTY_DIRECTORY)


class NumFilesDoc(grammar.SimpleExpressionDescription):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.single_mandatory,

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TP.fnap(_CHECKS_THAT_DIRECTORY_CONTAINS_SPECIFIED_NUMBER_OF_FILES)


class SelectionDoc(grammar.SimpleExpressionDescription):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return (
            a.Single(a.Multiplicity.MANDATORY,
                     a.Named(instruction_arguments.SELECTION_OPTION.argument),
                     ),
            syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.single_mandatory,
        )

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TP.fnap(_SELECTION_DESCRIPTION)


_TP = TextParser({
    'symbol_concept': concepts.SYMBOL_CONCEPT_INFO.name,
    'selection': instruction_arguments.SELECTION.name,
    'file_matcher': types.FILE_MATCHER_TYPE_INFO.name.singular,
    'any': instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT,
    'every': instruction_arguments.ALL_QUANTIFIER_ARGUMENT,
    'HARD_ERROR': exit_values.EXECUTION__HARD_ERROR.exit_identifier,
    'FILE_MATCHER': instruction_arguments.SELECTION_OPTION.argument,
    'FILE_MATCHER_SYNTAX_ELEMENT': syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.singular_name,
    'this_type': types.FILES_MATCHER_TYPE_INFO.name,
    'model': matcher_model.FILES_MATCHER_MODEL,
    'element': matcher_model.FILE_MATCHER_MODEL,
})

_MAIN_DESCRIPTION_REST = """\
Symbolic links are followed.
"""

_SELECTION_DESCRIPTION = """\
Makes the matcher apply to the sub set of {element:s} matched by {FILE_MATCHER}.
"""

_CHECKS_THAT_PATH_IS_AN_EMPTY_DIRECTORY = """\
Tests that the {model} is empty.
"""

_CHECKS_THAT_DIRECTORY_CONTAINS_SPECIFIED_NUMBER_OF_FILES = """\
Tests the number of {element:s}.
"""

_SYMBOL_REF_DESCRIPTION = """\
Reference to {symbol_concept:a},
that must have been defined as {this_type:a}.
"""
