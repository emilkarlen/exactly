from typing import Optional

from exactly_lib.instructions.multi_phase.utils.instruction_from_parts_for_executing_program import \
    ExecutionResultAndStderr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def equals(exit_code: int,
           stderr_contents: Optional[str]) -> ValueAssertion[ExecutionResultAndStderr]:
    return asrt.is_instance_with__many(
        ExecutionResultAndStderr,
        [
            asrt.sub_component(
                'exit_code',
                ExecutionResultAndStderr.exit_code.fget,
                asrt.equals(exit_code)
            ),
            asrt.sub_component(
                'stderr',
                ExecutionResultAndStderr.stderr_contents.fget,
                asrt.equals(stderr_contents)
            ),
        ]
    )
