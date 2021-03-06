from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def is_identity_transformer(expected: bool) -> Assertion[StringTransformer]:
    def get_is_identity(x: StringTransformer) -> bool:
        return x.is_identity_transformer

    return asrt.is_instance_with(StringTransformer,
                                 asrt.sub_component('is_identity',
                                                    get_is_identity,
                                                    asrt.is_instance_with(bool, asrt.equals(expected))),
                                 )
