import unittest

from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.util import symbol_table
from exactly_lib_test.test_case_file_structure.test_resources.application_environment import \
    application_environment_for_test
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_case_utils.string_transformers.test_resources import transformer_checker, model_construction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.string_transformer.test_resources import string_transformers
from exactly_lib_test.type_system.logic.test_resources.string_models import StringModelThatMustNotBeUsed


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestApplier),
    ])


class TestApplier(unittest.TestCase):
    def test_model_SHOULD_be_evaluated_so_that_failures_from_evaluation_are_detected(self):
        # ARRANGE #
        sut = transformer_checker._Applier()
        resolving_env = FullResolvingEnvironment(
            symbol_table.empty_symbol_table(),
            fake_tcds(),
            application_environment_for_test(),
        )
        transformer_that_raises = string_transformers.model_access_raises_hard_error()
        # ACT & ASSERT #
        with self.assertRaises(HardErrorException):
            sut.apply(
                self,
                asrt.MessageBuilder.new_empty(),
                transformer_that_raises,
                resolving_env,
                model_construction.constant(StringModelThatMustNotBeUsed()),
            )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
