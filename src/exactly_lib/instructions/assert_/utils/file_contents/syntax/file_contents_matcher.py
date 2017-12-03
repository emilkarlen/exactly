from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.argument_rendering.path_syntax import the_path_of
from exactly_lib.help_texts.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.help_texts.entity import syntax_elements, types
from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.instructions.assert_.utils.file_contents.instruction_options import EMPTY_ARGUMENT
from exactly_lib.instructions.assert_.utils.file_contents.parse_file_contents_assertion_part import \
    EXPECTED_FILE_REL_OPT_ARG_CONFIG
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_opts
from exactly_lib.instructions.utils.documentation.string_or_here_doc_or_file import StringOrHereDocOrFile
from exactly_lib.test_case_utils.parse.parse_here_doc_or_file_ref import FILE_ARGUMENT_OPTION
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.textformat_parser import TextParser

_EXPECTED_PATH_NAME = 'PATH-OF-EXPECTED'

_RELATIVITY_OF_EXPECTED_PATH_NAME = 'RELATIVITY-OF-EXPECTED-PATH'


class FileContentsMatcherHelp:
    def __init__(self):
        self.expected_file_arg = a.Option(FILE_ARGUMENT_OPTION,
                                          _EXPECTED_PATH_NAME)
        self.string_or_here_doc_or_file_arg = StringOrHereDocOrFile(
            _EXPECTED_PATH_NAME,
            _RELATIVITY_OF_EXPECTED_PATH_NAME,
            EXPECTED_FILE_REL_OPT_ARG_CONFIG,
            the_path_of('the file that contains the expected contents.'))
        self._parser = TextParser({
            'expected_file_arg': _EXPECTED_PATH_NAME,
            'any': instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT,
            'every': instruction_arguments.ALL_QUANTIFIER_ARGUMENT,
            'LINE_MATCHER': instruction_arguments.LINE_MATCHER.name,
            'INTEGER_COMPARISON': syntax_elements.INTEGER_COMPARISON_SYNTAX_ELEMENT.singular_name,
        })

    def _cls(self, additional_argument_usages: list) -> str:
        return cl_syntax.cl_syntax_for_args(additional_argument_usages)

    def syntax_element_description(self) -> SyntaxElementDescription:
        return SyntaxElementDescription(
            syntax_elements.FILE_CONTENTS_MATCHER.argument.name,
            [],
            self.invokation_variants()
        )

    def invokation_variants(self) -> list:
        def _cls(args: list) -> str:
            return cl_syntax.cl_syntax_for_args(args)

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

        return [
            InvokationVariant(_cls([mandatory_empty_arg]),
                              self._paragraphs(_DESCRIPTION_OF_EMPTY)),

            InvokationVariant(_cls([equals_arg,
                                    self.string_or_here_doc_or_file_arg.argument_usage(a.Multiplicity.MANDATORY),
                                    ]),
                              self._paragraphs(_DESCRIPTION_OF_EQUALS_STRING)),

            InvokationVariant(_cls([num_lines_arg,
                                    syntax_elements.INTEGER_COMPARISON_SYNTAX_ELEMENT.single_mandatory,
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

    def referenced_syntax_element_descriptions(self) -> list:
        return self.string_or_here_doc_or_file_arg.syntax_element_descriptions()

    def see_also_targets(self) -> list:
        name_and_cross_ref_elements = rel_opts.see_also_name_and_cross_refs(
            EXPECTED_FILE_REL_OPT_ARG_CONFIG.options)

        name_and_cross_ref_elements += [
            syntax_elements.INTEGER_COMPARISON_SYNTAX_ELEMENT,
            types.LINE_MATCHER_TYPE_INFO,
        ]

        return (
            cross_reference_id_list(name_and_cross_ref_elements)
            +
            self.string_or_here_doc_or_file_arg.see_also_targets()
        )

    def _paragraphs(self, s: str, extra: dict = None) -> list:
        """
        :rtype: [`ParagraphItem`]
        """
        return self._parser.fnap(s, extra)


_DESCRIPTION_OF_EMPTY = """\
Matches if the contents is empty.
"""

_DESCRIPTION_OF_EQUALS_STRING = """\
Matches if the contents is equal to a given
string, "here document" or file.
"""

_DESCRIPTION_OF_LINE_MATCHES = """\
Matches if {any}/{every} line of the contents matches {LINE_MATCHER}.
"""

_DESCRIPTION_OF_NUM_LINES = """\
Matches if the number of lines of the contents matches {INTEGER_COMPARISON}.
"""
