from exactly_lib import program_info
from exactly_lib.common.help.see_also import CrossReferenceIdSeeAlsoItem, see_also_url
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.argument_rendering import path_syntax
from exactly_lib.help_texts.entity.concepts import ENVIRONMENT_VARIABLE_CONCEPT_INFO
from exactly_lib.help_texts.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId
from exactly_lib.help_texts.names.formatting import InstructionName
from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.instructions.assert_.utils.file_contents.instruction_options import EMPTY_ARGUMENT
from exactly_lib.instructions.assert_.utils.file_contents.parsing import EXPECTED_FILE_REL_OPT_ARG_CONFIG
from exactly_lib.instructions.utils.documentation import documentation_text as dt
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_opts
from exactly_lib.test_case_file_structure import environment_variables
from exactly_lib.test_case_utils import negation_of_predicate
from exactly_lib.test_case_utils.lines_transformer import parse_lines_transformer
from exactly_lib.util.cli_syntax.elements import argument as a

EMPTY_ARGUMENT_CONSTANT = a.Constant(EMPTY_ARGUMENT)


class FileContentsHelpParts:
    def __init__(self,
                 instruction_name: str,
                 checked_file: str,
                 initial_args_of_invokation_variants: list):
        self.instruction_name = instruction_name
        self.initial_args_of_invokation_variants = initial_args_of_invokation_variants
        self.expected_file_arg = a.Named('EXPECTED-PATH')
        format_map = {
            'instruction_name': InstructionName(instruction_name),
            'checked_file': checked_file,
            'expected_file_arg': self.expected_file_arg.name,
            'not_option': instruction_arguments.NEGATION_ARGUMENT_STR,
            'program_name': program_info.PROGRAM_NAME,
            'home_act_env_var': environment_variables.ENV_VAR_HOME_ACT,
            'home_case_env_var': environment_variables.ENV_VAR_HOME_CASE,
            'transformation': instruction_arguments.LINES_TRANSFORMATION_ARGUMENT.name,
        }
        self._parser = TextParser(format_map)

    def _cls(self, additional_argument_usages: list) -> str:
        return cl_syntax.cl_syntax_for_args(self.initial_args_of_invokation_variants + additional_argument_usages)

    def invokation_variants(self) -> list:
        mandatory_empty_arg = a.Single(a.Multiplicity.MANDATORY,
                                       EMPTY_ARGUMENT_CONSTANT)

        optional_not_arg = negation_of_predicate.optional_negation_argument_usage()

        equals_arg = a.Single(a.Multiplicity.MANDATORY,
                              a.Constant(
                                  instruction_options.EQUALS_ARGUMENT))
        expected_file_arg = a.Single(a.Multiplicity.MANDATORY,
                                     self.expected_file_arg)
        optional_transformation_option = a.Single(a.Multiplicity.OPTIONAL,
                                                  instruction_arguments.LINES_TRANSFORMATION_ARGUMENT)
        here_doc_arg = a.Single(a.Multiplicity.MANDATORY,
                                instruction_arguments.HERE_DOCUMENT)
        return [
            InvokationVariant(self._cls([optional_transformation_option,
                                         optional_not_arg,
                                         mandatory_empty_arg]),
                              self._paragraphs(_DESCRIPTION_OF_EMPTY)),
            InvokationVariant(self._cls([optional_transformation_option,
                                         optional_not_arg,
                                         equals_arg,
                                         here_doc_arg,
                                         ]),
                              self._paragraphs(_DESCRIPTION_OF_EQUALS_HERE_DOC)),
            InvokationVariant(self._cls([optional_transformation_option,
                                         optional_not_arg,
                                         equals_arg,
                                         expected_file_arg,
                                         ]),
                              self._paragraphs(_DESCRIPTION_OF_EQUALS_FILE)),
            self._any_line_matches_invokation_variant(optional_transformation_option,
                                                      optional_not_arg),
        ]

    def _any_line_matches_invokation_variant(self,
                                             optional_transformation_option: a.ArgumentUsage,
                                             optional_not_arg: a.ArgumentUsage) -> InvokationVariant:
        any_arg = a.Single(a.Multiplicity.MANDATORY,
                           a.Constant(instruction_options.ANY_LINE_ARGUMENT))

        line_arg = a.Single(a.Multiplicity.MANDATORY,
                            a.Constant(instruction_options.LINE_ARGUMENT))

        matches_arg = a.Single(a.Multiplicity.MANDATORY,
                               a.Constant(instruction_options.MATCHES_ARGUMENT))

        reg_ex_arg = a.Single(a.Multiplicity.MANDATORY,
                              instruction_arguments.REG_EX)
        return InvokationVariant(self._cls([optional_transformation_option,
                                            optional_not_arg,
                                            any_arg,
                                            line_arg,
                                            matches_arg,
                                            reg_ex_arg,
                                            ]),
                                 self._paragraphs(_DESCRIPTION_OF_CONTAINS))

    def syntax_element_descriptions_at_top(self) -> list:
        return [negation_of_predicate.syntax_element_description()]

    def syntax_element_descriptions_at_bottom(self) -> list:
        transformation = parse_lines_transformer.selection_syntax_element_description()

        transformer = parse_lines_transformer.transformer_syntax_element_description()

        mandatory_path = path_syntax.path_or_symbol_reference(a.Multiplicity.MANDATORY,
                                                              instruction_arguments.PATH_ARGUMENT)

        relativity_of_expected_arg = a.Named('RELATIVITY-OF-EXPECTED-PATH')
        optional_relativity_of_expected = a.Single(a.Multiplicity.OPTIONAL,
                                                   relativity_of_expected_arg)
        return [
                   transformation,
                   transformer,
                   SyntaxElementDescription(self.expected_file_arg.name,
                                            self._paragraphs("The file that contains the expected contents."),
                                            [InvokationVariant(cl_syntax.cl_syntax_for_args(
                                                [optional_relativity_of_expected,
                                                 mandatory_path]),
                                                rel_opts.default_relativity_for_rel_opt_type(
                                                    EXPECTED_FILE_REL_OPT_ARG_CONFIG.argument_syntax_name,
                                                    EXPECTED_FILE_REL_OPT_ARG_CONFIG.options.default_option)
                                            )]
                                            ),
               ] + \
               rel_opts.relativity_syntax_element_descriptions(
                   instruction_arguments.PATH_ARGUMENT,
                   EXPECTED_FILE_REL_OPT_ARG_CONFIG.options,
                   relativity_of_expected_arg) + \
               [
                   SyntaxElementDescription(instruction_arguments.REG_EX.name,
                                            self._parser.fnap('A Python regular expression.')),
                   dt.here_document_syntax_element_description(self.instruction_name,
                                                               instruction_arguments.HERE_DOCUMENT),
               ]

    def see_also_items(self) -> list:
        cross_refs = [CrossReferenceIdSeeAlsoItem(x) for x in self._see_also_cross_refs()]
        reg_ex_url = see_also_url('Python regular expressions',
                                  'https://docs.python.org/3/library/re.html#regular-expression-syntax')
        from exactly_lib.help_texts.entity import types
        types = [CrossReferenceIdSeeAlsoItem(types.LINE_MATCHER_CONCEPT_INFO.cross_reference_target),
                 CrossReferenceIdSeeAlsoItem(types.LINES_TRANSFORMER_CONCEPT_INFO.cross_reference_target)]
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

_DESCRIPTION_OF_EQUALS_HERE_DOC = """\
Asserts that the contents of {checked_file} is equal to the contents of a "here document".
"""

_DESCRIPTION_OF_EQUALS_FILE = """\
Asserts that the contents of {checked_file} is equal to the contents of file {expected_file_arg}.
"""

_DESCRIPTION_OF_CONTAINS = """\
Asserts that the contents of {checked_file} contains a line matching a regular expression.
"""
