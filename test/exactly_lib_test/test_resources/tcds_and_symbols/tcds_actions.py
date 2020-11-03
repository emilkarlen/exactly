import os

from exactly_lib.test_case.path_resolving_env import PathResolvingEnvironmentPreOrPostSds
from exactly_lib_test.tcfs.test_resources.sds_populator import SdsSubDirResolver
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import TcdsAction


class MkSubDirAndMakeItCurrentDirectory(TcdsAction):
    def __init__(self, sub_dir_resolver: SdsSubDirResolver):
        self.sub_dir_resolver = sub_dir_resolver

    def apply(self, environment: PathResolvingEnvironmentPreOrPostSds):
        sub_dir = self.sub_dir_resolver.population_dir__create_if_not_exists(environment.sds)
        os.chdir(str(sub_dir))


class ChangeDirectoryToDirectory(TcdsAction):
    def __init__(self, sub_dir_resolver: SdsSubDirResolver):
        self.sub_dir_resolver = sub_dir_resolver

    def apply(self, environment: PathResolvingEnvironmentPreOrPostSds):
        sub_dir = self.sub_dir_resolver.population_dir(environment.sds)
        os.chdir(str(sub_dir))
