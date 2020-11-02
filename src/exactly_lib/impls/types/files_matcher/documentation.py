from typing import Sequence

from exactly_lib.common.help import headers
from exactly_lib.definitions import matcher_model, misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls import file_properties, texts
from exactly_lib.impls.types.expression import grammar
from exactly_lib.impls.types.files_matcher import config
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class EmptyDoc(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return ()

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TP.fnap(_CHECKS_THAT_PATH_IS_AN_EMPTY_DIRECTORY)


class NumFilesDoc(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.single_mandatory,

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return (
                _TP.fnap(_CHECKS_THAT_DIRECTORY_CONTAINS_SPECIFIED_NUMBER_OF_FILES) +
                texts.type_expression_has_syntax_of_primitive([
                    syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.singular_name,
                ])
        )

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.cross_reference_target,


class SelectionDoc(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return (
            syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.single_mandatory,
            syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.single_mandatory,
        )

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        ret_val = _TP.fnap(_SELECTION_DESCRIPTION)
        ret_val += texts.type_expression_has_syntax_of_primitive([
            syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.singular_name,
            syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.singular_name,
        ])
        return ret_val


class PruneDoc(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return (
            syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.single_mandatory,
            syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.single_mandatory,
        )

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        ret_val = _TP.fnap(_PRUNE_DESCRIPTION)
        ret_val += texts.type_expression_has_syntax_of_primitive([
            syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.singular_name,
            syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.singular_name,
        ])
        return ret_val


class MatchesDoc(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return (
            a.Single(a.Multiplicity.OPTIONAL, config.MATCHES_FULL_OPTION),
            syntax_elements.FILES_CONDITION_SYNTAX_ELEMENT.single_mandatory,
        )

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TP.fnap(_MATCHES_DESCRIPTION)

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return syntax_elements.FILES_CONDITION_SYNTAX_ELEMENT.cross_reference_target,


_TP = TextParser({
    'FILE_MATCHER': syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.singular_name,
    'FILES_MATCHER': syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.singular_name,
    'FILES_CONDITION': syntax_elements.FILES_CONDITION_SYNTAX_ELEMENT.singular_name,
    'INTEGER_MATCHER': syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.singular_name,
    'model': matcher_model.FILES_MATCHER_MODEL,
    'element': matcher_model.FILE_MATCHER_MODEL,
    'NOTE': headers.NOTE_LINE_HEADER,
    'SYMBOLIC_LINKS_ARE_FOLLOWED': misc_texts.SYMBOLIC_LINKS_ARE_FOLLOWED,
    'symbolic_link': file_properties.TYPE_INFO[file_properties.FileType.SYMLINK].name,
    'matches_full_option': option_syntax.option_syntax(config.MATCHES_FULL_OPTION.name),
    'prune_option': option_syntax.option_syntax(config.PRUNE_OPTION.name),
    'selection_option': option_syntax.option_syntax(config.SELECTION_OPTION.name),
})

_MATCHES_DESCRIPTION = """\
Matches iff the set of files contains every file in {FILES_CONDITION}.


If {matches_full_option} is given,
the set of files must contain no other files
than those in {FILES_CONDITION}.
"""

_SELECTION_DESCRIPTION = """\
Applies {FILES_MATCHER} to the sub set of {element:s} matched by {FILE_MATCHER}.


{NOTE} If combined with {prune_option} - pruning is done before {selection_option},
regardless of their mutual order.
"""

_PRUNE_DESCRIPTION = """\
Excludes contents of directories matched by {FILE_MATCHER}.


{SYMBOLIC_LINKS_ARE_FOLLOWED}.


{NOTE} {FILE_MATCHER} is only applied to directories (and {symbolic_link:s} to directories).
"""

_CHECKS_THAT_PATH_IS_AN_EMPTY_DIRECTORY = """\
Matches iff the {model} is empty.
"""

_CHECKS_THAT_DIRECTORY_CONTAINS_SPECIFIED_NUMBER_OF_FILES = """\
Matches iff the number of {element:s} satisfies {INTEGER_MATCHER}.
"""
