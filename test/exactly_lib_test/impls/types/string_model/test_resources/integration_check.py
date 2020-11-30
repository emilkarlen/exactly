from exactly_lib.impls.types.path.rel_opts_configuration import RelOptionsConfiguration
from exactly_lib.impls.types.string_model import parse
from exactly_lib.type_val_prims.string_model.string_model import StringModel
from exactly_lib_test.impls.types.logic.test_resources import integration_check
from exactly_lib_test.impls.types.string_model.test_resources import parse_check
from exactly_lib_test.type_val_deps.types.string_model.test_resources.properties_checker import \
    StringModelPropertiesConfiguration


def checker(accepted_file_relativities: RelOptionsConfiguration
            ) -> integration_check.IntegrationChecker[StringModel, None, None]:
    return integration_check.IntegrationChecker(
        parse.StringModelParser(accepted_file_relativities),
        StringModelPropertiesConfiguration(),
        check_application_result_with_tcds=False,
    )


def checker__w_arbitrary_file_relativities() -> integration_check.IntegrationChecker[StringModel, None, None]:
    return _CHECKER__W_ARBITRARY_FILE_RELATIVITIES


_CHECKER__W_ARBITRARY_FILE_RELATIVITIES = checker(parse_check.ARBITRARY_FILE_RELATIVITIES)
