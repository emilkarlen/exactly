import pathlib
import unittest
from typing import Callable

from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.tcfs.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib_test.test_resources.files import file_structure
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.file_assertions import DirContainsExactly
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder, Assertion, \
    AssertionBase


def dir_contains_exactly(relativity_option: RelOptionType,
                         expected_contents: file_structure.DirContents
                         ) -> Assertion[SandboxDs]:
    return asrt.sub_component('relativity_option=' + str(relativity_option),
                              REL_OPTIONS_MAP[relativity_option].root_resolver.from_non_hds,
                              DirContainsExactly(expected_contents))


def act_dir_contains_exactly(expected_contents: file_structure.DirContents
                             ) -> Assertion[SandboxDs]:
    return asrt.sub_component('act dir',
                              SandboxDs.act_dir.fget,
                              DirContainsExactly(expected_contents))


def tmp_user_dir_contains_exactly(expected_contents: file_structure.DirContents
                                  ) -> Assertion[SandboxDs]:
    return asrt.sub_component('user tmp dir',
                              SandboxDs.user_tmp_dir.fget,
                              DirContainsExactly(expected_contents))


def tmp_internal_dir_contains_exactly(expected_contents: file_structure.DirContents
                                      ) -> Assertion[SandboxDs]:
    return asrt.sub_component('internal tmp dir',
                              SandboxDs.internal_tmp_dir.fget,
                              DirContainsExactly(expected_contents))


def result_dir_contains_exactly(expected_contents: file_structure.DirContents
                                ) -> Assertion[SandboxDs]:
    return asrt.sub_component('result dir',
                              SandboxDs.result_dir.fget,
                              DirContainsExactly(expected_contents))


def cwd_contains_exactly(expected_contents: file_structure.DirContents
                         ) -> Assertion[SandboxDs]:
    return asrt.sub_component('result dir',
                              lambda sds: pathlib.Path().cwd(),
                              DirContainsExactly(expected_contents))


def sub_dir_of_sds_contains_exactly(sds__2__root_dir_path: Callable[[SandboxDs], pathlib.Path],
                                    expected_contents: file_structure.DirContents,
                                    description: str = 'custom sub dir of sds') -> Assertion[SandboxDs]:
    return asrt.sub_component(description,
                              sds__2__root_dir_path,
                              DirContainsExactly(expected_contents))


def non_hds_dir_contains_exactly(sds__2__root_dir_path: Callable[[SandboxDs], pathlib.Path],
                                 expected_contents: file_structure.DirContents) -> Assertion[SandboxDs]:
    return NonHdsDirContainsExactly(sds__2__root_dir_path, expected_contents)


class SubDirOfSdsContainsExactly(AssertionBase[SandboxDs]):
    def __init__(self,
                 sds__2__root_dir_path: Callable[[SandboxDs], pathlib.Path],
                 expected_contents: file_structure.DirContents,
                 description: str = 'custom sub dir of sds'):
        self._description = description
        self._expected_contents = expected_contents
        self.sds__2__root_dir_path = sds__2__root_dir_path

    def _apply(self,
               put: unittest.TestCase,
               sds: SandboxDs,
               message_builder: MessageBuilder):
        assertion = asrt.sub_component(self._description,
                                       self.sds__2__root_dir_path,
                                       DirContainsExactly(self._expected_contents))
        assertion.apply(put, sds, message_builder)


class NonHdsDirContainsExactly(AssertionBase[SandboxDs]):
    def __init__(self,
                 sds__2__root_dir_path: Callable[[SandboxDs], pathlib.Path],
                 expected_contents: file_structure.DirContents,
                 description: str = 'custom non-home directory'):
        self._description = description
        self._expected_contents = expected_contents
        self.sds__2__root_dir_path = sds__2__root_dir_path

    def _apply(self,
               put: unittest.TestCase,
               sds: SandboxDs,
               message_builder: MessageBuilder):
        assertion = asrt.sub_component(self._description,
                                       self.sds__2__root_dir_path,
                                       DirContainsExactly(self._expected_contents))
        assertion.apply(put, sds, message_builder)
