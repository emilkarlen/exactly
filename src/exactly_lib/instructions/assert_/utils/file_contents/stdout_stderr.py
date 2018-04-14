from typing import Sequence, Optional, List

from exactly_lib.common.help import syntax_contents_structure
from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.definitions import formatting
from exactly_lib.definitions.entity import concepts, syntax_elements, types
from exactly_lib.instructions.assert_.utils.file_contents import actual_files
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFileConstructor, \
    ComparisonActualFile
from exactly_lib.instructions.assert_.utils.file_contents.parse_instruction import ComparisonActualFileParser
from exactly_lib.instructions.assert_.utils.file_contents.syntax.file_contents_checker import \
    FileContentsCheckerHelp
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.data import file_ref_resolvers
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.program.program_resolver import ProgramResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import WithAssertPhasePurpose
from exactly_lib.test_case.phases.common import InstructionSourceInfo
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.parse import parse_here_doc_or_file_ref
from exactly_lib.test_case_utils.program.execution.store_result_in_instruction_tmp_dir import \
    make_transformed_file_from_output_in_instruction_tmp_dir
from exactly_lib.test_case_utils.program.parse import parse_program
from exactly_lib.type_system.data import file_refs
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.process_execution import process_output_files

OUTPUT_FROM_PROGRAM_OPTION_NAME = a.OptionName(long_name='from')


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase,
                                  WithAssertPhasePurpose):
    def __init__(self, name: str,
                 name_of_checked_file: str):
        self.file_arg = a.Named(parse_here_doc_or_file_ref.CONFIGURATION.argument_syntax_name)
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
        return self._format('Tests the contents of {checked_file} from the {action_to_check}, or from a {program_type}')

    def main_description_rest(self) -> list:
        return []

    def invokation_variants(self) -> list:
        return self._help_parts.invokation_variants__stdout_err(OUTPUT_FROM_PROGRAM_OPTION_NAME)

    def syntax_element_descriptions(self) -> list:
        return (self._help_parts.syntax_element_descriptions_at_top() +
                self._help_parts.syntax_element_descriptions_at_bottom())

    def see_also_targets(self) -> list:
        return self._help_parts.see_also_targets__stdout_err()

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
        self._default = actual_files.ComparisonActualFileConstructorForConstant(
            ActComparisonActualFileForStdFile(checked_file))

    def parse_from_token_parser(self, parser: TokenParser) -> ComparisonActualFileConstructor:
        def _parse_program(_parser: TokenParser) -> ComparisonActualFileConstructor:
            program = parse_program.parse_program(_parser)
            return _ComparisonActualFileConstructorForProgram(self._checked_file, program)

        return parser.consume_and_handle_optional_option(self._default,
                                                         _parse_program,
                                                         OUTPUT_FROM_PROGRAM_OPTION_NAME)


class ActComparisonActualFileForStdFile(actual_files.ComparisonActualFileConstantWithReferences):
    def __init__(self, checked_file: process_output_files.ProcOutputFile):
        super().__init__(())
        self.checked_file = checked_file
        self.checked_file_name = process_output_files.PROC_OUTPUT_FILE_NAMES[self.checked_file]

    def object_name(self) -> str:
        return process_output_files.PROC_OUTPUT_FILE_NAMES[self.checked_file]

    def file_check_failure(self, environment: i.InstructionEnvironmentForPostSdsStep) -> Optional[str]:
        return None

    def file_ref_resolver(self) -> FileRefResolver:
        return file_ref_resolvers.of_rel_option(RelOptionType.REL_RESULT,
                                                file_refs.constant_path_part(self.checked_file_name))


class _ComparisonActualFileConstructorForProgram(ComparisonActualFileConstructor):
    def __init__(self,
                 checked_output: process_output_files.ProcOutputFile,
                 program: ProgramResolver):
        self._checked_output = checked_output
        self._program = program

    def construct(self,
                  source_info: InstructionSourceInfo,
                  environment: i.InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices) -> ComparisonActualFile:
        program = self._program.resolve(environment.symbols).value_of_any_dependency(environment.home_and_sds)
        result = make_transformed_file_from_output_in_instruction_tmp_dir(environment,
                                                                          os_services.executable_factory__detect_ex(),
                                                                          source_info,
                                                                          self._checked_output,
                                                                          program)
        return actual_files.ComparisonActualFileForProgramOutput(result.path_of_file_with_transformed_contents)

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._program.validator

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._program.references
