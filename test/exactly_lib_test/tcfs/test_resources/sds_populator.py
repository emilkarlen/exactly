import pathlib
from typing import Sequence, Callable

from exactly_lib.tcfs.path_relativity import RelSdsOptionType
from exactly_lib.tcfs.relative_path_options import REL_SDS_OPTIONS_MAP
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib_test.tcfs.test_resources.dir_populator import SdsPopulator
from exactly_lib_test.test_resources.files.file_structure import DirContents


def empty() -> SdsPopulator:
    return multiple([])


def multiple(populators: Sequence[SdsPopulator]) -> SdsPopulator:
    return _ListOfPopulators(populators)


def tmp_internal_dir_contents(contents: DirContents) -> SdsPopulator:
    return _FilesInTmpInternalDir(contents)


def cwd_contents(contents: DirContents) -> SdsPopulator:
    return _FilesInCwd(contents)


def contents_in(relativity: RelSdsOptionType,
                dir_contents: DirContents) -> SdsPopulator:
    return _SdsPopulatorForRelSdsOptionType(relativity,
                                            dir_contents)


class SdsSubDirResolver:
    def root_dir(self, sds: SandboxDs) -> pathlib.Path:
        raise NotImplementedError()

    def population_dir(self, sds: SandboxDs) -> pathlib.Path:
        raise NotImplementedError()

    def population_dir__create_if_not_exists(self, sds: SandboxDs) -> pathlib.Path:
        sub_dir_path = self.population_dir(sds)
        sub_dir_path.mkdir(parents=True,
                           exist_ok=True)
        return sub_dir_path


class SdsSubDirResolverFromSdsFun(SdsSubDirResolver):
    def __init__(self, sds_2_path: Callable[[SandboxDs], pathlib.Path]):
        self.sds_2_path = sds_2_path

    def root_dir(self, sds: SandboxDs) -> pathlib.Path:
        return self.sds_2_path(sds)

    def population_dir(self, sds: SandboxDs) -> pathlib.Path:
        return self.root_dir(sds)


class SdsSubDirResolverWithRelSdsRoot(SdsSubDirResolver):
    def __init__(self,
                 relativity: RelSdsOptionType,
                 sub_dir: str):
        self.relativity = relativity
        self.sub_dir = sub_dir

    def root_dir(self, sds: SandboxDs) -> pathlib.Path:
        return REL_SDS_OPTIONS_MAP[self.relativity].root_resolver.from_sds(sds)

    def population_dir(self, sds: SandboxDs) -> pathlib.Path:
        return self.root_dir(sds) / self.sub_dir


class SdsPopulatorForSubDir(SdsPopulator):
    def __init__(self,
                 sub_dir_resolver: SdsSubDirResolver,
                 dir_contents: DirContents):
        self._sub_dir_resolver = sub_dir_resolver
        self.dir_contents = dir_contents

    @property
    def sub_dir_resolver(self) -> SdsSubDirResolver:
        return self._sub_dir_resolver

    def population_dir(self, sds: SandboxDs) -> pathlib.Path:
        return self._sub_dir_resolver.population_dir(sds)

    def populate_sds(self, sds: SandboxDs):
        sub_dir_path = self._sub_dir_resolver.population_dir__create_if_not_exists(sds)
        self.dir_contents.write_to(sub_dir_path)


def contents_in_resolved_dir(dir_resolver: SdsSubDirResolver,
                             dir_contents: DirContents) -> SdsPopulatorForSubDir:
    return SdsPopulatorForSubDir(dir_resolver,
                                 dir_contents)


class _ListOfPopulators(SdsPopulator):
    def __init__(self, populator_list: Sequence[SdsPopulator]):
        self.__populator_list = populator_list

    def populate_sds(self, sds: SandboxDs):
        for populator in self.__populator_list:
            populator.populate_sds(sds)


class _FilesInTmpInternalDir(SdsPopulator):
    def __init__(self,
                 contents: DirContents):
        self.test_root_contents = contents

    def populate_sds(self, sds: SandboxDs):
        self.test_root_contents.write_to(sds.internal_tmp_dir)


class _FilesInCwd(SdsPopulator):
    def __init__(self,
                 contents: DirContents):
        self.test_root_contents = contents

    def populate_sds(self, sds: SandboxDs):
        cwd = pathlib.Path().cwd()
        self.test_root_contents.write_to(cwd)


class _SdsPopulatorForRelSdsOptionType(SdsPopulator):
    def __init__(self,
                 relativity: RelSdsOptionType,
                 dir_contents: DirContents):
        self.relativity = relativity
        self.dir_contents = dir_contents

    def populate_sds(self, sds: SandboxDs):
        root_path = REL_SDS_OPTIONS_MAP[self.relativity].root_resolver.from_sds(sds)
        self.dir_contents.write_to(root_path)
