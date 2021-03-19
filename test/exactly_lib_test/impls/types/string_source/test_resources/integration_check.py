from typing import Callable

from exactly_lib.impls.types.string_source import parse
from exactly_lib.type_val_deps.types.path.rel_opts_configuration import RelOptionsConfiguration
from exactly_lib.type_val_deps.types.string_source.ddv import StringSourceAdv
from exactly_lib.type_val_deps.types.string_source.sdv import StringSourceSdv
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib_test.impls.types.logic.test_resources import integration_check
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Arrangement, AssertionResolvingEnvironment, \
    ExecutionExpectation, adv_asrt__any, prim_asrt__any
from exactly_lib_test.impls.types.string_source.test_resources import parse_check
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.dep_variants.test_resources.full_deps import execution_check
from exactly_lib_test.type_val_deps.types.string_source.test_resources.properties_checker import \
    StringSourcePropertiesConfiguration


def checker(accepted_file_relativities: RelOptionsConfiguration
            ) -> integration_check.IntegrationChecker[StringSource, None, None]:
    return integration_check.IntegrationChecker(
        parse.string_source_parser(accepted_file_relativities),
        StringSourcePropertiesConfiguration(),
        check_application_result_with_tcds=False,
    )


def primitive__const(const: Assertion[StringSource],
                     ) -> Callable[[AssertionResolvingEnvironment], Assertion[StringSource]]:
    def ret_val(env: AssertionResolvingEnvironment) -> Assertion[StringSource]:
        return const

    return ret_val


def execution_assertion(
        arrangement: Arrangement,
        execution: ExecutionExpectation[None] = ExecutionExpectation(),
        primitive: Callable[[AssertionResolvingEnvironment], Assertion[StringSource]] = prim_asrt__any,
        adv: Callable[[AssertionResolvingEnvironment], Assertion[StringSourceAdv]] = adv_asrt__any,
) -> Assertion[StringSourceSdv]:
    return execution_check.ExecutionAssertion(
        None,
        arrangement,
        adv,
        primitive,
        execution,
        _PROPERTIES_CONFIGURATION.applier(),
        _PROPERTIES_CONFIGURATION.new_execution_checker(),
        check_application_result_with_tcds=False,
    )


_PROPERTIES_CONFIGURATION = StringSourcePropertiesConfiguration()


def checker__w_arbitrary_file_relativities() -> integration_check.IntegrationChecker[StringSource, None, None]:
    return _CHECKER__W_ARBITRARY_FILE_RELATIVITIES


_CHECKER__W_ARBITRARY_FILE_RELATIVITIES = checker(parse_check.ARBITRARY_FILE_RELATIVITIES)
