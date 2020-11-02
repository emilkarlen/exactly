from exactly_lib.impls.types.interval.with_interval import WithIntInterval
from exactly_lib.util.interval.int_interval import IntInterval
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def is_with_interval(plain: ValueAssertion[IntInterval],
                     complement: ValueAssertion[IntInterval] = asrt.anything_goes(),
                     ) -> ValueAssertion:
    return asrt.is_instance_with__many(
        WithIntInterval,
        [
            asrt.sub_component(
                'interval (positive)',
                _get_interval,
                plain,
            ),
            asrt.sub_component(
                'interval (inversion)',
                _get_inversion,
                complement,
            ),
        ]
    )


def _get_interval(x: WithIntInterval) -> IntInterval:
    return x.interval


def _get_inversion(x: WithIntInterval) -> IntInterval:
    return x.interval.inversion
