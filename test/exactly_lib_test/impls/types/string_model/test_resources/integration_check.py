from typing import AbstractSet

from exactly_lib.impls.types.string_model import parse
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_prims.string_model import StringModel
from exactly_lib_test.impls.types.logic.test_resources import integration_check
from exactly_lib_test.type_val_deps.types.string_model.test_resources.properties_checker import \
    StringModelPropertiesConfiguration


def checker(accepted_file_relativities: AbstractSet[RelOptionType]
            ) -> integration_check.IntegrationChecker[StringModel, None, None]:
    return integration_check.IntegrationChecker(
        parse.StringModelParser(accepted_file_relativities),
        StringModelPropertiesConfiguration(),
        check_application_result_with_tcds=False,
    )


def checker__wo_file_relativities() -> integration_check.IntegrationChecker[StringModel, None, None]:
    return _CHECKER__WO_FILE_RELATIVITIES


_CHECKER__WO_FILE_RELATIVITIES = checker(set())
