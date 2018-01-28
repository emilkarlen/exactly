from exactly_lib.execution.instruction_execution.single_instruction_executor import \
    PartialInstructionControlledFailureInfo, PartialControlledFailureEnum
from exactly_lib.symbol import symbol_usage as su
from exactly_lib.symbol.err_msg import restriction_failure_renderer
from exactly_lib.symbol.resolver_structure import SymbolContainer
from exactly_lib.util import error_message_format
from exactly_lib.util.symbol_table import SymbolTable


def validate_symbol_usages(symbol_usages: list,
                           symbols: SymbolTable) -> PartialInstructionControlledFailureInfo:
    for symbol_usage in symbol_usages:
        result = validate_symbol_usage(symbol_usage, symbols)
        if result is not None:
            return result
    return None


def validate_symbol_usage(usage: su.SymbolUsage,
                          symbol_table: SymbolTable) -> PartialInstructionControlledFailureInfo:
    if isinstance(usage, su.SymbolReference):
        return _validate_symbol_reference(symbol_table, usage)
    elif isinstance(usage, su.SymbolDefinition):
        return _validate_symbol_definition(symbol_table, usage)
    else:
        raise TypeError('Unknown variant of {}: {}'.format(str(su.SymbolUsage),
                                                           str(usage)))


def _validate_symbol_definition(symbol_table: SymbolTable,
                                definition: su.SymbolDefinition,
                                ) -> PartialInstructionControlledFailureInfo:
    if symbol_table.contains(definition.name):
        already_defined_resolver_container = symbol_table.lookup(definition.name)
        assert isinstance(already_defined_resolver_container, SymbolContainer), \
            'Value in SymTbl must be ResolverContainer'
        return PartialInstructionControlledFailureInfo(
            PartialControlledFailureEnum.VALIDATION,
            'Symbol `{}\' has already been defined:\n\n{}'.format(
                definition.name,
                error_message_format.source_lines(
                    already_defined_resolver_container.definition_source)))
    else:
        for referenced_value in definition.references:
            failure_info = validate_symbol_usage(referenced_value, symbol_table)
            if failure_info is not None:
                return failure_info
        symbol_table.add(definition.symbol_table_entry)
        return None


def _validate_symbol_reference(symbol_table: SymbolTable,
                               reference: su.SymbolReference,
                               ) -> PartialInstructionControlledFailureInfo:
    assert isinstance(reference, su.SymbolReference)
    if not symbol_table.contains(reference.name):
        error_message = _undefined_symbol_error_message(reference)
        return PartialInstructionControlledFailureInfo(
            PartialControlledFailureEnum.VALIDATION,
            error_message)
    else:
        err_msg = _validate_reference(reference, symbol_table)
        if err_msg is not None:
            return PartialInstructionControlledFailureInfo(PartialControlledFailureEnum.VALIDATION, err_msg)
    return None


def _undefined_symbol_error_message(reference: su.SymbolReference) -> str:
    from exactly_lib.help_texts.formatting import InstructionName
    from exactly_lib.help_texts.test_case.instructions.instruction_names import SYMBOL_DEFINITION_INSTRUCTION_NAME
    def_name_emphasised = InstructionName(SYMBOL_DEFINITION_INSTRUCTION_NAME).emphasis
    lines = [
        'Symbol `{}\' is undefined.'.format(reference.name),
        '',
        'Define a symbol using the {} instruction.'.format(def_name_emphasised),
    ]
    return '\n'.join(lines)


def _validate_reference(symbol_reference: su.SymbolReference,
                        symbols: SymbolTable) -> str:
    referenced_resolver_container = symbols.lookup(symbol_reference.name)
    assert isinstance(referenced_resolver_container, SymbolContainer), \
        'Values in SymbolTable must be ResolverContainer'
    result = symbol_reference.restrictions.is_satisfied_by(symbols, symbol_reference.name,
                                                           referenced_resolver_container)
    if result is None:
        return None
    return restriction_failure_renderer.error_message(symbol_reference.name, symbols, result)
