from exactly_lib.common.instruction_documentation import InvokationVariant
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.setup.utils.instruction_utils import InstructionWithFileRefsBase
from exactly_lib.instructions.utils import file_properties
from exactly_lib.instructions.utils import file_ref
from exactly_lib.instructions.utils.arg_parse import parse_here_doc_or_file_ref
from exactly_lib.instructions.utils.arg_parse.parse_utils import split_arguments_list_string
from exactly_lib.instructions.utils.documentation import documentation_text as dt
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.instructions.utils.file_properties import FileType
from exactly_lib.instructions.utils.file_ref_check import FileRefCheck
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.string import lines_content
from exactly_lib.util.textformat.structure import structures as docs


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str):
        super().__init__(name, {})
        self.path_arg = dt.FILE_ARGUMENT

    def single_line_description(self) -> str:
        return 'Sets the contents of stdin for the act phase program.'

    def main_description_rest(self) -> list:
        return (
            rel_path_doc.default_relativity_for_rel_opt_type(self.path_arg.name,
                                                             parse_here_doc_or_file_ref.CONFIGURATION.default_option) +
            dt.paths_uses_posix_syntax())

    def invokation_variants(self) -> list:
        arguments = [a.Single(a.Multiplicity.OPTIONAL,
                              rel_path_doc.RELATIVITY_ARGUMENT),
                     a.Single(a.Multiplicity.MANDATORY, self.path_arg), ]
        here_doc_arg = a.Single(a.Multiplicity.MANDATORY, dt.HERE_DOCUMENT)
        return [
            InvokationVariant(self._cl_syntax_for_args(arguments),
                              docs.paras('Sets stdin to be the contents of a file.')),
            InvokationVariant(self._cl_syntax_for_args([here_doc_arg]),
                              docs.paras('Sets stdin to be the contents of a "here document".')),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            rel_path_doc.relativity_syntax_element_description(
                self.path_arg,
                parse_here_doc_or_file_ref.CONFIGURATION.accepted_options),
            dt.here_document_syntax_element_description(self.instruction_name(),
                                                        dt.HERE_DOCUMENT),
        ]

    def see_also(self) -> list:
        concepts = rel_path_doc.see_also_concepts(parse_here_doc_or_file_ref.CONFIGURATION.accepted_options)
        return [concept.cross_reference_target() for concept in concepts]


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> SetupPhaseInstruction:
        first_line_arguments = split_arguments_list_string(source.instruction_argument)
        if not first_line_arguments:
            raise SingleInstructionInvalidArgumentException('Missing arguments: no arguments')
        (here_doc_or_file_ref, remaining_arguments) = parse_here_doc_or_file_ref.parse(first_line_arguments, source)
        if remaining_arguments:
            raise SingleInstructionInvalidArgumentException('Superfluous arguments: ' + str(remaining_arguments))
        if here_doc_or_file_ref.is_here_document:
            content = lines_content(here_doc_or_file_ref.here_document)
            return _InstructionForHereDocument(content)
        return _InstructionForFileRef(here_doc_or_file_ref.file_reference)


class _InstructionForHereDocument(SetupPhaseInstruction):
    def __init__(self, contents: str):
        self.contents = contents

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        settings_builder.stdin.contents = self.contents
        return sh.new_sh_success()


class _InstructionForFileRef(InstructionWithFileRefsBase):
    def __init__(self, redirect_file: file_ref.FileRef):
        super().__init__((FileRefCheck(redirect_file,
                                       file_properties.must_exist_as(FileType.REGULAR)),))
        self.redirect_file = redirect_file

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        settings_builder.stdin.file_name = str(self.redirect_file.file_path_pre_or_post_eds(environment.home_and_eds))
        return sh.new_sh_success()
