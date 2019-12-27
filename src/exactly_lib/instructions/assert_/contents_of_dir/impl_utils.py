from typing import Sequence

from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.instructions.utils.logic_type_resolving_helper import resolving_helper_for_instruction_env
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.validation import sdv_validation
from exactly_lib.test_case_utils import file_properties, pfh_exception as pfh_ex_method
from exactly_lib.test_case_utils import path_check
from exactly_lib.test_case_utils.description_tree import bool_trace_rendering
from exactly_lib.test_case_utils.err_msg import path_err_msgs, file_or_dir_contents_headers
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.files_matcher.new_model_impl import FilesMatcherModelForDir
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.util.render import combinators as rend_comb


class FilesSource:
    def __init__(self,
                 path_of_dir: PathSdv):
        self._path_of_dir = path_of_dir

    @property
    def path_of_dir(self) -> PathSdv:
        return self._path_of_dir


class AssertPathIsExistingDirectory(AssertionPart[FilesSource, FilesSource]):
    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              custom_environment,
              files_source: FilesSource) -> FilesSource:
        expect_existing_dir = file_properties.must_exist_as(file_properties.FileType.DIRECTORY,
                                                            True)

        path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        failure_message = path_check.pre_or_post_sds_failure_message_or_none(
            path_check.PathCheck(files_source.path_of_dir,
                                 expect_existing_dir),
            path_resolving_env)
        if failure_message is not None:
            raise pfh_ex_method.PfhFailException(failure_message)
        else:
            return files_source


class FilesMatcherAsDirContentsAssertionPart(AssertionPart[FilesSource, FilesSource]):
    def __init__(self, files_matcher: FilesMatcherSdv):
        super().__init__(sdv_validation.SdvValidatorFromDdvValidator(
            lambda symbols: files_matcher.resolve(symbols).validator
        ))
        self._files_matcher = files_matcher

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._files_matcher.references

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              custom_environment,
              files_source: FilesSource) -> FilesSource:

        path_to_check = (
            files_source.path_of_dir.resolve(environment.symbols)
                .value_of_any_dependency__d(environment.tcds)
        )

        helper = resolving_helper_for_instruction_env(environment)
        model = FilesMatcherModelForDir(path_to_check)
        matcher = helper.resolve_files_matcher(self._files_matcher)
        try:
            result = matcher.matches_w_trace(model)
            if not result.value:
                raise pfh_ex_method.PfhFailException(
                    rend_comb.SequenceR([
                        path_err_msgs.line_header_block__primitive(
                            file_or_dir_contents_headers.unexpected_of_file_type(FileType.DIRECTORY),
                            path_to_check.describer,
                        ),
                        bool_trace_rendering.BoolTraceRenderer(result.trace),
                    ]
                    )
                )

            return files_source
        except HardErrorException as ex:
            raise pfh_ex_method.PfhHardErrorException(ex.error)
