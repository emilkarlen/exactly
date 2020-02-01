from typing import Sequence

from exactly_lib.definitions import matcher_model, misc_texts
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.test_case_utils import file_properties
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
            syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.single_mandatory,
            syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.single_mandatory,
        )

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TP.fnap(_SELECTION_DESCRIPTION)


class PruneDoc(grammar.SimpleExpressionDescription):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return (
            syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.single_mandatory,
            syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.single_mandatory,
        )

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TP.fnap(_PRUNE_DESCRIPTION)


_TP = TextParser({
    'FILE_MATCHER': syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.singular_name,
    'FILES_MATCHER': syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.singular_name,
    'model': matcher_model.FILES_MATCHER_MODEL,
    'element': matcher_model.FILE_MATCHER_MODEL,
    'NOTE': misc_texts.NOTE_LINE_HEADER,
    'SYMBOLIC_LINKS_ARE_FOLLOWED': misc_texts.SYMBOLIC_LINKS_ARE_FOLLOWED,
    'symbolic_link': file_properties.TYPE_INFO[file_properties.FileType.SYMLINK].name,
})

_SELECTION_DESCRIPTION = """\
Applies {FILES_MATCHER} to the sub set of {element:s} matched by {FILE_MATCHER}.
"""

_PRUNE_DESCRIPTION = """\
Excludes contents of directories matched by {FILE_MATCHER}.


{SYMBOLIC_LINKS_ARE_FOLLOWED}.


{NOTE} {FILE_MATCHER} is only applied to directories (and {symbolic_link:s} to directories).
"""

_CHECKS_THAT_PATH_IS_AN_EMPTY_DIRECTORY = """\
Tests that the {model} is empty.
"""

_CHECKS_THAT_DIRECTORY_CONTAINS_SPECIFIED_NUMBER_OF_FILES = """\
Tests the number of {element:s}.
"""
