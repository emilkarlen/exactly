from exactly_lib.tcfs.path_relativity import DirectoryStructurePartition
from exactly_lib_test.impls.types.test_resources import validation

FAILING_VALIDATION_ASSERTION_FOR_PARTITION = {
    DirectoryStructurePartition.HDS:
        validation.pre_sds_validation_fails__w_any_msg(),
    DirectoryStructurePartition.NON_HDS:
        validation.post_sds_validation_fails__w_any_msg(),
}
