from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def assert_is_single_instruction_invalid_argument_exception() -> Assertion:
    return asrt.is_instance_with(SingleInstructionInvalidArgumentException,
                                 asrt.sub_component('error_message',
                                                    lambda ex: ex.error_message,
                                                    asrt.is_instance(str)))
