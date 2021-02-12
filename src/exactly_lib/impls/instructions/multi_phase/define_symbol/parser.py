from typing import Tuple, Sequence

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.test_case.instructions import define_symbol as syntax
from exactly_lib.impls.instructions.multi_phase.utils import instruction_embryo as embryo
from exactly_lib.impls.instructions.multi_phase.utils.instruction_part_utils import PartsParserFromEmbryoParser, \
    MainStepResultTranslatorForErrorMessageStringResultAsHardError
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, from_parse_source
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.symbol import symbol_syntax
from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolUsage, SymbolDefinition, \
    SymbolDependentValue
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.util.line_source import LineSequence
from exactly_lib.util.symbol_table import SymbolTable
from . import type_setup


class TheInstructionEmbryo(embryo.PhaseAgnosticInstructionEmbryo[None]):
    def __init__(self, symbol: SymbolDefinition):
        self.symbol = symbol

    @property
    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return [self.symbol]

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices,
             ):
        self.custom_main(environment.symbols)

    def custom_main(self, symbols: SymbolTable):
        symbols.put(self.symbol.name,
                    self.symbol.symbol_container)


class EmbryoParser(embryo.InstructionEmbryoParser):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> TheInstructionEmbryo:
        first_line_number = source.current_line_number
        instruction_name_prefix = source.current_line_text[:source.column_index]
        remaining_source_before = source.remaining_source

        with from_parse_source(source,
                               consume_last_line_if_is_at_eol_after_parse=True,
                               consume_last_line_if_is_at_eof_after_parse=True) as token_parser:
            symbol_name, value_type, value_sdv = _parse(fs_location_info, token_parser)

        remaining_source_after = source.remaining_source
        num_chars_consumed = len(remaining_source_before) - len(remaining_source_after)
        parsed_str = remaining_source_before[:num_chars_consumed]
        source_lines = LineSequence(first_line_number,
                                    (instruction_name_prefix + parsed_str).splitlines())

        source_info = fs_location_info.current_source_file.source_location_info_for(source_lines)
        sym_def = SymbolDefinition(symbol_name,
                                   SymbolContainer(value_sdv,
                                                   value_type,
                                                   source_info))

        return TheInstructionEmbryo(sym_def)


PARTS_PARSER = PartsParserFromEmbryoParser(EmbryoParser(),
                                           MainStepResultTranslatorForErrorMessageStringResultAsHardError())


def _parse(fs_location_info: FileSystemLocationInfo,
           parser: TokenParser) -> Tuple[str, ValueType, SymbolDependentValue]:
    type_str = parser.consume_mandatory_unquoted_string('SYMBOL-TYPE', True)

    if type_str not in type_setup.TYPE_SETUPS:
        err_msg = 'Invalid type: {}\nExpecting one of {}'.format(type_str, _TYPES_LIST_IN_ERR_MSG)
        raise SingleInstructionInvalidArgumentException(err_msg)

    ts = type_setup.TYPE_SETUPS[type_str]

    name_str = parser.consume_mandatory_unquoted_string(
        syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.singular_name,
        True,
    )

    if not symbol_syntax.is_symbol_name(name_str):
        err_msg = symbol_syntax.invalid_symbol_name_error(name_str)
        raise SingleInstructionInvalidArgumentException(err_msg)

    parser.consume_mandatory_constant_unquoted_string(syntax.ASSIGNMENT_ARGUMENT, True)

    value_sdv = ts.parser.parse(fs_location_info, parser)

    parser.report_superfluous_arguments_if_not_at_eol()

    return name_str, ts.value_type, value_sdv


_TYPES_LIST_IN_ERR_MSG = '|'.join(sorted(type_setup.TYPE_SETUPS.keys()))
