from exactly_lib.type_system.logic.lines_transformer import StringTransformer
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def is_identity_transformer() -> asrt.ValueAssertion[StringTransformer]:
    def get_is_identity(x: StringTransformer) -> bool:
        return x.is_identity_transformer

    return asrt.is_instance_with(StringTransformer,
                                 asrt.sub_component('is_identity',
                                                    get_is_identity,
                                                    asrt.equals(True)),
                                 )
