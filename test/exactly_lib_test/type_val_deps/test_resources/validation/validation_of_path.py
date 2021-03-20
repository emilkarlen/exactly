from exactly_lib.tcfs.path_relativity import DirectoryStructurePartition
from exactly_lib_test.type_val_deps.test_resources.validation import validation

FAILING_VALIDATION_ASSERTION_FOR_PARTITION = {
    DirectoryStructurePartition.HDS:
        validation.ValidationAssertions.pre_sds_fails__w_any_msg(),
    DirectoryStructurePartition.NON_HDS:
        validation.ValidationAssertions.post_sds_fails__w_any_msg(),
}
