from abc import ABC, abstractmethod
from typing import Sequence

from exactly_lib.impls.file_properties import FileType
from exactly_lib.impls.types.condition import comparators
from exactly_lib.impls.types.condition.comparators import ComparisonOperator
from exactly_lib.tcfs.path_relativity import RelSdsOptionType
from exactly_lib.type_val_prims.matcher.files_matcher import FilesMatcher
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib_test.impls.types.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.impls.types.file_matcher.test_resources.argument_building import FileMatcherArg
from exactly_lib_test.impls.types.files_matcher.test_resources import arguments_building as fms_args
from exactly_lib_test.impls.types.files_matcher.test_resources.arguments_building import FilesMatcherArg
from exactly_lib_test.impls.types.integer.test_resources.arguments_building import int_condition
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Arrangement, arrangement_w_tcds, \
    PrimAndExeExpectation
from exactly_lib_test.tcfs.test_resources import sds_populator
from exactly_lib_test.test_resources.files.file_structure import FileSystemElement, Dir, DirContents, File
from exactly_lib_test.test_resources.test_utils import NEA, NExArr
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result


class NumFilesSetup:
    def __init__(self,
                 num_files_expr_operator: ComparisonOperator,
                 num_files_expr_operand: int,
                 cases: Sequence[NEA[bool, Sequence[FileSystemElement]]],
                 ):
        self.num_files_expr_operand = num_files_expr_operand
        self.num_files_expectation_operator = num_files_expr_operator
        self.cases = cases

    def num_files_arg(self) -> FilesMatcherArg:
        return fms_args.NumFiles(
            int_condition(self.num_files_expectation_operator,
                          self.num_files_expr_operand)
        )


MODEL_CONTENTS__NON_RECURSIVE = NumFilesSetup(
    comparators.EQ,
    2,
    [
        NEA(
            'match',
            True,
            [
                File.empty('a-file'),
                Dir('a-dir',
                    [File.empty('a-file-in-a-dir')]
                    ),
            ]
        ),
        NEA(
            'not match',
            False,
            [
                Dir('a-dir',
                    [File.empty('a-file-in-dir')]
                    ),
            ]
        ),
    ]
)

MODEL_CONTENTS__NON_RECURSIVE__SELECTION_TYPE_FILE = NumFilesSetup(
    comparators.EQ,
    1,
    [
        NEA(
            'match',
            True,
            [
                File.empty('file-1'),
                Dir('a-dir',
                    [File.empty('a-file-in-a-dir')]
                    ),
            ]
        ),
        NEA(
            'not match',
            False,
            [
                Dir('a-dir',
                    [File.empty('a-file-in-dir')]
                    ),
            ]
        ),
    ]
)

MODEL_CONTENTS__RECURSIVE = NumFilesSetup(
    comparators.EQ,
    3,
    [
        NEA(
            'match',
            True,
            [
                File.empty('a-file'),
                Dir('a-dir',
                    [File.empty('a-file-in-a-dir')]
                    ),
            ]
        ),
        NEA(
            'not match',
            False,
            [
                File.empty('a-file'),
                File.empty('another-file'),
                Dir('a-dir',
                    [File.empty('a-file-in-dir')]
                    ),
            ]
        ),
    ]
)

MODEL_CONTENTS__RECURSIVE__SELECTION_TYPE_FILE = NumFilesSetup(
    comparators.EQ,
    2,
    [
        NEA(
            'match',
            True,
            [
                File.empty('a-file'),
                Dir('a-dir',
                    [File.empty('a-file-in-a-dir')]
                    ),
            ]
        ),
        NEA(
            'not match',
            False,
            [
                File.empty('file-1'),
                File.empty('file-2'),
                Dir('a-dir',
                    [File.empty('file-in-dir')]
                    ),
            ]
        ),
    ]
)


class NumFilesTestCaseHelperBase(ABC):
    def __init__(self,
                 setup: NumFilesSetup,
                 checked_dir_location: RelSdsOptionType,
                 checked_dir_name: str,
                 ):
        self.setup = setup
        self.checked_dir_name = checked_dir_name
        self.checked_dir_location = checked_dir_location

    @abstractmethod
    def arg__recursive(self) -> FileMatcherArg:
        raise NotImplementedError('abstract method')

    @abstractmethod
    def arg__non_recursive(self) -> FileMatcherArg:
        raise NotImplementedError('abstract method')

    def execution_cases(self) -> Sequence[NExArr[PrimAndExeExpectation[FilesMatcher, MatchingResult], Arrangement]]:
        return [
            NExArr(
                case.name,
                PrimAndExeExpectation.of_exe(
                    main_result=asrt_matching_result.matches_value(case.expected)
                ),
                arrangement_w_tcds(
                    non_hds_contents=sds_populator.contents_in(
                        self.checked_dir_location,
                        DirContents([
                            Dir(self.checked_dir_name,
                                case.actual)
                        ])
                    )
                )
            )
            for case in self.setup.cases
        ]


class NumFilesWoSelectionTestCaseHelper(NumFilesTestCaseHelperBase):
    def arg__recursive(self) -> FileMatcherArg:
        return fm_args.DirContentsRecursive(self.setup.num_files_arg())

    def arg__non_recursive(self) -> FileMatcherArg:
        return fm_args.DirContents(self.setup.num_files_arg())


class NumFilesWFileTypeSelectionTestCaseHelper(NumFilesTestCaseHelperBase):
    def arg__recursive(self) -> FileMatcherArg:
        return fm_args.DirContentsRecursive(
            fms_args.Selection(
                fm_args.Type(FileType.REGULAR),
                self.setup.num_files_arg())
        )

    def arg__non_recursive(self) -> FileMatcherArg:
        return fm_args.DirContents(
            fms_args.Selection(
                fm_args.Type(FileType.REGULAR),
                self.setup.num_files_arg())
        )
