from exactly_lib.util.name import Name
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def is_name() -> asrt.ValueAssertion:
    return asrt.is_instance_with(Name,
                                 asrt.and_([
                                     asrt.sub_component('singular',
                                                        Name.singular.fget,
                                                        asrt.is_instance(str)),
                                     asrt.sub_component('plural',
                                                        Name.plural.fget,
                                                        asrt.is_instance(str)),
                                 ]))


def equals_name(name: Name) -> asrt.ValueAssertion:
    return asrt.is_instance_with(Name,
                                 asrt.and_([
                                     asrt.sub_component('singular',
                                                        Name.singular.fget,
                                                        asrt.equals(name.singular)),
                                     asrt.sub_component('plural',
                                                        Name.plural.fget,
                                                        asrt.equals(name.plural)),
                                 ]))
