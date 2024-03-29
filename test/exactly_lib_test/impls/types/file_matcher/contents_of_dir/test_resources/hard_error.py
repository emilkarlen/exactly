from exactly_lib.tcfs.path_relativity import RelSdsOptionType
from exactly_lib_test.impls.types.file_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.file_matcher.test_resources.integration_check import ModelConstructor
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Arrangement, arrangement_w_tcds, \
    ParseExpectation, ExecutionExpectation, Expectation
from exactly_lib_test.impls.types.matcher.test_resources import matchers
from exactly_lib_test.impls.types.test_resources import matcher_assertions as asrt_matcher
from exactly_lib_test.tcfs.test_resources import sds_populator
from exactly_lib_test.test_resources.files.file_structure import DirContents, Dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.files_matcher.test_resources.references import is_reference_to_files_matcher
from exactly_lib_test.type_val_deps.types.files_matcher.test_resources.symbol_context import FilesMatcherSymbolContext


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
                DirContents([Dir.empty(self.checked_dir_name)])
            ),
            symbols=FilesMatcherSymbolContext.of_primitive(
                self.files_matcher_name,
                matchers.MatcherThatReportsHardError(self.error_message)
            ).symbol_table,
        )

    def expectation(self) -> Expectation:
        return Expectation(
            ParseExpectation(
                symbol_references=asrt.matches_singleton_sequence(
                    is_reference_to_files_matcher(self.files_matcher_name)
                ),
            ),
            ExecutionExpectation(
                is_hard_error=asrt_matcher.is_hard_error(asrt.equals(self.error_message))
            )
        )
