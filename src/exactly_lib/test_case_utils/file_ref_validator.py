from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.err_msg2.described_path import DescribedPathPrimitive
from exactly_lib.test_case_utils.err_msg2.path_impl import described_path_resolvers


class FileRefValidatorBase(PreOrPostSdsValidator):
    """
    Validates existence of the resolved path of a `FileRef`.
    """

    def __init__(self,
                 file_ref_resolver: FileRefResolver):
        self._file_ref_resolver = file_ref_resolver

    def _validate_path(self, path: DescribedPathPrimitive) -> Optional[TextRenderer]:
        """
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[TextRenderer]:
        described_path_value = described_path_resolvers.of(self._file_ref_resolver) \
            .resolve__with_unknown_cd(environment.symbols)

        if described_path_value.value.exists_pre_sds():
            return self._validate_path(described_path_value.value_pre_sds(environment.hds))
        return None

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
        described_path_value = described_path_resolvers.of(self._file_ref_resolver) \
            .resolve__with_cwd_as_cd(environment.symbols)

        if not described_path_value.value.exists_pre_sds():
            return self._validate_path(described_path_value.value_post_sds__wo_hds(environment.sds))
        return None
