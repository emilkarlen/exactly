from exactly_lib.execution.instruction_execution.single_instruction_executor import \
    PartialInstructionControlledFailureInfo, PartialControlledFailureEnum
from exactly_lib.symbol import value_structure as vs
from exactly_lib.symbol.value_structure import ValueContainer
from exactly_lib.util import error_message_format
from exactly_lib.util.symbol_table import SymbolTable


def validate_symbol_usages(symbol_usages: list,
                           symbols: SymbolTable) -> PartialInstructionControlledFailureInfo:
    for symbol_usage in symbol_usages:
        result = validate_symbol_usage(symbol_usage, symbols)
        if result is not None:
            return result
    return None


def validate_symbol_usage(usage: vs.SymbolUsage,
                          symbol_table: SymbolTable) -> PartialInstructionControlledFailureInfo:
    if isinstance(usage, vs.SymbolReference):
        assert isinstance(usage, vs.SymbolReference)
        if not symbol_table.contains(usage.name):
            return PartialInstructionControlledFailureInfo(
                PartialControlledFailureEnum.VALIDATION,
                'Referenced symbol `{}\' is undefined.'.format(usage.name))
        else:
            err_msg = _validate_reference(usage, symbol_table)
            if err_msg is not None:
                return PartialInstructionControlledFailureInfo(PartialControlledFailureEnum.VALIDATION, err_msg)
        return None
    elif isinstance(usage, vs.SymbolDefinition):
        assert isinstance(usage, vs.SymbolDefinition)
        if symbol_table.contains(usage.name):
            already_defined_value_container = symbol_table.lookup(usage.name)
            assert isinstance(already_defined_value_container, ValueContainer), 'Value in SymTbl must be ValueContainer'
            return PartialInstructionControlledFailureInfo(
                PartialControlledFailureEnum.VALIDATION,
                'Symbol `{}\' has already been defined:\n\n{}'.format(
                    usage.name,
                    error_message_format.source_line(
                        already_defined_value_container.definition_source)))
        else:
            for referenced_value in usage.references:
                failure_info = validate_symbol_usage(referenced_value, symbol_table)
                if failure_info is not None:
                    return failure_info
            symbol_table.add(usage.symbol_table_entry)
            return None
    else:
        raise TypeError('Unknown variant of {}: {}'.format(str(vs.SymbolUsage),
                                                           str(usage)))


def _validate_reference(symbol_usage: vs.SymbolReference,
                        symbols: SymbolTable) -> str:
    referenced_value_container = symbols.lookup(symbol_usage.name)
    assert isinstance(referenced_value_container, ValueContainer), 'Values in SymbolTable must be ValueContainer'
    return symbol_usage.value_restriction.is_satisfied_by(symbols, symbol_usage.name, referenced_value_container)
