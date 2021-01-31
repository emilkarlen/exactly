from exactly_lib.tcfs.path_relativity import PathRelativityVariants
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def equals_path_relativity_variants(expected: PathRelativityVariants) -> Assertion:
    return asrt.is_instance_with(PathRelativityVariants,
                                 asrt.and_([
                                     asrt.sub_component('rel_option_types',
                                                        PathRelativityVariants.rel_option_types.fget,
                                                        asrt.equals(expected.rel_option_types)),
                                     asrt.sub_component('absolute',
                                                        PathRelativityVariants.absolute.fget,
                                                        asrt.equals(expected.absolute))
                                 ]))
