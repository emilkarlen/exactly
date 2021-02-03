from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import MultiSourceExpectation, \
    ExecutionExpectation
from exactly_lib_test.test_case.result.test_resources import pfh_assertions

IS_PASS = MultiSourceExpectation()
IS_FAIL = MultiSourceExpectation(
    execution=ExecutionExpectation(
        main_result=pfh_assertions.is_fail__with_arbitrary_message()
    )
)
