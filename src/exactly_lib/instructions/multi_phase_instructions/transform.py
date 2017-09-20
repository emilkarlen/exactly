from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.instructions.multi_phase_instructions.utils import instruction_embryo as embryo
from exactly_lib.named_element.symbol.path_resolver import FileRefResolver
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths
from exactly_lib.test_case_utils.parse.parse_file_ref import parse_file_ref_from_parse_source
from exactly_lib.test_case_utils.parse.rel_opts_configuration import argument_configuration_for_file_creation


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str):
        super().__init__(name, {})

    def single_line_description(self) -> str:
        return 'Transforms a file'

    def main_description_rest(self) -> list:
        return []

    def invokation_variants(self) -> list:
        return []

    def syntax_element_descriptions(self) -> list:
        return []

    def _see_also_cross_refs(self) -> list:
        return []


class TheInstructionEmbryo(embryo.InstructionEmbryo):
    def __init__(self,
                 src_file: FileRefResolver,
                 dst_file: FileRefResolver):
        self._src_file = src_file
        self._dst_file = dst_file

    @property
    def symbol_usages(self) -> list:
        return []

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             logging_paths: PhaseLoggingPaths,
             os_services: OsServices):
        raise NotImplementedError('todo')


class EmbryoParser(embryo.InstructionEmbryoParser):
    def parse(self, source: ParseSource) -> TheInstructionEmbryo:
        src_file = parse_file_ref_from_parse_source(source, REL_OPT_ARG_CONF)
        dst_file = parse_file_ref_from_parse_source(source, REL_OPT_ARG_CONF)
        return TheInstructionEmbryo(src_file, dst_file)


_PATH_ARGUMENT = instruction_arguments.PATH_ARGUMENT

REL_OPT_ARG_CONF = argument_configuration_for_file_creation(_PATH_ARGUMENT.name)
