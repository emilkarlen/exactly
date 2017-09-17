from exactly_lib.common.help.see_also import CrossReferenceIdSeeAlsoItem, see_also_url
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.entity.concepts import ENVIRONMENT_VARIABLE_CONCEPT_INFO
from exactly_lib.help_texts.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId
from exactly_lib.instructions.assert_.utils.expression import parse as parse_expr
from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.instructions.assert_.utils.file_contents.instruction_options import EMPTY_ARGUMENT
from exactly_lib.instructions.assert_.utils.file_contents.parse_file_contents_assertion_part import \
    EXPECTED_FILE_REL_OPT_ARG_CONFIG
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_opts
from exactly_lib.test_case_utils import negation_of_predicate
from exactly_lib.util.cli_syntax.elements import argument as a

EMPTY_ARGUMENT_CONSTANT = a.Constant(EMPTY_ARGUMENT)

FILE_CONTENTS_ASSERTION = a.Named('FILE-CONTENTS-ASSERTION')


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
        self.expected_file_arg = a.Named('EXPECTED-PATH')
        format_map = {
            'checked_file': checked_file,
            'expected_file_arg': self.expected_file_arg.name,
            'any': instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT,
            'every': instruction_arguments.ALL_QUANTIFIER_ARGUMENT,
            'file_contents_assertion': FILE_CONTENTS_ASSERTION.name,
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
        equals_expected_arg = a.Choice(a.Multiplicity.MANDATORY,
                                       [instruction_arguments.STRING,
                                        instruction_arguments.HERE_DOCUMENT,
                                        self.expected_file_arg])
        line_arg = a.Single(a.Multiplicity.MANDATORY,
                            a.Constant(instruction_options.LINE_ARGUMENT))

        matches_arg = a.Single(a.Multiplicity.MANDATORY,
                               a.Constant(instruction_options.MATCHES_ARGUMENT))
        reg_ex_arg = a.Single(a.Multiplicity.MANDATORY,
                              instruction_arguments.REG_EX)
        num_lines_arg = a.Single(a.Multiplicity.MANDATORY,
                                 a.Constant(instruction_options.NUM_LINES_ARGUMENT))

        return SyntaxElementDescription(
            FILE_CONTENTS_ASSERTION.name,
            [],
            [
                InvokationVariant(_cls([mandatory_empty_arg]),
                                  self._paragraphs(_DESCRIPTION_OF_EMPTY)),
                InvokationVariant(_cls([equals_arg,
                                        equals_expected_arg,
                                        ]),
                                  self._paragraphs(_DESCRIPTION_OF_EQUALS_STRING)),
                InvokationVariant(_cls([num_lines_arg,
                                        parse_expr.MANDATORY_OPERATOR_ARGUMENT,
                                        parse_expr.MANDATORY_INTEGER_ARGUMENT,
                                        ]),
                                  self._paragraphs(_DESCRIPTION_OF_NUM_LINES)),

                InvokationVariant(_cls([quantifier_arg,
                                        line_arg,
                                        matches_arg,
                                        reg_ex_arg,
                                        ]),
                                  self._paragraphs(_DESCRIPTION_OF_LINE_MATCHES)),
            ]
        )

    def see_also_items(self) -> list:
        cross_refs = [CrossReferenceIdSeeAlsoItem(x) for x in self._see_also_cross_refs()]
        reg_ex_url = see_also_url('Python regular expressions',
                                  'https://docs.python.org/3/library/re.html#regular-expression-syntax')
        from exactly_lib.help_texts.entity import types
        types = [CrossReferenceIdSeeAlsoItem(types.LINES_TRANSFORMER_CONCEPT_INFO.cross_reference_target)]
        return cross_refs + types + [reg_ex_url]

    @staticmethod
    def _see_also_cross_refs() -> list:
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
Asserts that {checked_file} is empty.
"""

_DESCRIPTION_OF_EQUALS_STRING = """\
Asserts that the contents of {checked_file} is equal to a given
string, "here document" or file.
"""

_DESCRIPTION_OF_LINE_MATCHES = """\
Asserts that {any}/{every} line of {checked_file} matches a regular expression.
"""

_DESCRIPTION_OF_NUM_LINES = """\
Asserts that the number of lines of {checked_file} matches a given comparison expression.
"""
