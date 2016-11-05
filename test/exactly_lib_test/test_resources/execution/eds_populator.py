from exactly_lib.test_case.sandbox_directory_structure import ExecutionDirectoryStructure
from exactly_lib_test.test_resources.file_structure import DirContents


class EdsPopulator:
    def apply(self,
              eds: ExecutionDirectoryStructure):
        raise NotImplementedError()


def empty() -> EdsPopulator:
    return _Empty()


def multiple(populators: list) -> EdsPopulator:
    return _ListOfPopulators(populators)


def act_dir_contents(contents: DirContents) -> EdsPopulator:
    return _FilesInActDir(contents)


def tmp_user_dir_contents(contents: DirContents) -> EdsPopulator:
    return _FilesInTmpUserDir(contents)


def tmp_internal_dir_contents(contents: DirContents) -> EdsPopulator:
    return _FilesInTmpInternalDir(contents)


class _Empty(EdsPopulator):
    def apply(self, eds: ExecutionDirectoryStructure):
        pass


class _ListOfPopulators(EdsPopulator):
    def __init__(self, populator_list: list):
        self.__populator_list = populator_list

    def apply(self, eds: ExecutionDirectoryStructure):
        for populator in self.__populator_list:
            populator.apply(eds)


class _FilesInActDir(EdsPopulator):
    def __init__(self,
                 contents: DirContents):
        self.test_root_contents = contents

    def apply(self, eds: ExecutionDirectoryStructure):
        self.test_root_contents.write_to(eds.act_dir)


class _FilesInTmpUserDir(EdsPopulator):
    def __init__(self,
                 contents: DirContents):
        self.test_root_contents = contents

    def apply(self, eds: ExecutionDirectoryStructure):
        self.test_root_contents.write_to(eds.tmp.user_dir)


class _FilesInTmpInternalDir(EdsPopulator):
    def __init__(self,
                 contents: DirContents):
        self.test_root_contents = contents

    def apply(self, eds: ExecutionDirectoryStructure):
        self.test_root_contents.write_to(eds.tmp.internal_dir)
