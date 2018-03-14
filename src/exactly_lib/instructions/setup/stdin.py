from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.syntax_contents_structure import invokation_variant_from_args
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering.path_syntax import the_path_of
from exactly_lib.instructions.setup.utils.instruction_utils import InstructionWithFileRefsBase
from exactly_lib.instructions.utils.documentation.string_or_here_doc_or_file import StringOrHereDocOrFile
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.element_parsers.token_stream_parser import from_parse_source, \
    TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.file_ref_check import FileRefCheck
from exactly_lib.test_case_utils.parse import parse_here_doc_or_file_ref
from exactly_lib.test_case_utils.parse.parse_here_doc_or_file_ref import SourceType
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure import structures as docs


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


RELATIVITY_OPTIONS_CONFIGURATION = parse_here_doc_or_file_ref.CONFIGURATION


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str):
        super().__init__(name, {})
        self.path_arg = instruction_arguments.PATH_ARGUMENT
        self.string_or_here_doc_or_file_arg = StringOrHereDocOrFile(
            self.path_arg.name,
            instruction_arguments.RELATIVITY_ARGUMENT.name,
            RELATIVITY_OPTIONS_CONFIGURATION,
            the_path_of('the file that will be the contents of stdin.')
        )

    def single_line_description(self) -> str:
        return 'Sets the contents of stdin for the act phase program'

    def invokation_variants(self) -> list:
        args = [a.Single(a.Multiplicity.MANDATORY, a.Constant(instruction_arguments.ASSIGNMENT_OPERATOR)),
                self.string_or_here_doc_or_file_arg.argument_usage(a.Multiplicity.MANDATORY),
                ]
        return [
            invokation_variant_from_args(args,
                                         docs.paras(
                                             'Sets stdin to be the contents of a string, "here document" or file')),
        ]

    def syntax_element_descriptions(self) -> list:
        return self.string_or_here_doc_or_file_arg.syntax_element_descriptions()

    def see_also_targets(self) -> list:
        return self.string_or_here_doc_or_file_arg.see_also_targets()


class Parser(InstructionParser):
    def parse(self, source: ParseSource) -> SetupPhaseInstruction:
        with from_parse_source(source, consume_last_line_if_is_at_eof_after_parse=True) as token_parser:
            assert isinstance(token_parser, TokenParser), 'Must have a TokenParser'  # Type info for IDE

            token_parser.consume_mandatory_constant_string_that_must_be_unquoted_and_equal(
                [instruction_arguments.ASSIGNMENT_OPERATOR],
                lambda x: x
            )
            string_or_file_ref = parse_here_doc_or_file_ref.parse_from_token_parser(token_parser,
                                                                                    RELATIVITY_OPTIONS_CONFIGURATION)
            if string_or_file_ref.source_type is not SourceType.HERE_DOC:
                token_parser.report_superfluous_arguments_if_not_at_eol()
                token_parser.consume_current_line_as_plain_string()

            if string_or_file_ref.is_file_ref:
                return _InstructionForFileRef(string_or_file_ref.file_reference_resolver)
            else:
                return _InstructionForStringResolver(string_or_file_ref.string_resolver)


class _InstructionForStringResolver(SetupPhaseInstruction):
    def __init__(self, contents: StringResolver):
        self.contents = contents

    def symbol_usages(self) -> list:
        return self.contents.references

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        contents = self.contents.resolve_value_of_any_dependency(environment.path_resolving_environment_pre_or_post_sds)
        settings_builder.stdin.contents = contents
        return sh.new_sh_success()


class _InstructionForFileRef(InstructionWithFileRefsBase):
    def __init__(self, redirect_file: FileRefResolver):
        super().__init__((FileRefCheck(redirect_file,
                                       file_properties.must_exist_as(FileType.REGULAR)),))
        self.redirect_file = redirect_file

    def symbol_usages(self) -> list:
        return self.redirect_file.references

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        env = environment.path_resolving_environment_pre_or_post_sds
        file_ref = self.redirect_file.resolve(environment.symbols)
        settings_builder.stdin.file_name = file_ref.value_of_any_dependency(env.home_and_sds)
        return sh.new_sh_success()
