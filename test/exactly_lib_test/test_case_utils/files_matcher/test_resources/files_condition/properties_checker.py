import unittest
from pathlib import PurePosixPath

from exactly_lib.symbol.logic.logic_type_sdv import LogicSdv
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.test_case_utils.files_matcher.files_condition import FilesCondition, FilesConditionSdv, \
    FilesConditionDdv
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib_test.test_case_utils.logic.test_resources.common_properties_checker import \
    CommonPropertiesConfiguration, Applier, CommonSdvPropertiesChecker
from exactly_lib_test.test_case_utils.logic.test_resources.logic_type_checker import \
    WithDetailsDescriptionExecutionPropertiesChecker
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_system.logic.test_resources.file_matcher import FileMatcherModelThatMustNotBeAccessed


class FilesConditionPropertiesConfiguration(
    CommonPropertiesConfiguration[FilesCondition,
                                  PurePosixPath,
                                  MatchingResult]):
    def __init__(self):
        self._applier = _Applier()

    def applier(self) -> Applier[FilesCondition, PurePosixPath, MatchingResult]:
        return self._applier

    def new_sdv_checker(self) -> CommonSdvPropertiesChecker[FilesCondition]:
        return _SdvPropertiesChecker()

    def new_execution_checker(self) -> WithDetailsDescriptionExecutionPropertiesChecker:
        return WithDetailsDescriptionExecutionPropertiesChecker(FilesConditionDdv, FilesCondition)


class _SdvPropertiesChecker(CommonSdvPropertiesChecker[FilesCondition]):
    def check(self,
              put: unittest.TestCase,
              actual: LogicSdv[FilesCondition],
              message_builder: MessageBuilder,
              ):
        asrt.is_instance(FilesConditionSdv).apply(
            put,
            actual,
            message_builder
        )


class _Applier(Applier[FilesCondition, PurePosixPath, MatchingResult]):
    """
    Test fails if the files-condition does not contain the tested path,
    or if it has no associated file-matcher.

    A dummy file-matcher model is used.
    """

    def apply(self,
              put: unittest.TestCase,
              message_builder: MessageBuilder,
              primitive: FilesCondition,
              resolving_environment: FullResolvingEnvironment,
              input_: PurePosixPath) -> MatchingResult:
        file_matcher = self._associated_file_matcher(put, message_builder, input_, primitive)
        return file_matcher.matches_w_trace(FileMatcherModelThatMustNotBeAccessed())

    @staticmethod
    def _associated_file_matcher(put,
                                 message_builder,
                                 file: PurePosixPath,
                                 primitive: FilesCondition,
                                 ) -> FileMatcher:
        files = primitive.files
        if file not in files:
            put.fail(
                message_builder.apply(
                    'Test impl error: the files-condition does not contain path {}'.format(file)
                )
            )
        mb_fm = files[file]
        if mb_fm is None:
            put.fail(
                message_builder.apply(
                    'Test impl error: the files-condition does not have an associated files matcher: {}'.format(file)
                )
            )
        return mb_fm
