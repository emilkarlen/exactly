import os
import tempfile
from contextlib import contextmanager
from time import strftime, localtime

from exactly_lib import program_info
from exactly_lib.symbol.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.util.file_utils import resolved_path, preserved_cwd
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import home_or_sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_utils import SdsAction, \
    sandbox_directory_structure
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir_contents


class HomeAndSdsAction:
    def apply(self, environment: PathResolvingEnvironmentPreOrPostSds):
        pass


class HomeAndSdsActionFromSdsAction(HomeAndSdsAction):
    def __init__(self, sds_action: SdsAction):
        self.sds_action = sds_action

    def apply(self, environment: PathResolvingEnvironmentPreOrPostSds):
        return self.sds_action.apply(environment)


class HomeAndSdsContents(tuple):
    def __new__(cls,
                home_dir_contents: DirContents = empty_dir_contents(),
                sds_contents: sds_populator.SdsPopulator = sds_populator.empty()):
        return tuple.__new__(cls, (home_dir_contents,
                                   sds_contents))

    @property
    def home_dir_contents(self) -> DirContents:
        return self[0]

    @property
    def sds_contents(self) -> sds_populator.SdsPopulator:
        return self[1]


@contextmanager
def home_and_sds_with_act_as_curr_dir(
        home_dir_contents: DirContents = empty_dir_contents(),
        sds_contents: sds_populator.SdsPopulator = sds_populator.empty(),
        home_or_sds_contents: home_or_sds_populator.HomeOrSdsPopulator = home_or_sds_populator.empty(),
        pre_contents_population_action: HomeAndSdsAction = HomeAndSdsAction()) -> HomeAndSds:
    prefix = strftime(program_info.PROGRAM_NAME + '-test-%Y-%m-%d-%H-%M-%S', localtime())
    with tempfile.TemporaryDirectory(prefix=prefix + "-home-") as home_dir:
        home_dir_path = resolved_path(home_dir)
        with sandbox_directory_structure(prefix=prefix + "-sds-") as sds:
            ret_val = HomeAndSds(home_dir_path, sds)
            with preserved_cwd():
                os.chdir(str(sds.act_dir))
                pre_contents_population_action.apply(ret_val)
                home_dir_contents.write_to(home_dir_path)
                sds_contents.apply(sds)
                home_or_sds_contents.write_to(ret_val)
                yield ret_val
