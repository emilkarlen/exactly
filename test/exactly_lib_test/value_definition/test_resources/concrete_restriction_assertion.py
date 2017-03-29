from exactly_lib.value_definition.concrete_restrictions import FileRefRelativityRestriction, StringRestriction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.value_definition.test_resources.path_relativity import equals_path_relativity_variants


def equals_file_ref_relativity_restriction(expected: FileRefRelativityRestriction) -> asrt.ValueAssertion:
    return asrt.is_instance_with(FileRefRelativityRestriction,
                                 asrt.sub_component('accepted',
                                                    FileRefRelativityRestriction.accepted.fget,
                                                    equals_path_relativity_variants(expected.accepted)))


is_string_value_restriction = asrt.is_instance(StringRestriction)
