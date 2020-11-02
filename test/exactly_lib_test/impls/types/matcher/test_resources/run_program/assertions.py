from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import matcher
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib_test.impls.types.program.test_resources import trace_assertions as asrt_pgm_trace
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result

_EXPECTED_HEADER = ' '.join((matcher.RUN_PROGRAM,
                             syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name))


def is_result_for_py_interpreter(exit_code: int) -> ValueAssertion[MatchingResult]:
    return asrt_matching_result.matches_value__w_header(
        value=asrt.equals(exit_code == 0),
        header=asrt.equals(_EXPECTED_HEADER),
        details=asrt.is_sequence_with_element_at_pos(
            0,
            asrt_pgm_trace.matches_pgm_as_detail__py_interpreter()
        )
    )
