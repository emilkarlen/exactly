import pathlib

from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_resources.file_structure import DirContents, File


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


def cwd_contents(contents: DirContents) -> SdsPopulator:
    return _FilesInCwd(contents)


class SdsPopulatorForFileWithContentsThatDependOnSds(SdsPopulator):
    def __init__(self,
                 file_name: str,
                 sds__2__file_contents_str,
                 dir_contents__2__sds_populator):
        """
        :type sds__2__file_contents_str: `SandboxDirectoryStructure` -> str
        :type dir_contents__2__sds_populator: `DirContents` -> `SdsPopulator`
        """
        self.file_name = file_name
        self.sds_2_file_contents_str = sds__2__file_contents_str
        self.dir_contents__2__sds_populator = dir_contents__2__sds_populator

    def apply(self, sds: SandboxDirectoryStructure):
        file_contents = self.sds_2_file_contents_str(sds)
        dir_contents = DirContents([
            File(self.file_name, file_contents)
        ])
        sds_populator = self.dir_contents__2__sds_populator(dir_contents)
        sds_populator.write_to(sds)


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


class _FilesInCwd(SdsPopulator):
    def __init__(self,
                 contents: DirContents):
        self.test_root_contents = contents

    def apply(self, sds: SandboxDirectoryStructure):
        cwd = pathlib.Path().cwd()
        self.test_root_contents.write_to(cwd)
