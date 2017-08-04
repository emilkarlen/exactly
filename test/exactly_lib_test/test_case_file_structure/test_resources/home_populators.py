import pathlib

from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import HomePopulator
from exactly_lib_test.test_resources.file_structure import DirContents


def empty() -> HomePopulator:
    return multiple([])


def multiple(home_populators: list) -> HomePopulator:
    return _ListOfPopulators(home_populators)


def case_home_dir_contents(contents: DirContents) -> HomePopulator:
    return _FilesInCaseHomeDir(contents)


# def contents_in(relativity: RelSdsOptionType,
#                 dir_contents: DirContents) -> SdsPopulator:
#     return _SdsPopulatorForRelSdsOptionType(relativity,
#                                             dir_contents)


# class SdsSubDirResolver:
#     def root_dir(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
#         raise NotImplementedError()
#
#     def population_dir(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
#         raise NotImplementedError()
#
#     def population_dir__create_if_not_exists(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
#         sub_dir_path = self.population_dir(sds)
#         sub_dir_path.mkdir(parents=True,
#                            exist_ok=True)
#         return sub_dir_path
#
#
# class SdsSubDirResolverFromSdsFun(SdsSubDirResolver):
#     def __init__(self, sds_2_path: types.FunctionType):
#         self.sds_2_path = sds_2_path
#
#     def root_dir(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
#         return self.sds_2_path(sds)
#
#     def population_dir(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
#         return self.root_dir(sds)
#
#
# class SdsSubDirResolverWithRelSdsRoot(SdsSubDirResolver):
#     def __init__(self,
#                  relativity: RelSdsOptionType,
#                  sub_dir: str):
#         self.relativity = relativity
#         self.sub_dir = sub_dir
#
#     def root_dir(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
#         return REL_SDS_OPTIONS_MAP[self.relativity].root_resolver.from_sds(sds)
#
#     def population_dir(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
#         return self.root_dir(sds) / self.sub_dir
#
#
# class SdsPopulatorForSubDir(SdsPopulator):
#     def __init__(self,
#                  sub_dir_resolver: SdsSubDirResolver,
#                  dir_contents: DirContents):
#         self._sub_dir_resolver = sub_dir_resolver
#         self.dir_contents = dir_contents
#
#     @property
#     def sub_dir_resolver(self) -> SdsSubDirResolver:
#         return self._sub_dir_resolver
#
#     def population_dir(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
#         return self._sub_dir_resolver.population_dir(sds)
#
#     def populate_sds(self, sds: SandboxDirectoryStructure):
#         sub_dir_path = self._sub_dir_resolver.population_dir__create_if_not_exists(sds)
#         self.dir_contents.write_to(sub_dir_path)
#
#
# def contents_in_sub_dir_of(relativity: RelSdsOptionType,
#                            sub_dir: str,
#                            dir_contents: DirContents) -> SdsPopulatorForSubDir:
#     return SdsPopulatorForSubDir(SdsSubDirResolverWithRelSdsRoot(relativity,
#                                                                  sub_dir),
#                                  dir_contents)
#
#
# def contents_in_resolved_dir(dir_resolver: SdsSubDirResolver,
#                              dir_contents: DirContents) -> SdsPopulatorForSubDir:
#     return SdsPopulatorForSubDir(dir_resolver,
#                                  dir_contents)
#
#
# class SdsPopulatorForFileWithContentsThatDependOnSds(SdsPopulator):
#     def __init__(self,
#                  file_name: str,
#                  sds__2__file_contents_str,
#                  dir_contents__2__sds_populator):
#         """
#         :type sds__2__file_contents_str: `SandboxDirectoryStructure` -> str
#         :type dir_contents__2__sds_populator: `DirContents` -> `SdsPopulator`
#         """
#         self.file_name = file_name
#         self.sds_2_file_contents_str = sds__2__file_contents_str
#         self.dir_contents__2__sds_populator = dir_contents__2__sds_populator
#
#     def populate_sds(self, sds: SandboxDirectoryStructure):
#         file_contents = self.sds_2_file_contents_str(sds)
#         dir_contents = DirContents([
#             File(self.file_name, file_contents)
#         ])
#         sds_populator = self.dir_contents__2__sds_populator(dir_contents)
#         sds_populator.write_to(sds)
#
#
class _ListOfPopulators(HomePopulator):
    def __init__(self, home_populators: list):
        for populator in home_populators:
            assert isinstance(populator, HomePopulator)
        self.__populator_list = home_populators

    def populate_hds(self, hds: HomeDirectoryStructure):
        for populator in self.__populator_list:
            assert isinstance(populator, HomePopulator)
            populator.populate_hds(hds)


class _FilesInCaseHomeDir(HomePopulator):
    def __init__(self,
                 contents: DirContents):
        self.test_root_contents = contents

    def populate_home(self, home_dir: pathlib.Path):
        self.test_root_contents.write_to(home_dir)

    def populate_hds(self, hds: HomeDirectoryStructure):
        self.populate_home(hds.case_dir)

# class _SdsPopulatorForRelSdsOptionType(SdsPopulator):
#     def __init__(self,
#                  relativity: RelSdsOptionType,
#                  dir_contents: DirContents):
#         self.relativity = relativity
#         self.dir_contents = dir_contents
#
#     def populate_sds(self, sds: SandboxDirectoryStructure):
#         root_path = REL_SDS_OPTIONS_MAP[self.relativity].root_resolver.from_sds(sds)
#         self.dir_contents.write_to(root_path)
