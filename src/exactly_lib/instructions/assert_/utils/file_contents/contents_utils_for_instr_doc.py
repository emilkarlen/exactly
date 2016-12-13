from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.help.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help.concepts.plain_concepts.environment_variable import ENVIRONMENT_VARIABLE_CONCEPT
from exactly_lib.help.utils.formatting import InstructionName
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.instructions.assert_.utils.file_contents import parsing
from exactly_lib.instructions.assert_.utils.file_contents.parsing import EMPTY_ARGUMENT, NOT_ARGUMENT
from exactly_lib.instructions.assert_.utils.file_contents.parsing import with_replaced_env_vars_help
from exactly_lib.instructions.utils.arg_parse import parse_here_doc_or_file_ref
from exactly_lib.instructions.utils.documentation import documentation_text as dt
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_opts
from exactly_lib.instructions.utils.documentation.documentation_text import CommandLineRenderingHelper
from exactly_lib.util.cli_syntax.elements import argument as a

EMPTY_ARGUMENT_CONSTANT = a.Constant(EMPTY_ARGUMENT)
NOT_ARGUMENT_CONSTANT = a.Constant(NOT_ARGUMENT)


class FileContentsHelpParts:
    def __init__(self,
                 instruction_name: str,
                 checked_file: str,
                 initial_args_of_invokation_variants: list):
        self.clr = CommandLineRenderingHelper()
        self.instruction_name = instruction_name
        self.initial_args_of_invokation_variants = initial_args_of_invokation_variants
        self.expected_file_arg = a.Named('EXPECTED-FILE')
        self.with_replaced_env_vars_option = a.Option(parsing.WITH_REPLACED_ENV_VARS_OPTION_NAME)
        format_map = {
            'instruction_name': InstructionName(instruction_name),
            'checked_file': checked_file,
            'expected_file_arg': self.expected_file_arg.name,
        }
        self._parser = TextParser(format_map)

    def _cls(self, additional_argument_usages: list) -> str:
        return self.clr.cl_syntax_for_args(self.initial_args_of_invokation_variants + additional_argument_usages)

    def invokation_variants(self) -> list:
        mandatory_empty_arg = a.Single(a.Multiplicity.MANDATORY,
                                       EMPTY_ARGUMENT_CONSTANT)
        mandatory_not_arg = a.Single(a.Multiplicity.MANDATORY,
                                     NOT_ARGUMENT_CONSTANT)
        expected_file_arg = a.Single(a.Multiplicity.MANDATORY,
                                     self.expected_file_arg)
        optional_replace_env_vars_option = a.Single(a.Multiplicity.OPTIONAL,
                                                    self.with_replaced_env_vars_option)
        here_doc_arg = a.Single(a.Multiplicity.MANDATORY, dt.HERE_DOCUMENT)
        return [
            InvokationVariant(self._cls([mandatory_empty_arg]),
                              self._paragraphs('Asserts that {checked_file} is empty.')),
            InvokationVariant(self._cls([mandatory_not_arg, mandatory_empty_arg]),
                              self._paragraphs('Asserts that {checked_file} is non-empty.')),
            InvokationVariant(self._cls([optional_replace_env_vars_option,
                                         here_doc_arg,
                                         ]),
                              self._paragraphs("""\
                              Asserts that the contents of {checked_file}
                              is equal to the contents of a "here document".
                              """)),
            InvokationVariant(self._cls([optional_replace_env_vars_option,
                                         # rel_opts.OPTIONAL_RELATIVITY_ARGUMENT_USAGE,
                                         expected_file_arg,
                                         ]),
                              self._paragraphs("""\
                              Asserts that the contents of {checked_file}
                              is equal to the contents of {expected_file_arg}.
                              """)),
        ]

    def syntax_element_descriptions(self) -> list:
        mandatory_path = a.Single(a.Multiplicity.MANDATORY,
                                  dt.FILE_ARGUMENT)
        relativity_of_expected_arg = a.Named('RELATIVITY-OF-EXPECTED-FILE')
        optional_relativity_of_expected = a.Single(a.Multiplicity.OPTIONAL,
                                                   relativity_of_expected_arg)
        return [
            SyntaxElementDescription(self.expected_file_arg.name,
                                     self._paragraphs("The file that contains the expected contents."),
                                     [InvokationVariant(self.clr.cl_syntax_for_args(
                                         [optional_relativity_of_expected,
                                          mandatory_path]),
                                         rel_opts.default_relativity_for_rel_opt_type(
                                             parse_here_doc_or_file_ref.CONFIGURATION.argument_syntax_name,
                                             parse_here_doc_or_file_ref.CONFIGURATION.default_option)
                                     )]
                                     ),
            rel_opts.relativity_syntax_element_description(dt.FILE_ARGUMENT,
                                                           parse_here_doc_or_file_ref.CONFIGURATION.accepted_options,
                                                           relativity_of_expected_arg),
            self.clr.cli_argument_syntax_element_description(
                self.with_replaced_env_vars_option,
                with_replaced_env_vars_help(self._parser.format('the contents of {checked_file}'))),
            dt.here_document_syntax_element_description(self.instruction_name,
                                                        dt.HERE_DOCUMENT),
        ]

    def see_also(self) -> list:
        concepts = rel_opts.see_also_concepts(parse_here_doc_or_file_ref.CONFIGURATION.accepted_options)
        if ENVIRONMENT_VARIABLE_CONCEPT not in concepts:
            concepts.append(ENVIRONMENT_VARIABLE_CONCEPT)
        return list(map(ConceptDocumentation.cross_reference_target, concepts))

    def _paragraphs(self, s: str, extra: dict = None) -> list:
        """
        :rtype: [`ParagraphItem`]
        """
        return self._parser.fnap(s, extra)
