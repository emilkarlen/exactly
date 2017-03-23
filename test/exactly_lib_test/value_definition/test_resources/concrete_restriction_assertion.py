from exactly_lib.test_case_file_structure.file_ref_relativity import PathRelativityVariants
from exactly_lib.value_definition.concrete_restrictions import FileRefRelativityRestriction, StringRestriction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_path_relativity_variants(expected: PathRelativityVariants) -> asrt.ValueAssertion:
    return asrt.is_instance_with(PathRelativityVariants,
                                 asrt.and_([
                                     asrt.sub_component('rel_option_types',
                                                        PathRelativityVariants.rel_option_types.fget,
                                                        asrt.equals(expected.rel_option_types)),
                                     asrt.sub_component('absolute',
                                                        PathRelativityVariants.absolute.fget,
                                                        asrt.equals(expected.absolute))
                                 ]))


def equals_file_ref_relativity_restriction(expected: FileRefRelativityRestriction) -> asrt.ValueAssertion:
    return asrt.is_instance_with(FileRefRelativityRestriction,
                                 asrt.sub_component('accepted',
                                                    FileRefRelativityRestriction.accepted.fget,
                                                    equals_path_relativity_variants(expected.accepted)))


is_string_value_restriction = asrt.is_instance(StringRestriction)
