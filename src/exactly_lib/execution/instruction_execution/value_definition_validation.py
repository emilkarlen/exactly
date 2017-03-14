from exactly_lib.execution.instruction_execution.single_instruction_executor import \
    PartialInstructionControlledFailureInfo, PartialControlledFailureEnum
from exactly_lib.test_case.file_ref_relativity import RelOptionType
from exactly_lib.util import error_message_format
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.value_definition import symbol_table_contents as sym_tbl, value_definition_usage
from exactly_lib.value_definition.symbol_table_contents import FileRefValue


def validate_pre_sds(value_usage: value_definition_usage.ValueUsage,
                     symbol_table: SymbolTable) -> PartialInstructionControlledFailureInfo:
    if isinstance(value_usage, value_definition_usage.ValueReference):
        assert isinstance(value_usage, value_definition_usage.ValueReference)
        if not symbol_table.contains(value_usage.name):
            return PartialInstructionControlledFailureInfo(
                PartialControlledFailureEnum.VALIDATION,
                'Referenced definition `{}\' is undefined.'.format(value_usage.name))
        if isinstance(value_usage, value_definition_usage.ValueReferenceOfPath):
            err_msg = _validate_reference_of_path(value_usage, symbol_table)
            if err_msg is not None:
                return PartialInstructionControlledFailureInfo(PartialControlledFailureEnum.VALIDATION, err_msg)
        return None
    elif isinstance(value_usage, value_definition_usage.ValueDefinition):
        assert isinstance(value_usage, value_definition_usage.ValueDefinition)
        if symbol_table.contains(value_usage.name):
            file_ref_value = symbol_table.lookup(value_usage.name)
            assert isinstance(file_ref_value, FileRefValue), 'Currently only type FileRefValue:s are supported'
            return PartialInstructionControlledFailureInfo(
                PartialControlledFailureEnum.VALIDATION,
                'Name `{}\' has already been defined:\n\n{}'.format(
                    value_usage.name,
                    error_message_format.source_line(
                        file_ref_value.source)))
        else:
            for referenced_value in value_usage.referenced_values:
                failure_info = validate_pre_sds(referenced_value, symbol_table)
                if failure_info is not None:
                    return failure_info
            symbol_table.add(value_usage.symbol_table_entry)
            return None
    else:
        raise TypeError('Unknown variant of {}: {}'.format(str(value_definition_usage.ValueUsage),
                                                           str(value_usage)))


def _validate_reference_of_path(value_usage: value_definition_usage.ValueReferenceOfPath,
                                value_definitions: SymbolTable) -> str:
    referenced_value = value_definitions.lookup(value_usage.name)
    if not isinstance(referenced_value, sym_tbl.FileRefValue):
        return 'Referenced definition {} is not a path.'.format(value_usage.name)
    assert isinstance(referenced_value, sym_tbl.FileRefValue)
    actual_relativity = referenced_value.file_ref.relativity(value_definitions)
    if actual_relativity not in value_usage.valid_relativities.rel_option_types:
        return _invalid_relativity_error_message(value_usage, actual_relativity)
    return None


def _invalid_relativity_error_message(value_usage: value_definition_usage.ValueReferenceOfPath,
                                      actual_relativity: RelOptionType) -> str:
    # TODO [val-def] Improve error message -
    # - include valid relativities
    # - use option strings to display relativities (or environment variables)
    return ('Referenced variable `{}\' c,'
            ' since it is relative {}'.format(value_usage.name,
                                              actual_relativity
                                              ))
