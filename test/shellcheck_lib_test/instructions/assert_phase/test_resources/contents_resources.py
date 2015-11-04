import os

from shellcheck_lib.execution import environment_variables
from shellcheck_lib_test.instructions.assert_phase.test_resources.instruction_check import ActResultProducer


class ActResultProducerForContentsWithAllEnvVarsBase(ActResultProducer):
    def __init__(self):
        super().__init__()
        self.sorted_env_var_keys = sorted(environment_variables.ALL_ENV_VARS)

    @property
    def expected_contents_after_replacement(self) -> str:
        return self._content_from_values(self.sorted_env_var_keys)

    @property
    def unexpected_contents_after_replacement(self) -> str:
        """
        :return: Gives a variation of the expected result, that is not equal to the expected result.
        """
        return self._content_from_values(tuple(reversed(self.sorted_env_var_keys)))

    @staticmethod
    def _content_from_values(values_in_determined_order: iter) -> str:
        all_values_concatenated = ''.join(values_in_determined_order)
        all_values_on_separate_lines = os.linesep.join(values_in_determined_order)
        all_values_concatenated_in_reverse_order = ''.join(reversed(values_in_determined_order))
        return os.linesep.join([all_values_concatenated,
                                all_values_on_separate_lines,
                                all_values_concatenated_in_reverse_order]) + os.linesep
