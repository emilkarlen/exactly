import os

from exactly_lib.execution import environment_variables
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds


class ReplacedEnvVarsFileContentsGenerator:
    """
    Generates contents with all environment variables that this program sets.
    Some of these variables _should_ be replaced by the replacement option, and some _should_not_.
    This assures that it is tested that only the correct variables are replaced.

    The contents is a bit contrived - to make the test check both a single value on a single line,
    and multiple values on a single line.
    """
    def __init__(self):
        self.sorted_env_var_keys = sorted(environment_variables.ALL_REPLACED_ENV_VARS)

    def contents_before_replacement(self, home_and_sds: HomeAndSds) -> str:
        env_vars_dict = environment_variables.replaced(home_and_sds.hds,
                                                       home_and_sds.sds)
        values_in_determined_order = list(map(env_vars_dict.get, self.sorted_env_var_keys))
        return self._content_from_values(values_in_determined_order,
                                         home_and_sds)

    def expected_contents_after_replacement(self, home_and_sds: HomeAndSds) -> str:
        return self._content_from_values(self.sorted_env_var_keys,
                                         home_and_sds)

    def unexpected_contents_after_replacement(self, home_and_sds: HomeAndSds) -> str:
        """
        :return: Gives a variation of the expected result, that is not equal to the expected result.
        """
        return self._content_from_values(tuple(reversed(self.sorted_env_var_keys)),
                                         home_and_sds)

    @staticmethod
    def _content_from_values(values_in_determined_order: iter,
                             home_and_sds: HomeAndSds) -> str:
        """
        Generates a string with a combination of values that should, and should not, be replaced.
        """
        all_values_concatenated = ''.join(values_in_determined_order)
        all_values_on_separate_lines = os.linesep.join(values_in_determined_order)
        all_values_concatenated_in_reverse_order = ''.join(reversed(values_in_determined_order))
        sds = home_and_sds.sds
        should_not_be_replaced_values = os.linesep.join([str(sds.root_dir),
                                                         str(sds.result.root_dir)])
        return os.linesep.join([all_values_concatenated,
                                all_values_on_separate_lines,
                                all_values_concatenated_in_reverse_order,
                                should_not_be_replaced_values]) + os.linesep
