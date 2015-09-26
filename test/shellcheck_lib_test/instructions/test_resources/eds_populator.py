from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib_test.util.file_structure import DirContents


class EdsPopulator:
    def apply(self,
              eds: ExecutionDirectoryStructure):
        raise NotImplementedError()


class Empty(EdsPopulator):
    def apply(self, eds: ExecutionDirectoryStructure):
        pass


class FilesInActDir(EdsPopulator):
    def __init__(self,
                 test_root_contents: DirContents):
        self.test_root_contents = test_root_contents

    def apply(self, eds: ExecutionDirectoryStructure):
        self.test_root_contents.write_to(eds.act_dir)
