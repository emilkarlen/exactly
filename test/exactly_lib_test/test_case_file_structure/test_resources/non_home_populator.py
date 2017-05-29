from exactly_lib.test_case_file_structure import relative_path_options
from exactly_lib.test_case_file_structure.path_relativity import RelNonHomeOptionType
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import SdsPopulator
from exactly_lib_test.test_resources.file_structure import DirContents


class NonHomePopulator:
    def apply(self,
              sds: SandboxDirectoryStructure):
        raise NotImplementedError()


def rel_option(relativity: RelNonHomeOptionType,
               dir_contents: DirContents) -> NonHomePopulator:
    return _NonHomePopulatorForRelativityOption(relativity,
                                                dir_contents)


def from_sds_populator(sds_populator: SdsPopulator) -> NonHomePopulator:
    return _NonHomePopulatorFromSdsPopulator(sds_populator)


class _NonHomePopulatorForRelativityOption(NonHomePopulator):
    def __init__(self,
                 relativity: RelNonHomeOptionType,
                 dir_contents: DirContents):
        self.relativity = relativity
        self.dir_contents = dir_contents

    def apply(self,
              sds: SandboxDirectoryStructure):
        root_path = relative_path_options.REL_NON_HOME_OPTIONS_MAP[self.relativity].root_resolver.from_sds(sds)
        self.dir_contents.write_to(root_path)


class _NonHomePopulatorFromSdsPopulator(NonHomePopulator):
    def __init__(self,
                 sds_populator: SdsPopulator):
        self.sds_populator = sds_populator

    def apply(self,
              sds: SandboxDirectoryStructure):
        self.sds_populator.apply(sds)
