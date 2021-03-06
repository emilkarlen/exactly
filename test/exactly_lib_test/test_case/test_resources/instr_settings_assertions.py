from typing import Optional, Mapping, Dict

from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def matches(
        environ: Assertion[Optional[Mapping[str, str]]] = asrt.anything_goes(),
        return_value_from_default_getter: Assertion[Dict[str, str]] = asrt.anything_goes(),
        timeout: Assertion[Optional[int]] = asrt.is_none_or_instance(int),
) -> Assertion[InstructionSettings]:
    return asrt.is_instance_with__many(
        InstructionSettings,
        [
            asrt.sub_component(
                'timeout',
                _get_timeout,
                timeout,
            ),
            asrt.sub_component(
                'environ',
                _get_environ,
                environ,
            ),
            asrt.sub_component(
                'return value from default environ getter',
                _get_default_environ,
                asrt.is_instance_with(dict, return_value_from_default_getter),
            ),
        ]
    )


def _get_environ(x: InstructionSettings) -> Optional[Mapping[str, str]]:
    return x.environ()


def _get_timeout(x: InstructionSettings) -> Optional[int]:
    return x.timeout_in_seconds()


def _get_default_environ(x: InstructionSettings) -> Dict[str, str]:
    return x.default_environ_getter()
