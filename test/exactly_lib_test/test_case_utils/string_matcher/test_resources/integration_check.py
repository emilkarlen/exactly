import pathlib
from typing import Callable

from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.test_case_utils.string_matcher import parse_string_matcher
from exactly_lib.test_case_utils.string_transformer.impl.identity import IdentityStringTransformer
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.string_matcher import DestinationFilePathGetter
from exactly_lib.type_system.logic.string_matcher import StringMatcherModel
from exactly_lib.util.file_utils import TmpDirFileSpaceAsDirCreatedOnDemand, TmpDirFileSpace
from exactly_lib_test.test_case_utils.logic.test_resources import integration_check
from exactly_lib_test.test_case_utils.matcher.test_resources import integration_check as matcher_integration_check
from exactly_lib_test.test_case_utils.matcher.test_resources.matcher_checker import \
    MatcherPropertiesConfiguration
from exactly_lib_test.type_system.data.test_resources import described_path

ModelConstructor = Callable[[FullResolvingEnvironment], StringMatcherModel]


def empty_model() -> ModelConstructor:
    return model_of('')


def model_of(contents: str) -> ModelConstructor:
    return _ModelConstructorHelper(contents).construct


def model_that_must_not_be_used(environment: FullResolvingEnvironment) -> StringMatcherModel:
    return MODEL_THAT_MUST_NOT_BE_USED


MODEL_THAT_MUST_NOT_BE_USED = StringMatcherModel(described_path.new_primitive(pathlib.Path('non-existing-file')),
                                                 IdentityStringTransformer(),
                                                 DestinationFilePathGetter(),
                                                 )


class _ModelConstructorHelper:
    def __init__(self,
                 contents: str,
                 ):
        self.contents = contents

    def construct(self, environment: FullResolvingEnvironment) -> StringMatcherModel:
        tmp_dir_file_space = TmpDirFileSpaceAsDirCreatedOnDemand(environment.tcds.sds.internal_tmp_dir)
        original_file_path = self._create_original_file(tmp_dir_file_space)

        return StringMatcherModel(
            original_file_path,
            IdentityStringTransformer(),
            DestinationFilePathGetter(),
        )

    def _create_original_file(self, file_space: TmpDirFileSpace) -> DescribedPath:
        original_file_path = file_space.new_path()

        with original_file_path.open(mode='w') as f:
            f.write(self.contents)

        return described_path.new_primitive(original_file_path)


ARBITRARY_MODEL = empty_model()


def constant_model(model: StringMatcherModel) -> ModelConstructor:
    return matcher_integration_check.constant_model(model)


CHECKER = integration_check.IntegrationChecker(
    parse_string_matcher.string_matcher_parser(),
    MatcherPropertiesConfiguration()
)
