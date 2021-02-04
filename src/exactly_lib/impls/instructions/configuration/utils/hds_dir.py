import pathlib
from typing import Sequence

from exactly_lib.common.help.abs_or_rel_path import abs_or_rel_path_of_existing
from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, InvokationVariant
from exactly_lib.common.report_rendering import text_docs
from exactly_lib.definitions import formatting, instruction_arguments
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.entity.conf_params import ConfigurationParameterInfo
from exactly_lib.impls.instructions.configuration.utils.single_arg_utils import single_eq_invokation_variants, \
    extract_single_eq_argument_string
from exactly_lib.impls.text_render import header_rendering
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.misc_utils import split_arguments_list_string
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.tcfs.path_relativity import RelHdsOptionType
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.result import svh
from exactly_lib.util.render import combinators as rend_comb

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

    def invokation_variants(self) -> Sequence[InvokationVariant]:
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
        argument = extract_single_eq_argument_string(_DIR_ARG.name, rest_of_line)
        path_arguments = split_arguments_list_string(argument)
        if len(path_arguments) > 1:
            raise SingleInstructionInvalidArgumentException('Too many arguments: ' + argument)

        try:
            path_argument = pathlib.Path(pathlib.PurePosixPath(path_arguments[0]))
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

    def main(self, configuration_builder: ConfigurationBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        new_path = self._new_path()
        if not new_path.exists():
            return _validation_error('Directory does not exist', new_path)
        if not new_path.is_dir():
            return _validation_error('Not a directory', new_path)
        configuration_builder.set_hds_dir(self.dir_to_set, new_path.resolve())
        return svh.new_svh_success()

    def _new_path(self) -> pathlib.Path:
        if self.argument.is_absolute():
            return self.argument
        return self.relativity_root / self.argument


def _validation_error(header: str, path: pathlib.Path) -> svh.SuccessOrValidationErrorOrHardError:
    return svh.new_svh_validation_error(
        rend_comb.SingletonSequenceR(
            header_rendering.HeaderValueRenderer(
                header,
                text_docs.minor_blocks_of_string_lines([str(path)])
            )
        )
    )
