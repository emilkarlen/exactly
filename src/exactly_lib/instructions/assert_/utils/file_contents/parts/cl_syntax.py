from exactly_lib.common.help.see_also import SeeAlsoSet
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.entity import syntax_element
from exactly_lib.help_texts.entity.concepts import ENVIRONMENT_VARIABLE_CONCEPT_INFO
from exactly_lib.help_texts.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId
from exactly_lib.instructions.assert_.utils.expression import parse as parse_expr
from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.instructions.assert_.utils.file_contents.instruction_options import EMPTY_ARGUMENT
from exactly_lib.instructions.assert_.utils.file_contents.parse_file_contents_assertion_part import \
    EXPECTED_FILE_REL_OPT_ARG_CONFIG
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_opts
from exactly_lib.instructions.utils.documentation.string_or_here_doc_or_file import StringOrHereDocOrFile
from exactly_lib.test_case_utils import negation_of_predicate
from exactly_lib.test_case_utils.parse.parse_here_doc_or_file_ref import FILE_ARGUMENT_OPTION
from exactly_lib.util.cli_syntax.elements import argument as a

EMPTY_ARGUMENT_CONSTANT = a.Constant(EMPTY_ARGUMENT)

FILE_CONTENTS_ASSERTION = a.Named('FILE-CONTENTS-ASSERTION')

EXPECTED_PATH_NAME = 'EXPECTED-PATH'
RELATIVITY_OF_EXPECTED_PATH_NAME = 'RELATIVITY-OF-EXPECTED-PATH'


def file_contents_assertion_arguments() -> list:
    file_contents_arg = a.Single(a.Multiplicity.MANDATORY,
                                 FILE_CONTENTS_ASSERTION)

    optional_not_arg = negation_of_predicate.optional_negation_argument_usage()

    optional_transformation_option = a.Single(a.Multiplicity.OPTIONAL,
                                              instruction_arguments.LINES_TRANSFORMATION_ARGUMENT)
    return [optional_transformation_option,
            optional_not_arg,
            file_contents_arg]


class FileContentsAssertionHelp:
    def __init__(self,
                 checked_file: str):
        self.expected_file_arg = a.Option(FILE_ARGUMENT_OPTION,
                                          EXPECTED_PATH_NAME)
        self.string_or_here_doc_or_file_arg = StringOrHereDocOrFile(
            EXPECTED_PATH_NAME,
            RELATIVITY_OF_EXPECTED_PATH_NAME,
            EXPECTED_FILE_REL_OPT_ARG_CONFIG,
            'The file that contains the expected contents.')
        format_map = {
            'checked_file': checked_file,
            'expected_file_arg': EXPECTED_PATH_NAME,
            'any': instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT,
            'every': instruction_arguments.ALL_QUANTIFIER_ARGUMENT,
            'file_contents_assertion': FILE_CONTENTS_ASSERTION.name,
            'line_matcher': instruction_arguments.LINE_MATCHER.name,
        }
        self._parser = TextParser(format_map)

    def _cls(self, additional_argument_usages: list) -> str:
        return cl_syntax.cl_syntax_for_args(additional_argument_usages)

    def file_contents_assertion_sed(self) -> SyntaxElementDescription:
        def _cls(args: list) -> str:
            return cl_syntax.cl_syntax_for_args(args)

        mandatory_empty_arg = a.Single(a.Multiplicity.MANDATORY,
                                       EMPTY_ARGUMENT_CONSTANT)
        quantifier_arg = a.Choice(a.Multiplicity.MANDATORY,
                                  [
                                      a.Constant(
                                          instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT),
                                      a.Constant(
                                          instruction_arguments.ALL_QUANTIFIER_ARGUMENT),
                                  ])
        equals_arg = a.Single(a.Multiplicity.MANDATORY,
                              a.Constant(
                                  instruction_options.EQUALS_ARGUMENT))
        line_arg = a.Single(a.Multiplicity.MANDATORY,
                            a.Constant(instruction_options.LINE_ARGUMENT))

        quantifier_separator_arg = a.Single(a.Multiplicity.MANDATORY,
                                            a.Constant(instruction_arguments.QUANTIFICATION_SEPARATOR_ARGUMENT))

        matches_arg = a.Single(a.Multiplicity.MANDATORY,
                               a.Constant(instruction_options.MATCHES_ARGUMENT))
        line_matcher_arg = a.Single(a.Multiplicity.MANDATORY,
                                    instruction_arguments.LINE_MATCHER)
        num_lines_arg = a.Single(a.Multiplicity.MANDATORY,
                                 a.Constant(instruction_options.NUM_LINES_ARGUMENT))

        return SyntaxElementDescription(
            FILE_CONTENTS_ASSERTION.name,
            [],
            [
                InvokationVariant(_cls([mandatory_empty_arg]),
                                  self._paragraphs(_DESCRIPTION_OF_EMPTY)),
                InvokationVariant(_cls([equals_arg,
                                        self.string_or_here_doc_or_file_arg.argument_usage(a.Multiplicity.MANDATORY),
                                        ]),
                                  self._paragraphs(_DESCRIPTION_OF_EQUALS_STRING)),
                InvokationVariant(_cls([num_lines_arg,
                                        parse_expr.MANDATORY_OPERATOR_ARGUMENT,
                                        parse_expr.MANDATORY_INTEGER_ARGUMENT,
                                        ]),
                                  self._paragraphs(_DESCRIPTION_OF_NUM_LINES)),

                InvokationVariant(_cls([quantifier_arg,
                                        line_arg,
                                        quantifier_separator_arg,
                                        matches_arg,
                                        line_matcher_arg,
                                        ]),
                                  self._paragraphs(_DESCRIPTION_OF_LINE_MATCHES)),
            ]
        )

    def used_syntax_element_descriptions(self) -> list:
        return self.string_or_here_doc_or_file_arg.syntax_element_descriptions()

    def see_also_items(self) -> list:
        return self.see_also_set().see_also_items

    def see_also_set(self) -> SeeAlsoSet:
        from exactly_lib.help_texts.entity import types
        cross_refs = self.see_also_targets()
        cross_refs += [
            syntax_element.REGEX_SYNTAX_ELEMENT.cross_reference_target,
            types.LINES_TRANSFORMER_CONCEPT_INFO.cross_reference_target,
            types.LINE_MATCHER_CONCEPT_INFO.cross_reference_target,
        ]
        return SeeAlsoSet(cross_refs).union(self.string_or_here_doc_or_file_arg.see_also_set())

    @staticmethod
    def see_also_targets() -> list:
        concepts = rel_opts.see_also_concepts(EXPECTED_FILE_REL_OPT_ARG_CONFIG.options)
        if ENVIRONMENT_VARIABLE_CONCEPT_INFO not in concepts:
            concepts.append(ENVIRONMENT_VARIABLE_CONCEPT_INFO)
        return list(map(SingularAndPluralNameAndCrossReferenceId.cross_reference_target.fget, concepts))

    def _paragraphs(self, s: str, extra: dict = None) -> list:
        """
        :rtype: [`ParagraphItem`]
        """
        return self._parser.fnap(s, extra)


_DESCRIPTION_OF_EMPTY = """\
Asserts that {checked_file} is an empty file.
"""

_DESCRIPTION_OF_EQUALS_STRING = """\
Asserts that the contents of {checked_file} is equal to a given
string, "here document" or file.
"""

_DESCRIPTION_OF_LINE_MATCHES = """\
Asserts that {any}/{every} line of {checked_file} matches a {line_matcher}.
"""

_DESCRIPTION_OF_NUM_LINES = """\
Asserts that the number of lines of {checked_file} matches a given comparison expression.
"""
