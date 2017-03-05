from exactly_lib.execution.instruction_execution.single_instruction_executor import \
    PartialInstructionControlledFailureInfo, PartialControlledFailureEnum
from exactly_lib.test_case import value_definition


def validate_pre_sds(value_usage: value_definition.ValueUsage,
                     symbol_table: value_definition.SymbolTable) -> PartialInstructionControlledFailureInfo:
    if isinstance(value_usage, value_definition.ValueReference):
        assert isinstance(value_usage, value_definition.ValueReference)
        if not symbol_table.contains(value_usage.name):
            return PartialInstructionControlledFailureInfo(
                PartialControlledFailureEnum.VALIDATION,
                'Referenced variable `{}\' is undefined.'.format(value_usage.name))
        else:
            return None
    elif isinstance(value_usage, value_definition.ValueDefinition):
        assert isinstance(value_usage, value_definition.ValueDefinition)
        if symbol_table.contains(value_usage.name):
            return PartialInstructionControlledFailureInfo(
                PartialControlledFailureEnum.VALIDATION,
                'Defined variable `{}\' has already been defined.'.format(value_usage.name))
        else:
            symbol_table.add(value_usage)
            return None
    else:
        raise TypeError('Unknown variant of {}: {}'.format(str(value_definition.ValueUsage),
                                                           str(value_usage)))
