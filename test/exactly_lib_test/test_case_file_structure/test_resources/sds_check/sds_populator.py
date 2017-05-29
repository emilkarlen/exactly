import pathlib

from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib.test_case_file_structure.relative_path_options import REL_SDS_OPTIONS_MAP
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import SdsPopulator
from exactly_lib_test.test_resources.file_structure import DirContents, File


def empty() -> SdsPopulator:
    return multiple([])


def multiple(populators: list) -> SdsPopulator:
    return _ListOfPopulators(populators)


def tmp_internal_dir_contents(contents: DirContents) -> SdsPopulator:
    return _FilesInTmpInternalDir(contents)


def cwd_contents(contents: DirContents) -> SdsPopulator:
    return _FilesInCwd(contents)


def contents_in(relativity: RelSdsOptionType,
                dir_contents: DirContents) -> SdsPopulator:
    return _SdsPopulatorForRelSdsOptionType(relativity,
                                            dir_contents)


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

    def populate_sds(self, sds: SandboxDirectoryStructure):
        file_contents = self.sds_2_file_contents_str(sds)
        dir_contents = DirContents([
            File(self.file_name, file_contents)
        ])
        sds_populator = self.dir_contents__2__sds_populator(dir_contents)
        sds_populator.write_to(sds)


class _ListOfPopulators(SdsPopulator):
    def __init__(self, populator_list: list):
        self.__populator_list = populator_list

    def populate_sds(self, sds: SandboxDirectoryStructure):
        for populator in self.__populator_list:
            populator.apply(sds)


class _FilesInTmpInternalDir(SdsPopulator):
    def __init__(self,
                 contents: DirContents):
        self.test_root_contents = contents

    def populate_sds(self, sds: SandboxDirectoryStructure):
        self.test_root_contents.write_to(sds.tmp.internal_dir)


class _FilesInCwd(SdsPopulator):
    def __init__(self,
                 contents: DirContents):
        self.test_root_contents = contents

    def populate_sds(self, sds: SandboxDirectoryStructure):
        cwd = pathlib.Path().cwd()
        self.test_root_contents.write_to(cwd)


class _SdsPopulatorForRelSdsOptionType(SdsPopulator):
    def __init__(self,
                 relativity: RelSdsOptionType,
                 dir_contents: DirContents):
        self.relativity = relativity
        self.dir_contents = dir_contents

    def populate_sds(self, sds: SandboxDirectoryStructure):
        root_path = REL_SDS_OPTIONS_MAP[self.relativity].root_resolver.from_sds(sds)
        self.dir_contents.write_to(root_path)
