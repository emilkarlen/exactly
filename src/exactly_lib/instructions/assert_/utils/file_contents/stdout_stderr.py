from typing import Sequence, List

from exactly_lib.common.help import syntax_contents_structure
from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.definitions import actual_file_attributes
from exactly_lib.definitions import formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import concepts, syntax_elements, types
from exactly_lib.instructions.assert_.utils.file_contents import actual_files
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFileConstructor, \
    ActualFilePropertyDescriptorConstructorForComparisonFile, ComparisonActualFile
from exactly_lib.instructions.assert_.utils.file_contents.parse_instruction import ComparisonActualFileParser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.data import path_sdvs
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import WithAssertPhasePurpose
from exactly_lib.test_case.phases.common import InstructionSourceInfo
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.err_msg2 import file_or_dir_contents_headers
from exactly_lib.test_case_utils.file_contents_check_syntax import \
    FileContentsCheckerHelp
from exactly_lib.test_case_utils.parse import parse_here_doc_or_path
from exactly_lib.test_case_utils.program.execution.store_result_in_instruction_tmp_dir import \
    make_transformed_file_from_output_in_instruction_tmp_dir
from exactly_lib.test_case_utils.program.parse import parse_program
from exactly_lib.type_system.data import paths
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.process_execution import process_output_files
from exactly_lib.util.render.renderer import Renderer
from exactly_lib.util.simple_textstruct.rendering import blocks, line_objects
from exactly_lib.util.simple_textstruct.structure import MajorBlock
from exactly_lib.util.textformat.structure.core import ParagraphItem

_SINGLE_LINE_DESCRIPTION = 'Tests the contents of {checked_file} from the {action_to_check}, or from a {program_type}'

OUTPUT_FROM_PROGRAM_OPTION_NAME = a.OptionName(long_name='from')


class TheInstructionDocumentation(InstructionDocumentationWithTextParserBase,
                                  WithAssertPhasePurpose):
    def __init__(self, name: str,
                 name_of_checked_file: str):
        self.file_arg = a.Named(parse_here_doc_or_path.CONFIGURATION.argument_syntax_name)
        self._help_parts = FileContentsCheckerHelp(name,
                                                   name_of_checked_file,
                                                   [])

        super().__init__(name, {
            'checked_file': name_of_checked_file,
            'action_to_check': formatting.concept_(concepts.ACTION_TO_CHECK_CONCEPT_INFO),
            'program_type': formatting.entity_(types.PROGRAM_TYPE_INFO),
            'FILE_ARG': self.file_arg.name,
        })
        self.checked_file = name_of_checked_file

    def single_line_description(self) -> str:
        return self._tp.format(_SINGLE_LINE_DESCRIPTION)

    def main_description_rest(self) -> List[ParagraphItem]:
        return []

    def invokation_variants(self) -> List[InvokationVariant]:
        return self._help_parts.invokation_variants__stdout_err(OUTPUT_FROM_PROGRAM_OPTION_NAME)

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return self._help_parts.see_also_targets__std_out_err()

    def _specific_invocation_invokation_variants(self) -> List[syntax_contents_structure.InvokationVariant]:
        return [
            syntax_contents_structure.invokation_variant_from_args([
                a.Single(a.Multiplicity.MANDATORY, a.Option(OUTPUT_FROM_PROGRAM_OPTION_NAME)),
                a.Single(a.Multiplicity.MANDATORY, syntax_elements.PROGRAM_SYNTAX_ELEMENT.argument),
            ]),
        ]


class Parser(ComparisonActualFileParser):
    def __init__(self, checked_file: process_output_files.ProcOutputFile):
        self._checked_file = checked_file
        self._checked_file_name = process_output_files.PROC_OUTPUT_FILE_NAMES[checked_file]
        self._default = actual_files.ConstructorForPath(
            path_sdvs.of_rel_option(RelOptionType.REL_RESULT,
                                    paths.constant_path_part(self._checked_file_name)),
            file_or_dir_contents_headers.target_name_of_proc_output_file_from_act_phase(checked_file),
            False,
        )

    def parse_from_token_parser(self, parser: TokenParser) -> ComparisonActualFileConstructor:
        def _parse_program(_parser: TokenParser) -> ComparisonActualFileConstructor:
            program = parse_program.parse_program(_parser)
            return _ComparisonActualFileConstructorForProgram(self._checked_file, program)

        return parser.consume_and_handle_optional_option(self._default,
                                                         _parse_program,
                                                         OUTPUT_FROM_PROGRAM_OPTION_NAME)


class _ComparisonActualFileConstructorForProgram(ComparisonActualFileConstructor):
    def __init__(self,
                 checked_output: process_output_files.ProcOutputFile,
                 program: ProgramSdv):
        self._checked_output = checked_output
        self._program = program

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._program.references

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._program.validator

    def construct(self,
                  source_info: InstructionSourceInfo,
                  environment: i.InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices) -> ComparisonActualFile:
        program = self._program.resolve(environment.symbols).value_of_any_dependency(environment.tcds)
        result = make_transformed_file_from_output_in_instruction_tmp_dir(environment,
                                                                          os_services.executable_factory__detect_ex(),
                                                                          source_info,
                                                                          self._checked_output,
                                                                          program)
        file_with_transformed_contents = path_sdvs.constant(
            paths.absolute_path(result.path_of_file_with_transformed_contents)
        )

        path_with_transformed_contents = (
            file_with_transformed_contents.resolve(environment.symbols)
                .value_of_any_dependency__d(environment.tcds)
        )

        return ComparisonActualFile(
            path_with_transformed_contents,
            ActualFilePropertyDescriptorConstructorForComparisonFile(
                path_with_transformed_contents.describer,
                actual_file_attributes.OUTPUT_FROM_PROGRAM_OBJECT_NAME),
            False
        )

    def failure_message_header(self, environment: PathResolvingEnvironmentPreOrPostSds) -> Renderer[MajorBlock]:
        header = file_or_dir_contents_headers.unexpected(
            file_or_dir_contents_headers.target_name_of_proc_output_file_from_program(self._checked_output)
        )

        return blocks.MajorBlockOfSingleLineObject(
            line_objects.StringLineObject(header)
        )
