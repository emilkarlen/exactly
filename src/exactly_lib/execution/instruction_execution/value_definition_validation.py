from exactly_lib.execution.instruction_execution.single_instruction_executor import \
    PartialInstructionControlledFailureInfo, PartialControlledFailureEnum
from exactly_lib.util import error_message_format
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.value_definition import value_structure as vs
from exactly_lib.value_definition.value_structure import ValueContainer


def validate_pre_sds(value_usage: vs.ValueUsage2,
                     symbol_table: SymbolTable) -> PartialInstructionControlledFailureInfo:
    if isinstance(value_usage, vs.ValueReference2):
        assert isinstance(value_usage, vs.ValueReference2)
        if not symbol_table.contains(value_usage.name):
            return PartialInstructionControlledFailureInfo(
                PartialControlledFailureEnum.VALIDATION,
                'Referenced definition `{}\' is undefined.'.format(value_usage.name))
        else:
            err_msg = _validate_reference(value_usage, symbol_table)
            if err_msg is not None:
                return PartialInstructionControlledFailureInfo(PartialControlledFailureEnum.VALIDATION, err_msg)
        return None
    elif isinstance(value_usage, vs.ValueDefinition2):
        assert isinstance(value_usage, vs.ValueDefinition2)
        if symbol_table.contains(value_usage.name):
            already_defined_value_container = symbol_table.lookup(value_usage.name)
            assert isinstance(already_defined_value_container, ValueContainer), 'Value in SymTbl must be ValueContainer'
            return PartialInstructionControlledFailureInfo(
                PartialControlledFailureEnum.VALIDATION,
                'Name `{}\' has already been defined:\n\n{}'.format(
                    value_usage.name,
                    error_message_format.source_line(
                        already_defined_value_container.source)))
        else:
            for referenced_value in value_usage.references:
                failure_info = validate_pre_sds(referenced_value, symbol_table)
                if failure_info is not None:
                    return failure_info
            symbol_table.add(value_usage.symbol_table_entry)
            return None
    else:
        raise TypeError('Unknown variant of {}: {}'.format(str(vs.ValueUsage2),
                                                           str(value_usage)))


def _validate_reference(value_usage: vs.ValueReference2,
                        value_definitions: SymbolTable) -> str:
    referenced_value_container = value_definitions.lookup(value_usage.name)
    assert isinstance(referenced_value_container, ValueContainer), 'Values in SymbolTable must be ValueContainer'
    return value_usage.value_restriction.is_satisfied_by(value_definitions, referenced_value_container.value)
