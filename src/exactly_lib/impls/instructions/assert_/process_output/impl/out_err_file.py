from typing import Sequence

from exactly_lib.common.report_rendering.description_tree import rendering__node_wo_data
from exactly_lib.definitions.test_case import file_check_properties
from exactly_lib.impls.instructions.assert_.utils.file_contents import actual_files
from exactly_lib.impls.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFileConstructor, \
    ComparisonActualFile
from exactly_lib.impls.instructions.assert_.utils.file_contents.parse_instruction import ComparisonActualFileParser
from exactly_lib.impls.instructions.utils.logic_type_resolving_helper import resolving_helper_for_instruction_env
from exactly_lib.impls.program_execution.file_transformation_utils import \
    make_transformed_file_from_output_in_instruction_tmp_dir
from exactly_lib.impls.text_render import header_rendering
from exactly_lib.impls.types.program.parse import parse_program
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import instruction_environment as i
from exactly_lib.type_val_deps.dep_variants.sdv import sdv_validation
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.resolving_helper import resolving_helper__of_full_env
from exactly_lib.type_val_deps.dep_variants.sdv.sdv_validation import SdvValidator
from exactly_lib.type_val_deps.types.path import path_ddvs, path_sdvs
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.util.process_execution import process_output_files
from exactly_lib.util.render.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock
from . import texts
from .. import defs


class Parser(ComparisonActualFileParser):
    _PROGRAM_PARSER = parse_program.program_parser()

    def __init__(self, checked_file: process_output_files.ProcOutputFile):
        super().__init__()
        self._checked_file = checked_file
        self._checked_file_name = process_output_files.PROC_OUTPUT_FILE_NAMES[checked_file]
        self._default = self._default(checked_file)

    def parse_from_token_parser(self, parser: TokenParser) -> ComparisonActualFileConstructor:
        return parser.consume_and_handle_optional_option(self._default,
                                                         self._parse_program,
                                                         defs.OUTPUT_FROM_PROGRAM_OPTION_NAME)

    def _parse_program(self, parser: TokenParser) -> ComparisonActualFileConstructor:
        program = self._PROGRAM_PARSER.parse_from_token_parser(parser)
        return _ComparisonActualFileConstructorForProgram(self._checked_file, program)

    @staticmethod
    def _default(checked_file: process_output_files.ProcOutputFile) -> ComparisonActualFileConstructor:
        return actual_files.ConstructorForPath(
            path_sdvs.of_rel_option(
                RelOptionType.REL_RESULT,
                path_ddvs.constant_path_part(process_output_files.PROC_OUTPUT_FILE_NAMES[checked_file])
            ),
            texts.target_name_of_proc_output_file_from_act_phase(checked_file),
            False,
        )


class _ComparisonActualFileConstructorForProgram(ComparisonActualFileConstructor):
    def __init__(self,
                 checked_output: process_output_files.ProcOutputFile,
                 program: ProgramSdv,
                 ):
        self._checked_output = checked_output
        self._program = program

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._program.references

    @property
    def validator(self) -> SdvValidator:
        return sdv_validation.SdvValidatorFromDdvValidator(
            lambda symbols: self._program.resolve(symbols).validator
        )

    def construct(self,
                  environment: i.InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices) -> ComparisonActualFile:
        program = resolving_helper_for_instruction_env(os_services, environment).resolve_program(self._program)
        result = make_transformed_file_from_output_in_instruction_tmp_dir(environment,
                                                                          os_services,
                                                                          self._checked_output,
                                                                          program)
        file_with_transformed_contents = path_sdvs.constant(
            path_ddvs.absolute_path(result.path_of_file_with_transformed_contents)
        )

        path_with_transformed_contents = (
            file_with_transformed_contents.resolve(environment.symbols)
                .value_of_any_dependency__d(environment.tcds)
        )

        return ComparisonActualFile(
            path_with_transformed_contents,
            False
        )

    def failure_message_header(self, environment: FullResolvingEnvironment) -> Renderer[MajorBlock]:
        resolver = resolving_helper__of_full_env(environment)
        program = resolver.resolve_program(self._program)

        return header_rendering.HeaderValueRenderer.of_unexpected_attr_of_obj(
            file_check_properties.CONTENTS,
            texts.target_name_of_proc_output_file_from_program(self._checked_output),
            rendering__node_wo_data.NodeAsMinorBlocksRenderer(program.structure()),
        )
