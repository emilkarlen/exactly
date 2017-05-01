import exactly_lib.instructions.assert_.utils.file_contents.instruction_options
from exactly_lib.common.help.see_also import CrossReferenceIdSeeAlsoItem, see_also_url
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.help.concepts.names_and_cross_references import ENVIRONMENT_VARIABLE_CONCEPT_INFO
from exactly_lib.help.utils.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId
from exactly_lib.help.utils.names.formatting import InstructionName
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.argument_rendering import path_syntax
from exactly_lib.instructions.assert_.utils.file_contents.instruction_options import NOT_ARGUMENT, EMPTY_ARGUMENT
from exactly_lib.instructions.assert_.utils.file_contents.parsing import with_replaced_env_vars_help
from exactly_lib.instructions.utils.arg_parse import parse_here_doc_or_file_ref
from exactly_lib.instructions.utils.documentation import documentation_text as dt
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_opts
from exactly_lib.util.cli_syntax.elements import argument as a

EMPTY_ARGUMENT_CONSTANT = a.Constant(EMPTY_ARGUMENT)
NOT_ARGUMENT_CONSTANT = a.Constant(NOT_ARGUMENT)


class FileContentsHelpParts:
    def __init__(self,
                 instruction_name: str,
                 checked_file: str,
                 initial_args_of_invokation_variants: list):
        self.instruction_name = instruction_name
        self.initial_args_of_invokation_variants = initial_args_of_invokation_variants
        self.expected_file_arg = a.Named('EXPECTED-FILE')
        self.with_replaced_env_vars_option = a.Option(
            exactly_lib.instructions.assert_.utils.file_contents.instruction_options.WITH_REPLACED_ENV_VARS_OPTION_NAME)
        format_map = {
            'instruction_name': InstructionName(instruction_name),
            'checked_file': checked_file,
            'expected_file_arg': self.expected_file_arg.name,
            'not_option': NOT_ARGUMENT,
        }
        self._parser = TextParser(format_map)

    def _cls(self, additional_argument_usages: list) -> str:
        return cl_syntax.cl_syntax_for_args(self.initial_args_of_invokation_variants + additional_argument_usages)

    def invokation_variants(self) -> list:
        mandatory_empty_arg = a.Single(a.Multiplicity.MANDATORY,
                                       EMPTY_ARGUMENT_CONSTANT)

        optional_not_arg = a.Single(a.Multiplicity.OPTIONAL,
                                    NOT_ARGUMENT_CONSTANT)
        equals_arg = a.Single(a.Multiplicity.MANDATORY,
                              a.Constant(
                                  exactly_lib.instructions.assert_.utils.file_contents.instruction_options.EQUALS_ARGUMENT))
        contains_arg = a.Single(a.Multiplicity.MANDATORY,
                                a.Constant(
                                    exactly_lib.instructions.assert_.utils.file_contents.instruction_options.CONTAINS_ARGUMENT))
        reg_ex_arg = a.Single(a.Multiplicity.MANDATORY,
                              dt.REG_EX)
        expected_file_arg = a.Single(a.Multiplicity.MANDATORY,
                                     self.expected_file_arg)
        optional_replace_env_vars_option = a.Single(a.Multiplicity.OPTIONAL,
                                                    self.with_replaced_env_vars_option)
        here_doc_arg = a.Single(a.Multiplicity.MANDATORY, dt.HERE_DOCUMENT)
        return [
            InvokationVariant(self._cls([optional_not_arg,
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

    def syntax_element_descriptions(self) -> list:
        mandatory_path = a.Single(a.Multiplicity.MANDATORY,
                                  path_syntax.FILE_ARGUMENT)
        relativity_of_expected_arg = a.Named('RELATIVITY-OF-EXPECTED-FILE')
        optional_relativity_of_expected = a.Single(a.Multiplicity.OPTIONAL,
                                                   relativity_of_expected_arg)
        return [
                   SyntaxElementDescription(self.expected_file_arg.name,
                                            self._paragraphs("The file that contains the expected contents."),
                                            [InvokationVariant(cl_syntax.cl_syntax_for_args(
                                                [optional_relativity_of_expected,
                                                 mandatory_path]),
                                                rel_opts.default_relativity_for_rel_opt_type(
                                                    parse_here_doc_or_file_ref.CONFIGURATION.argument_syntax_name,
                                                    parse_here_doc_or_file_ref.CONFIGURATION.options.default_option)
                                            )]
                                            ),
               ] + \
               rel_opts.relativity_syntax_element_descriptions(
                   path_syntax.FILE_ARGUMENT,
                   parse_here_doc_or_file_ref.CONFIGURATION.options,
                   relativity_of_expected_arg) + \
               [
                   SyntaxElementDescription(dt.REG_EX.name,
                                            self._parser.fnap('A Python regular expression.')),
                   cl_syntax.cli_argument_syntax_element_description(
                       self.with_replaced_env_vars_option,
                       with_replaced_env_vars_help(self._parser.format('the contents of {checked_file}'))),
                   dt.here_document_syntax_element_description(self.instruction_name,
                                                               dt.HERE_DOCUMENT),
               ]

    def see_also_items(self) -> list:
        cross_refs = [CrossReferenceIdSeeAlsoItem(x) for x in self._see_also_cross_refs()]
        reg_ex_url = see_also_url('Python regular expressions',
                                  'https://docs.python.org/3/library/re.html#regular-expression-syntax')
        return cross_refs + [reg_ex_url]

    @staticmethod
    def _see_also_cross_refs() -> list:
        concepts = rel_opts.see_also_concepts(parse_here_doc_or_file_ref.CONFIGURATION.options)
        if ENVIRONMENT_VARIABLE_CONCEPT_INFO not in concepts:
            concepts.append(ENVIRONMENT_VARIABLE_CONCEPT_INFO)
        return list(map(SingularAndPluralNameAndCrossReferenceId.cross_reference_target.fget, concepts))

    def _paragraphs(self, s: str, extra: dict = None) -> list:
        """
        :rtype: [`ParagraphItem`]
        """
        return self._parser.fnap(s, extra)


_DESCRIPTION_TAL_FOR_NEGATION = """\

If {not_option} is given, the assertion is negated."""

_DESCRIPTION_OF_EMPTY = """\
Asserts that {checked_file} is empty.
""" + _DESCRIPTION_TAL_FOR_NEGATION

_DESCRIPTION_OF_EQUALS_HERE_DOC = """\
Asserts that the contents of {checked_file} is equal to the contents of a "here document".
""" + _DESCRIPTION_TAL_FOR_NEGATION

_DESCRIPTION_OF_EQUALS_FILE = """\
Asserts that the contents of {checked_file} is equal to the contents of a file.
""" + _DESCRIPTION_TAL_FOR_NEGATION

_DESCRIPTION_OF_CONTAINS = """\
Asserts that the contents of {checked_file} contains a line matching a regular expression.
""" + _DESCRIPTION_TAL_FOR_NEGATION
