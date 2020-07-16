from typing import Sequence

from exactly_lib.common.report_rendering.description_tree import rendering__node_bool
from exactly_lib.definitions.test_case import file_check_properties
from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.instructions.utils.logic_type_resolving_helper import resolving_helper_for_instruction_env
from exactly_lib.symbol import sdv_validation
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.sdv_structure import SymbolReference, references_from_objects_with_symbol_references
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_file_structure import ddv_validators
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_utils import file_properties, pfh_exception as pfh_ex_method
from exactly_lib.test_case_utils import path_check
from exactly_lib.test_case_utils.described_dep_val import LogicWithDetailsDescriptionSdv
from exactly_lib.test_case_utils.err_msg import path_err_msgs, file_or_dir_contents_headers
from exactly_lib.test_case_utils.file_matcher.file_matcher_models import FileMatcherModelForDescribedPath
from exactly_lib.test_case_utils.file_matcher.impl.model_constructor import ModelConstructor
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, FilesMatcherSdv
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.symbol_table import SymbolTable


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
              files_source: FilesSource) -> FilesSource:
        expect_existing_dir = file_properties.must_exist_as(file_properties.FileType.DIRECTORY,
                                                            True)

        path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        failure_message = path_check.pre_or_post_sds_failure_message_or_none(
            path_check.PathCheck(files_source.path_of_dir,
                                 expect_existing_dir),
            path_resolving_env)
        if failure_message is not None:
            raise pfh_ex_method.PfhHardErrorException(failure_message)
        else:
            return files_source


class FilesMatcherAsDirContentsAssertionPart(AssertionPart[FilesSource, FilesSource]):
    def __init__(self,
                 model_constructor: LogicWithDetailsDescriptionSdv[ModelConstructor[FilesMatcherModel]],
                 files_matcher: FilesMatcherSdv,
                 ):
        def get_ddv_validator(symbols: SymbolTable) -> DdvValidator:
            return ddv_validators.all_of([
                model_constructor.resolve(symbols).validator,
                files_matcher.resolve(symbols).validator,
            ])

        super().__init__(sdv_validation.SdvValidatorFromDdvValidator(
            get_ddv_validator
        ))
        self._model_constructor = model_constructor
        self._files_matcher = files_matcher
        self._references = references_from_objects_with_symbol_references([
            model_constructor,
            files_matcher,
        ])

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              files_source: FilesSource) -> FilesSource:

        path_to_check = (
            files_source.path_of_dir.resolve(environment.symbols)
                .value_of_any_dependency__d(environment.tcds)
        )

        helper = resolving_helper_for_instruction_env(os_services, environment)
        model_constructor = self._resolve_model_constructor(os_services, environment)
        model = self._get_model(model_constructor, path_to_check)

        matcher = helper.resolve_files_matcher(self._files_matcher)
        try:
            result = matcher.matches_w_trace(model)
            if not result.value:
                final_result = self._final_result_of(model_constructor, result)
                raise pfh_ex_method.PfhFailException(
                    rend_comb.SequenceR([
                        path_err_msgs.line_header_block__primitive(
                            file_or_dir_contents_headers.unexpected_of_file_type(FileType.DIRECTORY),
                            path_to_check.describer,
                        ),
                        rendering__node_bool.BoolTraceRenderer(final_result.trace),
                    ]
                    )
                )

            return files_source
        except HardErrorException as ex:
            raise pfh_ex_method.PfhHardErrorException(ex.error)

    @staticmethod
    def _final_result_of(model_constructor: ModelConstructor[FilesMatcherModel],
                         matcher: MatchingResult) -> MatchingResult:
        tb = TraceBuilder(file_check_properties.DIR_CONTENTS)
        tb.append_details(model_constructor.describer)
        tb.append_child(matcher.trace)
        return tb.build_result(matcher.value)

    def _resolve_model_constructor(self,
                                   os_services: OsServices,
                                   environment: InstructionEnvironmentForPostSdsStep,
                                   ) -> ModelConstructor[FilesMatcherModel]:
        resolver = resolving_helper_for_instruction_env(os_services, environment)
        return resolver.resolve_logic_w_describer(
            self._model_constructor
        )

    @staticmethod
    def _get_model(model_constructor: ModelConstructor[FilesMatcherModel],
                   dir_to_check: DescribedPath,
                   ) -> FilesMatcherModel:
        return model_constructor.make_model(FileMatcherModelForDescribedPath(dir_to_check))
