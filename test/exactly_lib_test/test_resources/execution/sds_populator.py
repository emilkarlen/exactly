from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_resources.file_structure import DirContents


class SdsPopulator:
    def apply(self,
              sds: SandboxDirectoryStructure):
        raise NotImplementedError()


def empty() -> SdsPopulator:
    return _Empty()


def multiple(populators: list) -> SdsPopulator:
    return _ListOfPopulators(populators)


def act_dir_contents(contents: DirContents) -> SdsPopulator:
    return _FilesInActDir(contents)


def tmp_user_dir_contents(contents: DirContents) -> SdsPopulator:
    return _FilesInTmpUserDir(contents)


def tmp_internal_dir_contents(contents: DirContents) -> SdsPopulator:
    return _FilesInTmpInternalDir(contents)


class _Empty(SdsPopulator):
    def apply(self, sds: SandboxDirectoryStructure):
        pass


class _ListOfPopulators(SdsPopulator):
    def __init__(self, populator_list: list):
        self.__populator_list = populator_list

    def apply(self, sds: SandboxDirectoryStructure):
        for populator in self.__populator_list:
            populator.apply(sds)


class _FilesInActDir(SdsPopulator):
    def __init__(self,
                 contents: DirContents):
        self.test_root_contents = contents

    def apply(self, sds: SandboxDirectoryStructure):
        self.test_root_contents.write_to(sds.act_dir)


class _FilesInTmpUserDir(SdsPopulator):
    def __init__(self,
                 contents: DirContents):
        self.test_root_contents = contents

    def apply(self, sds: SandboxDirectoryStructure):
        self.test_root_contents.write_to(sds.tmp.user_dir)


class _FilesInTmpInternalDir(SdsPopulator):
    def __init__(self,
                 contents: DirContents):
        self.test_root_contents = contents

    def apply(self, sds: SandboxDirectoryStructure):
        self.test_root_contents.write_to(sds.tmp.internal_dir)
