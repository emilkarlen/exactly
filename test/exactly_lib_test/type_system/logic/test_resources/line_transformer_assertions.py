from exactly_lib.type_system.logic.lines_transformer import LinesTransformer
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def is_identity_transformer() -> asrt.ValueAssertion[LinesTransformer]:
    def get_is_identity(x: LinesTransformer) -> bool:
        return x.is_identity_transformer

    return asrt.is_instance_with(LinesTransformer,
                                 asrt.sub_component('is_identity',
                                                    get_is_identity,
                                                    asrt.equals(True)),
                                 )
