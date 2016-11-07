import shlex

from exactly_lib.common.instruction_documentation import InvokationVariant, \
    SyntaxElementDescription
from exactly_lib.instructions.utils import file_properties
from exactly_lib.instructions.utils import instruction_from_parts_for_executing_sub_process as spe_parts
from exactly_lib.instructions.utils.arg_parse import parse_executable_file
from exactly_lib.instructions.utils.arg_parse import parse_file_ref
from exactly_lib.instructions.utils.arg_parse.parse_executable_file import PARSE_FILE_REF_CONFIGURATION
from exactly_lib.instructions.utils.arg_parse.parse_utils import TokenStream
from exactly_lib.instructions.utils.cmd_and_args_resolvers import CmdAndArgsResolverForExecutableFileBase
from exactly_lib.instructions.utils.documentation import documentation_text as dt
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.instructions.utils.executable_file import ExecutableFile
from exactly_lib.instructions.utils.file_ref import FileRef
from exactly_lib.instructions.utils.file_ref_check import FileRefCheckValidator, FileRefCheck
from exactly_lib.instructions.utils.instruction_parts import InstructionInfoForConstructingAnInstructionFromParts
from exactly_lib.instructions.utils.pre_or_post_validation import AndValidator
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax


def instruction_parser(
        instruction_info: InstructionInfoForConstructingAnInstructionFromParts) -> SingleInstructionParser:
    return spe_parts.InstructionParser(instruction_info,
                                       SetupParser())


INTERPRET_OPTION_NAME = a.OptionName(long_name='interpret')
INTERPRET_OPTION = long_option_syntax(INTERPRET_OPTION_NAME.long)

SOURCE_OPTION_NAME = a.OptionName(long_name='source')
SOURCE_OPTION = long_option_syntax(SOURCE_OPTION_NAME.long)

OPTIONS_SEPARATOR_ARGUMENT = '--'

NON_ASSERT_PHASE_DESCRIPTION_REST = """\
It is considered an error if the program exits with a non-zero exit code.
"""

_SOURCE_SYNTAX_ELEMENT_NAME = 'SOURCE'


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self,
                 name: str,
                 single_line_description: str = 'Runs a program',
                 additional_format_map: dict = None,
                 description_rest_text: str = None):
        self.description_rest_text = description_rest_text
        self.executable_arg = a.Named('EXECUTABLE')
        format_map = {'EXECUTABLE': self.executable_arg.name}
        if additional_format_map:
            format_map.update(additional_format_map)
        super().__init__(name, format_map)
        self.relativity_arg_path = dt.PATH_ARGUMENT
        self.mandatory_path = a.Single(a.Multiplicity.MANDATORY,
                                       dt.PATH_ARGUMENT)
        self.optional_relativity = rel_path_doc.OPTIONAL_RELATIVITY_ARGUMENT_USAGE
        self.mandatory_executable = a.Single(a.Multiplicity.MANDATORY,
                                             self.executable_arg)
        self.generic_arg = a.Named('ARGUMENT')
        self.zero_or_more_generic_args = a.Single(a.Multiplicity.ZERO_OR_MORE,
                                                  self.generic_arg)
        self.optional_arg_sep = a.Single(a.Multiplicity.OPTIONAL,
                                         a.Constant(OPTIONS_SEPARATOR_ARGUMENT))
        self._single_line_description = single_line_description

    def single_line_description(self) -> str:
        return self._single_line_description

    def main_description_rest(self) -> list:
        if self.description_rest_text:
            return self._paragraphs(self.description_rest_text)
        return []

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(self._cl_syntax_for_args([
                self.mandatory_executable,
                self.optional_arg_sep,
                self.zero_or_more_generic_args]),
                self._paragraphs(
                    """\
                    Executes the given executable with the given command line arguments.

                    The arguments are splitted according to shell syntax.
                    """)),
            InvokationVariant(self._cl_syntax_for_args([
                self.mandatory_executable,
                a.Single(a.Multiplicity.MANDATORY, a.Option(INTERPRET_OPTION_NAME)),
                self.optional_relativity,
                self.mandatory_path,
                self.optional_arg_sep,
                self.zero_or_more_generic_args]),
                self._paragraphs(
                    """\
                    Interprets the given file using {EXECUTABLE}.

                    Arguments are splitted according to shell syntax.
                    """)),
            InvokationVariant(self._cl_syntax_for_args([
                self.mandatory_executable,
                a.Single(a.Multiplicity.MANDATORY, a.Option(SOURCE_OPTION_NAME)),
                a.Single(a.Multiplicity.MANDATORY, a.Named(_SOURCE_SYNTAX_ELEMENT_NAME))]),
                self._paragraphs(
                    """\
                    Interprets the given SOURCE using {EXECUTABLE}.

                    SOURCE is taken literary, and is given as a single argument to {EXECUTABLE}.
                    """)),
        ]

    def syntax_element_descriptions(self) -> list:
        executable_path_arguments = [self.optional_relativity,
                                     self.mandatory_path]
        executable_in_parenthesis_arguments = ([a.Single(a.Multiplicity.MANDATORY, a.Constant('('))] +
                                               executable_path_arguments +
                                               [self.zero_or_more_generic_args,
                                                a.Single(a.Multiplicity.MANDATORY, a.Constant(')'))])
        default_relativity_desc = rel_path_doc.default_relativity_for_rel_opt_type(
            dt.PATH_ARGUMENT.name,
            PARSE_FILE_REF_CONFIGURATION.default_option)
        return [
            SyntaxElementDescription(
                self.executable_arg.name,
                self._paragraphs('Specifies a program by giving the path to an executable file, '
                                 'and optionally also arguments to the program.'),
                [
                    InvokationVariant(self._cl_syntax_for_args(executable_path_arguments),
                                      default_relativity_desc),
                    InvokationVariant(self._cl_syntax_for_args(executable_in_parenthesis_arguments),
                                      self._paragraphs('An executable program with arguments. '
                                                       '(Must be inside parentheses.)') +
                                      default_relativity_desc),
                ]),
            rel_path_doc.relativity_syntax_element_description(self.relativity_arg_path,
                                                               PARSE_FILE_REF_CONFIGURATION.accepted_options),
        ]

    def see_also(self) -> list:
        concepts = rel_path_doc.see_also_concepts(PARSE_FILE_REF_CONFIGURATION.accepted_options)
        return [concept.cross_reference_target() for concept in concepts]


class CmdAndArgsResolverForExecute(CmdAndArgsResolverForExecutableFileBase):
    def __init__(self,
                 executable: ExecutableFile,
                 argument_list: list):
        super().__init__(executable)
        self.argument_list = argument_list

    def _arguments(self, home_and_sds: HomeAndSds) -> list:
        return self.argument_list


class CmdAndArgsResolverForInterpret(CmdAndArgsResolverForExecutableFileBase):
    def __init__(self,
                 executable: ExecutableFile,
                 file_to_interpret: FileRef,
                 argument_list: list):
        super().__init__(executable)
        self.file_to_interpret = file_to_interpret
        self.argument_list = argument_list

    def _arguments(self, home_and_sds: HomeAndSds) -> list:
        return [str(self.file_to_interpret.file_path_pre_or_post_sds(home_and_sds))] + self.argument_list


class CmdAndArgsResolverForSource(CmdAndArgsResolverForExecutableFileBase):
    def __init__(self,
                 executable: ExecutableFile,
                 source: str):
        super().__init__(executable)
        self.source = source

    def _arguments(self, home_and_sds: HomeAndSds) -> list:
        return [self.source]


class SetupParser(spe_parts.ValidationAndSubProcessExecutionSetupParser):
    def apply(self, source: SingleInstructionParserSource) -> spe_parts.ValidationAndSubProcessExecutionSetup:
        tokens = TokenStream(source.instruction_argument)
        (exe_file, arg_tokens) = parse_executable_file.parse(tokens)
        (validator, cmd_and_args_resolver) = self._validator__cmd_and_args_resolver(exe_file, arg_tokens)
        return spe_parts.ValidationAndSubProcessExecutionSetup(validator, cmd_and_args_resolver, False)

    def _validator__cmd_and_args_resolver(self,
                                          exe_file: ExecutableFile,
                                          arg_tokens: TokenStream):
        if arg_tokens.is_null:
            return self._execute(exe_file, '')
        if arg_tokens.head == INTERPRET_OPTION:
            return self._interpret(exe_file, arg_tokens.tail_source_or_empty_string)
        if arg_tokens.head == SOURCE_OPTION:
            return self._source(exe_file, arg_tokens.tail_source)
        if arg_tokens.head == OPTIONS_SEPARATOR_ARGUMENT:
            return self._execute(exe_file, arg_tokens.tail.source)
        return self._execute(exe_file, arg_tokens.source)

    @staticmethod
    def _execute(exe_file: ExecutableFile,
                 remaining_arguments_str: str):
        cmd_resolver = CmdAndArgsResolverForExecute(exe_file, shlex.split(remaining_arguments_str))
        return exe_file.validator, cmd_resolver

    @staticmethod
    def _interpret(exe_file: ExecutableFile,
                   remaining_arguments_str: str):
        remaining_arguments = shlex.split(remaining_arguments_str)
        (file_to_interpret, remaining_arguments) = parse_file_ref.parse_file_ref__list(remaining_arguments)
        file_to_interpret_check = FileRefCheck(file_to_interpret,
                                               file_properties.must_exist_as(file_properties.FileType.REGULAR))
        validator = AndValidator((exe_file.validator,
                                  FileRefCheckValidator(file_to_interpret_check)))
        cmd_resolver = CmdAndArgsResolverForInterpret(exe_file, file_to_interpret, remaining_arguments)
        return validator, cmd_resolver

    @staticmethod
    def _source(exe_file: ExecutableFile,
                remaining_arguments_str: str):
        if not remaining_arguments_str:
            msg = 'Missing {SOURCE} argument for option {option}'.format(SOURCE=_SOURCE_SYNTAX_ELEMENT_NAME,
                                                                         option=SOURCE_OPTION)
            raise SingleInstructionInvalidArgumentException(msg)
        cmd_resolver = CmdAndArgsResolverForSource(exe_file, remaining_arguments_str)
        return exe_file.validator, cmd_resolver
