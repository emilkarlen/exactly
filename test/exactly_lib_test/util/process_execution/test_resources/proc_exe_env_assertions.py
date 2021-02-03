from typing import Optional, Dict

from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def matches(
        timeout_in_seconds: Assertion[Optional[int]] = asrt.anything_goes(),
        environ: Assertion[Optional[Dict[str, str]]] = asrt.anything_goes(),
) -> Assertion[ProcessExecutionSettings]:
    return asrt.is_instance_with__many(
        ProcessExecutionSettings,
        [
            asrt.sub_component(
                'timeout',
                ProcessExecutionSettings.timeout_in_seconds.fget,
                timeout_in_seconds,
            ),
            asrt.sub_component(
                'environ',
                ProcessExecutionSettings.environ.fget,
                environ,
            ),
        ]
    )
