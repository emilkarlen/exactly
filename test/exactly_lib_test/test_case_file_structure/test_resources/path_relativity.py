from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, SpecificPathRelativity
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_path_relativity(expected: SpecificPathRelativity) -> asrt.ValueAssertion:
    return asrt.is_instance_with(SpecificPathRelativity,
                                 asrt.and_([
                                     asrt.sub_component('is_absolute',
                                                        SpecificPathRelativity.is_absolute.fget,
                                                        asrt.equals(expected.is_absolute)),
                                     asrt.sub_component('is_relative',
                                                        SpecificPathRelativity.is_relative.fget,
                                                        asrt.equals(expected.is_relative)),
                                     asrt.sub_component('relativity_type',
                                                        SpecificPathRelativity.relativity_type.fget,
                                                        asrt.equals(expected.relativity_type)),
                                 ])
                                 )


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
