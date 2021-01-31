from exactly_lib.util.str_.name import Name, NameWithGender
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def is_name() -> Assertion:
    return asrt.is_instance_with(Name,
                                 asrt.and_([
                                     asrt.sub_component('singular',
                                                        Name.singular.fget,
                                                        asrt.is_instance(str)),
                                     asrt.sub_component('plural',
                                                        Name.plural.fget,
                                                        asrt.is_instance(str)),
                                 ]))


def equals_name(name: Name) -> Assertion:
    return asrt.is_instance_with(Name,
                                 asrt.and_([
                                     asrt.sub_component('singular',
                                                        Name.singular.fget,
                                                        asrt.equals(name.singular)),
                                     asrt.sub_component('plural',
                                                        Name.plural.fget,
                                                        asrt.equals(name.plural)),
                                 ]))


def equals_name_with_gender(name: NameWithGender) -> Assertion[NameWithGender]:
    return asrt.is_instance_with(Name,
                                 asrt.and_([
                                     asrt.sub_component('determinator_word',
                                                        NameWithGender.determinator_word.fget,
                                                        asrt.equals(name.determinator_word)),
                                     asrt.sub_component('singular',
                                                        NameWithGender.singular.fget,
                                                        asrt.equals(name.singular)),
                                     asrt.sub_component('plural',
                                                        NameWithGender.plural.fget,
                                                        asrt.equals(name.plural)),
                                 ]))
