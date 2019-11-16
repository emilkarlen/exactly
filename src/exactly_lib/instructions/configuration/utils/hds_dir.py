import pathlib

from exactly_lib.common.help.abs_or_rel_path import abs_or_rel_path_of_existing
from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.common.report_rendering import text_docs
from exactly_lib.definitions import formatting, instruction_arguments
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.entity.conf_params import ConfigurationParameterInfo
from exactly_lib.instructions.configuration.utils.single_arg_utils import single_eq_invokation_variants, \
    extract_single_eq_argument_string
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.result import sh
from exactly_lib.test_case_file_structure.path_relativity import RelHdsOptionType
from exactly_lib.util import strings

_RELATIVITY_ROOT = 'location of the current source file - the file that contains the instruction'


class DirConfParamInstructionDocumentationBase(InstructionDocumentationWithTextParserBase):
    def __init__(self,
                 name: str,
                 conf_param: ConfigurationParameterInfo):
        self.conf_param = conf_param
        super().__init__(name, {
            'conf_param': formatting.conf_param_(conf_param),
            'DIR': _DIR_ARG.name,
        })

    def single_line_description(self) -> str:
        return self._tp.format('Sets the {conf_param} directory')

    def invokation_variants(self) -> list:
        return single_eq_invokation_variants(_DIR_ARG)

    def syntax_element_descriptions(self) -> list:
        return [
            SyntaxElementDescription(_DIR_ARG.name,
                                     abs_or_rel_path_of_existing('directory',
                                                                 _DIR_ARG.name,
                                                                 _RELATIVITY_ROOT)),
        ]

    def see_also_targets(self) -> list:
        return cross_reference_id_list([
            self.conf_param,
            concepts.HDS_CONCEPT_INFO,
        ])


_DIR_ARG = instruction_arguments.DIR_WITHOUT_RELATIVITY_OPTIONS_ARGUMENT


class Parser(InstructionParser):
    def __init__(self, dir_to_set: RelHdsOptionType):
        self.dir_to_set = dir_to_set

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> ConfigurationPhaseInstruction:
        rest_of_line = source.remaining_part_of_current_line
        source.consume_current_line()
        path_argument_str = extract_single_eq_argument_string(rest_of_line)

        try:
            path_argument = pathlib.Path(pathlib.PurePosixPath(path_argument_str))
        except ValueError as ex:
            raise SingleInstructionInvalidArgumentException('Invalid path syntax:\n' + str(ex))

        return _Instruction(self.dir_to_set,
                            fs_location_info.current_source_file.abs_path_of_dir_containing_last_file_base_name,
                            path_argument)


class _Instruction(ConfigurationPhaseInstruction):
    def __init__(self,
                 dir_to_set: RelHdsOptionType,
                 relativity_root: pathlib.Path,
                 argument: pathlib.Path):
        self.dir_to_set = dir_to_set
        self.relativity_root = relativity_root
        self.argument = argument

    def main(self, configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        new_path = self._new_path()
        if not new_path.exists():
            return sh.new_sh_hard_error(
                text_docs.single_line(
                    strings.FormatPositional(
                        'Directory does not exist: {}',
                        new_path)
                )
            )
        if not new_path.is_dir():
            return sh.new_sh_hard_error(
                text_docs.single_line(
                    strings.FormatPositional(
                        'Not a directory: {}',
                        new_path)
                )
            )
        configuration_builder.set_hds_dir(self.dir_to_set, new_path.resolve())
        return sh.new_sh_success()

    def _new_path(self) -> pathlib.Path:
        if self.argument.is_absolute():
            return self.argument
        return self.relativity_root / self.argument
