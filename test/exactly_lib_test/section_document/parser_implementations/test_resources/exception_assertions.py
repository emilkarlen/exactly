from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def assert_is_single_instruction_invalid_argument_exception() -> asrt.ValueAssertion:
    return asrt.is_instance_with(SingleInstructionInvalidArgumentException,
                                 asrt.sub_component('error_message',
                                                    lambda ex: ex.error_message,
                                                    asrt.is_instance(str)))
