from abc import ABC, abstractmethod
from typing import Sequence

from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import ExecutionExpectation
from exactly_lib_test.test_case.result.test_resources import pfh_assertions as asrt_pfh
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct2
from exactly_lib_test.test_case_file_structure.test_resources import tcds_populators
from exactly_lib_test.test_case_file_structure.test_resources.arguments_building import RelOptPathArgument
from exactly_lib_test.test_case_file_structure.test_resources.ds_construction import TcdsArrangementPostAct
from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir.test_resources.files_matcher_integration import \
    NumFilesSetup
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as fms_args
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import FilesMatcherArg
from exactly_lib_test.test_resources.arguments_building import ArgumentElementsRenderer, SequenceOfArguments, \
    OptionArgument
from exactly_lib_test.test_resources.files.file_structure import DirContents, Dir
from exactly_lib_test.test_resources.test_utils import NExArr


class NumFilesTestCaseHelperBase(ABC):
    def __init__(self,
                 setup: NumFilesSetup,
                 checked_dir_location: RelOptionType,
                 checked_dir_name: str,
                 ):
        self.setup = setup
        self.checked_dir_name = checked_dir_name
        self.checked_dir_location = checked_dir_location

    def argument__recursive(self) -> ArgumentElementsRenderer:
        return SequenceOfArguments([
            RelOptPathArgument(self.checked_dir_name,
                               self.checked_dir_location),
            OptionArgument(file_or_dir_contents.RECURSIVE_OPTION.name),
            self._files_matcher_arg(),
        ]
        )

    def argument__non_recursive(self) -> ArgumentElementsRenderer:
        return SequenceOfArguments([
            RelOptPathArgument(self.checked_dir_name,
                               self.checked_dir_location),
            self._files_matcher_arg(),
        ]
        )

    @abstractmethod
    def _files_matcher_arg(self) -> FilesMatcherArg:
        pass

    def execution_cases(self) -> Sequence[NExArr[ExecutionExpectation, ArrangementPostAct2]]:
        return [
            NExArr(
                case.name,
                ExecutionExpectation(
                    main_result=asrt_pfh.is_non_hard_error(case.expected)
                ),
                ArrangementPostAct2(
                    TcdsArrangementPostAct(
                        tcds_contents=tcds_populators.TcdsPopulatorForRelOptionType(
                            self.checked_dir_location,
                            DirContents([
                                Dir(self.checked_dir_name,
                                    case.actual)
                            ])
                        )
                    )
                )
            )
            for case in self.setup.cases
        ]


class NumFilesWoSelectionTestCaseHelper(NumFilesTestCaseHelperBase):
    def _files_matcher_arg(self) -> FilesMatcherArg:
        return self.setup.num_files_arg()


class NumFilesWFileTypeSelectionTestCaseHelper(NumFilesTestCaseHelperBase):
    def _files_matcher_arg(self) -> FilesMatcherArg:
        return fms_args.Selection(
            fm_args.Type(FileType.REGULAR),
            self.setup.num_files_arg())
