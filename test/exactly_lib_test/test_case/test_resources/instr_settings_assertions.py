from typing import Optional, Mapping

from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def matches(
        environ: Assertion[Optional[Mapping[str, str]]] = asrt.anything_goes(),
) -> Assertion[InstructionSettings]:
    return asrt.is_instance_with(
        InstructionSettings,
        asrt.sub_component(
            'environ',
            _get_environ,
            environ,
        )
    )


def _get_environ(x: InstructionSettings) -> Optional[Mapping[str, str]]:
    return x.environ()
