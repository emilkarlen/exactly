from abc import ABC, abstractmethod
from typing import Sequence

from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.condition.comparators import ComparisonOperator
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib_test.test_case_file_structure.test_resources import sds_populator
from exactly_lib_test.test_case_utils.condition.integer.test_resources.arguments_building import int_condition
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.test_case_utils.file_matcher.test_resources.argument_building import FileMatcherArg
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as fms_args
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import FilesMatcherArg
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import ExecutionExpectation, \
    Arrangement, arrangement_w_tcds
from exactly_lib_test.test_resources.files.file_structure import FileSystemElement, empty_file, Dir, DirContents
from exactly_lib_test.test_resources.test_utils import NEA, NExArr
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result


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
                empty_file('a-file'),
                Dir('a-dir',
                    [empty_file('a-file-in-a-dir')]
                    ),
            ]
        ),
        NEA(
            'not match',
            False,
            [
                Dir('a-dir',
                    [empty_file('a-file-in-dir')]
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
                empty_file('file-1'),
                Dir('a-dir',
                    [empty_file('a-file-in-a-dir')]
                    ),
            ]
        ),
        NEA(
            'not match',
            False,
            [
                Dir('a-dir',
                    [empty_file('a-file-in-dir')]
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
                empty_file('a-file'),
                Dir('a-dir',
                    [empty_file('a-file-in-a-dir')]
                    ),
            ]
        ),
        NEA(
            'not match',
            False,
            [
                empty_file('a-file'),
                empty_file('another-file'),
                Dir('a-dir',
                    [empty_file('a-file-in-dir')]
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
                empty_file('a-file'),
                Dir('a-dir',
                    [empty_file('a-file-in-a-dir')]
                    ),
            ]
        ),
        NEA(
            'not match',
            False,
            [
                empty_file('file-1'),
                empty_file('file-2'),
                Dir('a-dir',
                    [empty_file('file-in-dir')]
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
        pass

    @abstractmethod
    def arg__non_recursive(self) -> FileMatcherArg:
        pass

    def execution_cases(self) -> Sequence[NExArr[ExecutionExpectation, Arrangement]]:
        return [
            NExArr(
                case.name,
                ExecutionExpectation(
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
