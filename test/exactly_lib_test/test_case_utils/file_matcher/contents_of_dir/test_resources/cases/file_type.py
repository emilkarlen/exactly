import pathlib
import unittest
from typing import Sequence, Optional, List, Callable

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangement
from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir.test_resources.case_generator import \
    SingleCaseGenerator, ExecutionResult, RESULT__MATCHES
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as fm_args, file_type_tests
from exactly_lib_test.test_case_utils.file_matcher.test_resources.argument_building import FileMatcherArg
from exactly_lib_test.test_case_utils.files_matcher.models.test_resources import model_checker
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as fms_args
from exactly_lib_test.test_resources.files.file_structure import FileSystemElement
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def file_type_detection__recursive__depth_0() -> Sequence[NameAndValue[SingleCaseGenerator]]:
    return [
        NameAndValue(
            str(file_type),
            _TestTypeTypeDetection(
                file_type,
                fm_args.DirContentsRecursiveArgs,
                file_type_tests.ALL_TYPES_OF_FILES__DEPTH_0,
                file_type_tests.EXPECTED__DEPTH_0[file_type],
            )
        )
        for file_type in FileType
    ]


def file_type_detection__recursive__depth_1() -> Sequence[NameAndValue[SingleCaseGenerator]]:
    return [
        NameAndValue(
            str(file_type),
            _TestTypeTypeDetection(
                file_type,
                fm_args.DirContentsRecursiveArgs,
                file_type_tests.ACTUAL__RECURSIVE__DEPTH_1,
                file_type_tests.EXPECTED__DEPTH_1[file_type],
            )
        )
        for file_type in FileType
    ]


def file_type_detection__non_recursive() -> Sequence[NameAndValue[SingleCaseGenerator]]:
    return [
        NameAndValue(
            str(file_type),
            _TestTypeTypeDetection(
                file_type,
                lambda x: x,
                file_type_tests.ALL_TYPES_OF_FILES__DEPTH_0,
                [
                    pathlib.Path(file_name)
                    for file_name in file_type_tests.EXPECTED__DEPTH_0[file_type]
                ],
            )
        )
        for file_type in FileType
    ]


class _TestTypeTypeDetection(SingleCaseGenerator):
    def __init__(self,
                 type_to_detect: FileType,
                 mk_arguments_from_selection: Callable[[fms_args.Selection], FileMatcherArg],
                 checked_dir_contents: List[FileSystemElement],
                 expected: List[pathlib.Path],
                 ):
        super().__init__()
        self._type_to_detect = type_to_detect
        self._mk_arguments_from_selection = mk_arguments_from_selection
        self._checked_dir_contents = checked_dir_contents
        self._expected = expected

    def arguments(self) -> FileMatcherArg:
        return self._mk_arguments_from_selection(
            fms_args.Selection(
                fm_args.Type(self._type_to_detect),
                self._helper.files_matcher_sym_ref_arg()
            )
        )

    def symbols(self, put: unittest.TestCase) -> SymbolTable:
        return SymbolTable({
            self.files_matcher_name:
                model_checker.matcher__sym_tbl_container(put,
                                                         self._helper.model_file_path(),
                                                         self._expected,
                                                         )
        })

    def tcds_arrangement(self) -> Optional[TcdsArrangement]:
        return self._helper.tcds_arrangement_for_contents_of_checked_dir(
            self._checked_dir_contents,
        )

    def expected_symbols(self) -> Sequence[ValueAssertion[SymbolReference]]:
        return [
            self._helper.files_matcher_sym_assertion(),
        ]

    def execution_result(self) -> ExecutionResult:
        return RESULT__MATCHES
