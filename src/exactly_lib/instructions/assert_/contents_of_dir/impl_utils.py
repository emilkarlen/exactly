from typing import Sequence

from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.instructions.utils.logic_type_resolving_helper import resolving_helper_for_instruction_env
from exactly_lib.symbol import sdv_validation
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.logic.resolving_helper import resolving_helper__of_full_env
from exactly_lib.symbol.sdv_structure import SymbolReference, references_from_objects_with_symbol_references
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_file_structure import ddv_validators
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_utils import file_properties, pfh_exception as pfh_ex_method
from exactly_lib.test_case_utils import path_check
from exactly_lib.test_case_utils.described_dep_val import LogicWithDescriberSdv
from exactly_lib.test_case_utils.description_tree import bool_trace_rendering
from exactly_lib.test_case_utils.err_msg import path_err_msgs, file_or_dir_contents_headers
from exactly_lib.test_case_utils.file_matcher.file_matcher_models import FileMatcherModelForDescribedPath
from exactly_lib.test_case_utils.file_matcher.impl.file_contents_utils import ModelConstructor
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, FilesMatcherSdv
from exactly_lib.type_system.logic.hard_error import HardErrorException
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
            raise pfh_ex_method.PfhHardErrorException(failure_message)
        else:
            return files_source


class FilesMatcherAsDirContentsAssertionPart(AssertionPart[FilesSource, FilesSource]):
    def __init__(self,
                 model_constructor: LogicWithDescriberSdv[ModelConstructor[FilesMatcherModel]],
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
              custom_environment,
              files_source: FilesSource) -> FilesSource:

        path_to_check = (
            files_source.path_of_dir.resolve(environment.symbols)
                .value_of_any_dependency__d(environment.tcds)
        )

        helper = resolving_helper_for_instruction_env(environment)

        model = self._get_model(environment, path_to_check)

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

    def _get_model(self,
                   environment: InstructionEnvironmentForPostSdsStep,
                   dir_to_check: DescribedPath,
                   ) -> FilesMatcherModel:
        constructor = resolving_helper__of_full_env(environment.full_resolving_environment).resolve_logic_w_describer(
            self._model_constructor
        )
        return constructor.make_model(FileMatcherModelForDescribedPath(dir_to_check))
