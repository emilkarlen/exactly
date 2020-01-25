from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.files_matcher import is_reference_to_files_matcher__ref
from exactly_lib_test.test_case_file_structure.test_resources import sds_populator
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.file_matcher.test_resources.integration_check import ModelConstructor
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import Arrangement, arrangement_w_tcds, \
    Expectation, ParseExpectation, ExecutionExpectation
from exactly_lib_test.test_case_utils.test_resources import matcher_assertions as asrt_matcher
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class HardErrorDueToHardErrorFromFilesMatcherHelper:
    def __init__(self,
                 files_matcher_name: str = 'the_files_matcher',
                 checked_dir_location: RelSdsOptionType = RelSdsOptionType.REL_TMP,
                 checked_dir_name: str = 'checked-dir',
                 error_message: str = 'the hard error message',
                 ):
        self.files_matcher_name = files_matcher_name
        self.checked_dir_location = checked_dir_location
        self.checked_dir_name = checked_dir_name
        self.error_message = error_message

    def model_constructor(self) -> ModelConstructor:
        return integration_check.file_in_sds(self.checked_dir_location,
                                             self.checked_dir_name)

    def arrangement(self) -> Arrangement:
        return arrangement_w_tcds(
            non_hds_contents=sds_populator.contents_in(
                self.checked_dir_location,
                DirContents([empty_dir(self.checked_dir_name)])
            ),
            symbols=symbol_utils.symbol_table_from_name_and_sdv_mapping({
                self.files_matcher_name:
                    FilesMatcherSdv(matchers.sdv_from_primitive_value(
                        matchers.MatcherThatReportsHardError(self.error_message)
                    ))
            }),
        )

    def expectation(self) -> Expectation:
        return Expectation(
            ParseExpectation(
                symbol_references=asrt.matches_singleton_sequence(
                    is_reference_to_files_matcher__ref(self.files_matcher_name)
                ),
            ),
            ExecutionExpectation(
                is_hard_error=asrt_matcher.is_hard_error(asrt.equals(self.error_message))
            )
        )
