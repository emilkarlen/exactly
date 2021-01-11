import unittest
from typing import Sequence, Callable

from exactly_lib.type_val_deps.envs.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, \
    Expectation, ParseExpectation
from exactly_lib_test.impls.types.matcher.test_resources.matcher_w_init_action import MatcherWInitialAction
from exactly_lib_test.impls.types.string_matcher.test_resources import integration_check, \
    arguments_building2 as args2
from exactly_lib_test.impls.types.string_matcher.test_resources.arguments_building2 import StringMatcherArg
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.test_resources.string_matcher import StringMatcherSymbolContext
from exactly_lib_test.type_val_prims.matcher.test_resources import matching_result
from exactly_lib_test.type_val_prims.string_source.test_resources import properties_access
from exactly_lib_test.type_val_prims.string_source.test_resources.string_source_base import StringSourceTestImplBase
from exactly_lib_test.type_val_prims.string_source.test_resources.string_source_contents import \
    StringSourceContentsFromLines


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestThatInfixOperatorsFreezesTheModel),
    ])


class TestThatInfixOperatorsFreezesTheModel(unittest.TestCase):
    def test_conjunction(self):
        self._check(
            operand_result=True,
            mk_expr=args2.conjunction,
        )

    def test_disjunction(self):
        self._check(
            operand_result=False,
            mk_expr=args2.disjunction,
        )

    def _check(self,
               operand_result: bool,
               mk_expr: Callable[[Sequence[StringMatcherArg]], StringMatcherArg],
               ):
        # ARRANGE #
        operand_that_accesses_model_contents = StringMatcherSymbolContext.of_primitive(
            'ACCESSES_MODEL_CONTENTS',
            matcher_that_accesses_contents_and_gives_constant(operand_result),
        )
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_FULL.check(
            self,
            mk_expr(
                [
                    args2.SymbolReference(operand_that_accesses_model_contents.name),
                    args2.SymbolReference(operand_that_accesses_model_contents.name)
                ]
            ).as_remaining_source,
            MakeModelWithContentsOnlyAccessibleAfterFreeze(self).construct,
            arrangement_w_tcds(
                symbols=operand_that_accesses_model_contents.symbol_table,
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.len_equals(2)
                )
            ),
        )


def matcher_that_accesses_contents_and_gives_constant(result: bool) -> MatcherWTrace[StringSource]:
    return MatcherWInitialAction(
        properties_access.get_string_source_contents,
        matching_result.of(result)
    )


class MakeModelWithContentsOnlyAccessibleAfterFreeze:
    def __init__(self, put: unittest.TestCase):
        self._put = put

    def construct(self, environment: FullResolvingEnvironment) -> StringSource:
        return _StringSourceWithContentsOnlyAccessibleAfterFreeze(
            put=self._put,
            is_frozen=False,
            contents=StringSourceContentsFromLines(
                (),
                environment.application_environment.tmp_files_space,
                False,
            )
        )


class _StringSourceWithContentsOnlyAccessibleAfterFreeze(StringSourceTestImplBase):
    def __init__(self,
                 put: unittest.TestCase,
                 is_frozen: bool,
                 contents: StringSourceContents,
                 ):
        super().__init__()
        self._put = put
        self._is_frozen = is_frozen
        self._contents = contents

    def freeze(self):
        self._is_frozen = True

    def contents(self) -> StringSourceContents:
        self._put.assertTrue(self._is_frozen,
                             'string source must be frozen when contents is accessed')

        return self._contents


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
