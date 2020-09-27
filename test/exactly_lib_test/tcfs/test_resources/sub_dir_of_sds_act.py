from exactly_lib.tcfs.path_relativity import RelSdsOptionType
from exactly_lib_test.tcfs.test_resources.ds_action import MkSubDirAndMakeItCurrentDirectory
from exactly_lib_test.tcfs.test_resources.sds_populator import SdsSubDirResolverWithRelSdsRoot

_SUB_DIR_OF_ACT_DIR_THAT_IS_CWD = 'test-cwd'
SUB_DIR_RESOLVER = SdsSubDirResolverWithRelSdsRoot(RelSdsOptionType.REL_ACT,
                                                   _SUB_DIR_OF_ACT_DIR_THAT_IS_CWD)
MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY = MkSubDirAndMakeItCurrentDirectory(SUB_DIR_RESOLVER)
