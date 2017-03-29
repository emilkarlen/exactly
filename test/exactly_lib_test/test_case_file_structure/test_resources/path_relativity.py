from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def path_relativity_variants_equals(expected: PathRelativityVariants) -> asrt.ValueAssertion:
    return asrt.is_instance_with(PathRelativityVariants,
                                 asrt.And([
                                     asrt.sub_component('rel_option_types',
                                                        PathRelativityVariants.rel_option_types.fget,
                                                        asrt.equals(expected.rel_option_types)),
                                     asrt.sub_component('absolute',
                                                        PathRelativityVariants.absolute.fget,
                                                        asrt.equals(expected.absolute)),
                                 ]))
