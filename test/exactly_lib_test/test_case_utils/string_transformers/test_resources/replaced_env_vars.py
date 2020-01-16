import os

from exactly_lib.test_case_file_structure import tcds_symbols
from exactly_lib.test_case_file_structure.tcds import Tcds


class ReplacedEnvVarsFileContentsGeneratorWithAllReplacedVariables:
    """
    Generates contents with all environment variables that this program sets.
    Some of these variables _should_ be replaced by the replacement option, and some _should_not_.
    This assures that it is tested that only the correct variables are replaced.

    The contents is a bit contrived - to make the test check both a single value on a single line,
    and multiple values on a single line.
    """

    def __init__(self):
        self.sorted_env_var_keys = sorted(tcds_symbols.ALL_REPLACED_SYMBOLS)

    def contents_before_replacement(self, tcds: Tcds) -> str:
        env_vars_dict = tcds_symbols.replaced(tcds)
        values_in_determined_order = list(map(env_vars_dict.get, self.sorted_env_var_keys))
        return self._content_from_values(values_in_determined_order,
                                         tcds)

    def expected_contents_after_replacement(self, tcds: Tcds) -> str:
        return self._content_from_values(self.sorted_env_var_keys,
                                         tcds)

    def unexpected_contents_after_replacement(self, tcds: Tcds) -> str:
        """
        :return: Gives a variation of the expected result, that is not equal to the expected result.
        """
        return self._content_from_values(tuple(reversed(self.sorted_env_var_keys)),
                                         tcds)

    @staticmethod
    def _content_from_values(values_in_determined_order: iter,
                             tcds: Tcds) -> str:
        """
        Generates a string with a combination of values that should, and should not, be replaced.
        """
        all_values_concatenated = ''.join(values_in_determined_order)
        all_values_on_separate_lines = os.linesep.join(values_in_determined_order)
        all_values_concatenated_in_reverse_order = ''.join(reversed(values_in_determined_order))
        sds = tcds.sds
        should_not_be_replaced_values = os.linesep.join([str(sds.root_dir),
                                                         str(sds.result.root_dir)])
        return os.linesep.join([all_values_concatenated,
                                all_values_on_separate_lines,
                                all_values_concatenated_in_reverse_order,
                                should_not_be_replaced_values]) + os.linesep


class ReplacedEnvVarsFileContentsGeneratorForSubDirRelationshipBetweenHdsActAndCase:
    def __init__(self,
                 name_of_parent_dir__rel_hds_symbol: str,
                 name_of_sub_dir__rel_hds_symbol: str):
        self.name_of_parent_dir__rel_hds_symbol = name_of_parent_dir__rel_hds_symbol
        self.name_of_sub_dir__rel_hds_symbol = name_of_sub_dir__rel_hds_symbol

    """
    Generates contents where one of the rel-home environment variables (home/act, home/case)
    is a sub directory of the other.
    """

    def contents_before_replacement(self, tcds: Tcds) -> str:
        env_vars_dict = tcds_symbols.symbols_rel_hds(tcds.hds)

        just_some_stuff_that_should_not_be_replaced = str(tcds.sds.root_dir)

        ret_val = '\n'.join([
            env_vars_dict[self.name_of_parent_dir__rel_hds_symbol],
            just_some_stuff_that_should_not_be_replaced,
            env_vars_dict[self.name_of_sub_dir__rel_hds_symbol], ])
        return ret_val

    def expected_contents_after_replacement(self, tcds: Tcds) -> str:
        just_some_stuff_that_should_not_be_replaced = str(tcds.sds.root_dir)

        ret_val = '\n'.join([
            self.name_of_parent_dir__rel_hds_symbol,
            just_some_stuff_that_should_not_be_replaced,
            self.name_of_sub_dir__rel_hds_symbol,
        ])
        return ret_val

    def unexpected_contents_after_replacement(self, tcds: Tcds) -> str:
        """
        :return: Gives a variation of the expected result, that is not equal to the expected result.
        """
        env_vars_dict = tcds_symbols.symbols_rel_hds(tcds.hds)

        value_of_parent_dir = env_vars_dict[self.name_of_parent_dir__rel_hds_symbol]
        value_of_sub_dir = env_vars_dict[self.name_of_parent_dir__rel_hds_symbol]
        sub_dir_suffix_relative_the_parent_dir = value_of_sub_dir[len(value_of_parent_dir):]

        just_some_stuff_that_should_not_be_replaced = str(tcds.sds.root_dir)

        ret_val = '\n'.join([
            self.name_of_parent_dir__rel_hds_symbol + sub_dir_suffix_relative_the_parent_dir,
            just_some_stuff_that_should_not_be_replaced,
            self.name_of_parent_dir__rel_hds_symbol,
        ])
        return ret_val
