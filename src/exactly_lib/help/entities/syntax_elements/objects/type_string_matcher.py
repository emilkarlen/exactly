from typing import List

from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, \
    invokation_variant_from_args, InvokationVariant, cli_argument_syntax_element_description
from exactly_lib.definitions import instruction_arguments, formatting
from exactly_lib.definitions.argument_rendering.path_syntax import the_path_of
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements, concepts, types
from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_opts
from exactly_lib.instructions.utils.documentation.string_or_here_doc_or_file import StringOrHereDocOrFile
from exactly_lib.test_case_utils import negation_of_predicate
from exactly_lib.test_case_utils.parse.parse_here_doc_or_path import FILE_ARGUMENT_OPTION
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.test_case_utils.string_matcher.matcher_options import EMPTY_ARGUMENT
from exactly_lib.test_case_utils.string_matcher.parse.parts.equality import \
    EXPECTED_FILE_REL_OPT_ARG_CONFIG
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser

_EXPECTED_PATH_NAME = 'PATH-OF-EXPECTED'

_RELATIVITY_OF_EXPECTED_PATH_NAME = 'RELATIVITY-OF-EXPECTED-PATH'


class _StringMatcherDocumentation(SyntaxElementDocumentation):
    def __init__(self):
        super().__init__(TypeCategory.LOGIC,
                         syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT)

        self.matcher_element_name = instruction_arguments.STRING_MATCHER_PRIMITIVE_SYNTAX_ELEMENT
        self.expected_file_arg = a.Option(FILE_ARGUMENT_OPTION,
                                          _EXPECTED_PATH_NAME)
        self.string_or_here_doc_or_file_arg = StringOrHereDocOrFile(
            _EXPECTED_PATH_NAME,
            _RELATIVITY_OF_EXPECTED_PATH_NAME,
            EXPECTED_FILE_REL_OPT_ARG_CONFIG,
            the_path_of('the file that contains the expected contents.'))
        self._parser = TextParser({
            'symbol_concept': concepts.SYMBOL_CONCEPT_INFO.name,
            'expected_file_arg': _EXPECTED_PATH_NAME,
            'any': instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT,
            'every': instruction_arguments.ALL_QUANTIFIER_ARGUMENT,
            'LINE_MATCHER': instruction_arguments.LINE_MATCHER.name,
            'HERE_DOCUMENT': formatting.syntax_element_(syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT),
            'INTEGER_MATCHER': syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.singular_name,
            'REGEX': syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name,
            'full_regex_match': option_syntax.option_syntax(matcher_options.FULL_MATCH_ARGUMENT_OPTION),
            'this_type': types.STRING_MATCHER_TYPE_INFO.name,
            'SYMBOL_REFERENCE_SYNTAX_ELEMENT': syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT.singular_name,
        })

    def main_description_rest_paragraphs(self) -> List[ParagraphItem]:
        return self._parser.fnap(_MAIN_DESCRIPTION_REST)

    def invokation_variants(self) -> List[InvokationVariant]:
        matcher_arg = a.Single(a.Multiplicity.MANDATORY,
                               a.Named(self.matcher_element_name))

        optional_transformation_option = a.Single(a.Multiplicity.OPTIONAL,
                                                  instruction_arguments.STRING_TRANSFORMATION_ARGUMENT)
        return [
            invokation_variant_from_args([
                optional_transformation_option,
                negation_of_predicate.optional_negation_argument_usage(),
                matcher_arg,
            ])
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return (
                [
                    self._matcher_sed(),
                    negation_of_predicate.matcher_syntax_element_description(),
                    self._transformation_sed(),
                ] +
                self.string_or_here_doc_or_file_arg.syntax_element_descriptions()
        )

    def _matcher_sed(self) -> SyntaxElementDescription:
        mandatory_empty_arg = a.Single(a.Multiplicity.MANDATORY,
                                       a.Constant(EMPTY_ARGUMENT))
        quantifier_arg = a.Choice(a.Multiplicity.MANDATORY,
                                  [
                                      a.Constant(
                                          instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT),
                                      a.Constant(
                                          instruction_arguments.ALL_QUANTIFIER_ARGUMENT),
                                  ])
        equals_arg = a.Single(a.Multiplicity.MANDATORY,
                              a.Constant(
                                  matcher_options.EQUALS_ARGUMENT))

        line_arg = a.Single(a.Multiplicity.MANDATORY,
                            a.Constant(matcher_options.LINE_ARGUMENT))

        quantifier_separator_arg = a.Single(a.Multiplicity.MANDATORY,
                                            a.Constant(instruction_arguments.QUANTIFICATION_SEPARATOR_ARGUMENT))

        line_matcher_arg = a.Single(a.Multiplicity.MANDATORY,
                                    instruction_arguments.LINE_MATCHER)
        num_lines_arg = a.Single(a.Multiplicity.MANDATORY,
                                 a.Constant(matcher_options.NUM_LINES_ARGUMENT))

        symbol_argument = a.Single(a.Multiplicity.MANDATORY,
                                   syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.argument)

        return SyntaxElementDescription(
            self.matcher_element_name,
            [],
            [
                invokation_variant_from_args([mandatory_empty_arg],
                                             self._parser.fnap(_DESCRIPTION_OF_EMPTY)),

                invokation_variant_from_args([equals_arg,
                                              self.string_or_here_doc_or_file_arg.argument_usage(
                                                  a.Multiplicity.MANDATORY),
                                              ],
                                             self._parser.fnap(_DESCRIPTION_OF_EQUALS_STRING)),

                self._matches_regex_invokation_variant(),

                invokation_variant_from_args([num_lines_arg,
                                              syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.single_mandatory,
                                              ],
                                             self._parser.fnap(_DESCRIPTION_OF_NUM_LINES)),

                invokation_variant_from_args([quantifier_arg,
                                              line_arg,
                                              quantifier_separator_arg,
                                              line_matcher_arg,
                                              ],
                                             self._parser.fnap(_DESCRIPTION_OF_LINE_MATCHES)),

                invokation_variant_from_args([symbol_argument],
                                             self._parser.fnap(_SYMBOL_REF_DESCRIPTION)),

            ])

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        name_and_cross_ref_elements = [
            syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT,
            syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT,
            syntax_elements.LINE_MATCHER_SYNTAX_ELEMENT,
            syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT,
            syntax_elements.REGEX_SYNTAX_ELEMENT,
        ]

        name_and_cross_ref_elements += rel_opts.see_also_name_and_cross_refs(
            EXPECTED_FILE_REL_OPT_ARG_CONFIG.options)

        return (
                cross_reference_id_list(name_and_cross_ref_elements)
                +
                self.string_or_here_doc_or_file_arg.see_also_targets()
        )

    def _transformation_sed(self) -> SyntaxElementDescription:
        return cli_argument_syntax_element_description(
            instruction_arguments.STRING_TRANSFORMATION_ARGUMENT,
            self._parser.fnap(_TRANSFORMATION_DESCRIPTION),
            [
                invokation_variant_from_args([a.Single(a.Multiplicity.MANDATORY,
                                                       instruction_arguments.TRANSFORMATION_OPTION)]),
            ]
        )

    def _matches_regex_invokation_variant(self) -> InvokationVariant:
        matches_regex_arg = a.Single(a.Multiplicity.MANDATORY,
                                     a.Constant(
                                         matcher_options.MATCHES_ARGUMENT))

        return invokation_variant_from_args([matches_regex_arg,
                                             a.Single(a.Multiplicity.OPTIONAL,
                                                      a.Option(matcher_options.FULL_MATCH_ARGUMENT_OPTION)),
                                             syntax_elements.REGEX_SYNTAX_ELEMENT.single_mandatory,
                                             ],
                                            self._parser.fnap(_DESCRIPTION_OF_MATCHES_REGEX))


_MAIN_DESCRIPTION_REST = """\
Lines are separated by a single new-line character
(or a sequence representing a single new-line, on platforms
that use multiple characters as new-line).
"""

_TRANSFORMATION_DESCRIPTION = """\
Applies the matching to a transformed variant of the original string.
"""

_DESCRIPTION_OF_EMPTY = """\
Matches if the string is empty.
"""

_DESCRIPTION_OF_EQUALS_STRING = """\
Matches if the string is equal to a given
string, {HERE_DOCUMENT} or file.


Any {SYMBOL_REFERENCE_SYNTAX_ELEMENT} appearing in the file {expected_file_arg} is NOT substituted.
"""

_DESCRIPTION_OF_MATCHES_REGEX = """\
Matches if {REGEX} matches any part of the string.


If {full_regex_match} is given,
then {REGEX} must match the full string.
"""

_DESCRIPTION_OF_LINE_MATCHES = """\
Matches if {any}/{every} line of the string matches {LINE_MATCHER}.
"""

_DESCRIPTION_OF_NUM_LINES = """\
Matches if the number of lines of the string matches {INTEGER_MATCHER}.
"""

_SYMBOL_REF_DESCRIPTION = """\
Reference to {symbol_concept:a/q},
that must have been defined as {this_type:a/q}.
"""

DOCUMENTATION = _StringMatcherDocumentation()
