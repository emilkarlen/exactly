from exactly_lib import program_info
from exactly_lib.common.help.see_also import CrossReferenceIdSeeAlsoItem, see_also_url
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.argument_rendering import path_syntax
from exactly_lib.help_texts.concepts import ENVIRONMENT_VARIABLE_CONCEPT_INFO
from exactly_lib.help_texts.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId
from exactly_lib.help_texts.names.formatting import InstructionName
from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.instructions.assert_.utils.file_contents.instruction_options import EMPTY_ARGUMENT
from exactly_lib.instructions.assert_.utils.file_contents.parsing import EXPECTED_FILE_REL_OPT_ARG_CONFIG
from exactly_lib.instructions.utils.documentation import documentation_text as dt
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_opts
from exactly_lib.test_case_file_structure import environment_variables
from exactly_lib.test_case_utils import negation_of_predicate
from exactly_lib.test_case_utils.file_transformer import env_vars_replacement
from exactly_lib.test_case_utils.lines_transformers.parse_lines_transformer import WITH_REPLACED_ENV_VARS_OPTION_NAME
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure import structures as docs

EMPTY_ARGUMENT_CONSTANT = a.Constant(EMPTY_ARGUMENT)


class FileContentsHelpParts:
    def __init__(self,
                 instruction_name: str,
                 checked_file: str,
                 initial_args_of_invokation_variants: list):
        self.instruction_name = instruction_name
        self.initial_args_of_invokation_variants = initial_args_of_invokation_variants
        self.expected_file_arg = a.Named('EXPECTED-PATH')
        self.with_replaced_env_vars_option = a.Option(WITH_REPLACED_ENV_VARS_OPTION_NAME)
        format_map = {
            'instruction_name': InstructionName(instruction_name),
            'checked_file': checked_file,
            'expected_file_arg': self.expected_file_arg.name,
            'not_option': instruction_arguments.NEGATION_ARGUMENT_STR,
            'program_name': program_info.PROGRAM_NAME,
            'home_act_env_var': environment_variables.ENV_VAR_HOME_ACT,
            'home_case_env_var': environment_variables.ENV_VAR_HOME_CASE,
            'home_env_var_with_replacement_precedence': env_vars_replacement.HOME_ENV_VAR_WITH_REPLACEMENT_PRECEDENCE,
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
        contains_arg = a.Single(a.Multiplicity.MANDATORY,
                                a.Constant(
                                    instruction_options.CONTAINS_ARGUMENT))
        reg_ex_arg = a.Single(a.Multiplicity.MANDATORY,
                              instruction_arguments.REG_EX)
        expected_file_arg = a.Single(a.Multiplicity.MANDATORY,
                                     self.expected_file_arg)
        optional_replace_env_vars_option = a.Single(a.Multiplicity.OPTIONAL,
                                                    self.with_replaced_env_vars_option)
        here_doc_arg = a.Single(a.Multiplicity.MANDATORY,
                                instruction_arguments.HERE_DOCUMENT)
        return [
            InvokationVariant(self._cls([optional_replace_env_vars_option,
                                         optional_not_arg,
                                         mandatory_empty_arg]),
                              self._paragraphs(_DESCRIPTION_OF_EMPTY)),
            InvokationVariant(self._cls([optional_replace_env_vars_option,
                                         optional_not_arg,
                                         equals_arg,
                                         here_doc_arg,
                                         ]),
                              self._paragraphs(_DESCRIPTION_OF_EQUALS_HERE_DOC)),
            InvokationVariant(self._cls([optional_replace_env_vars_option,
                                         optional_not_arg,
                                         equals_arg,
                                         expected_file_arg,
                                         ]),
                              self._paragraphs(_DESCRIPTION_OF_EQUALS_FILE)),
            InvokationVariant(self._cls([optional_replace_env_vars_option,
                                         optional_not_arg,
                                         contains_arg,
                                         reg_ex_arg,
                                         ]),
                              self._paragraphs(_DESCRIPTION_OF_CONTAINS)),
        ]

    def syntax_element_descriptions_at_top(self) -> list:
        return [negation_of_predicate.syntax_element_description()]

    def syntax_element_descriptions_at_bottom(self) -> list:
        mandatory_path = path_syntax.path_or_symbol_reference(a.Multiplicity.MANDATORY,
                                                              instruction_arguments.PATH_ARGUMENT)

        relativity_of_expected_arg = a.Named('RELATIVITY-OF-EXPECTED-PATH')
        optional_relativity_of_expected = a.Single(a.Multiplicity.OPTIONAL,
                                                   relativity_of_expected_arg)
        return [
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
                   cl_syntax.cli_argument_syntax_element_description(
                       self.with_replaced_env_vars_option,
                       self._with_replaced_env_vars_help()),
                   dt.here_document_syntax_element_description(self.instruction_name,
                                                               instruction_arguments.HERE_DOCUMENT),
               ]

    def see_also_items(self) -> list:
        cross_refs = [CrossReferenceIdSeeAlsoItem(x) for x in self._see_also_cross_refs()]
        reg_ex_url = see_also_url('Python regular expressions',
                                  'https://docs.python.org/3/library/re.html#regular-expression-syntax')
        return cross_refs + [reg_ex_url]

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

    def _with_replaced_env_vars_help(self) -> list:
        prologue = self._paragraphs(_WITH_REPLACED_ENV_VARS_PROLOGUE)
        variables_list = [docs.simple_header_only_list(sorted(environment_variables.ALL_REPLACED_ENV_VARS),
                                                       docs.lists.ListType.VARIABLE_LIST)]
        return prologue + variables_list


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

_WITH_REPLACED_ENV_VARS_PROLOGUE = """\
Every occurrence of a path that matches an {program_name} environment variable
in contents of {checked_file} is replaced with the name of the matching variable.
(Variable values are replaced with variable names.)


If {home_case_env_var} and {home_act_env_var} are equal, then paths will be replaced with
{home_env_var_with_replacement_precedence}.


The environment variables that are replaced are:
"""
