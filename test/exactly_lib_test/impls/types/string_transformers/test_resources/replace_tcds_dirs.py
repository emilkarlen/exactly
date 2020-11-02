import os

from exactly_lib.tcfs import tcds_symbols
from exactly_lib.tcfs.tcds import TestCaseDs


class ReplacedSymbolsFileContentsGeneratorWithAllReplacedVariables:
    """
    Generates contents with all paths with a corresponding path symbol, and some more SDS paths.
    Some of these variables _should_ be replaced by the replacement option, and some _should_not_.
    This assures that it is tested that only the correct variables are replaced.

    The contents is a bit contrived - to make the test check both a single value on a single line,
    and multiple values on a single line.
    """

    def __init__(self):
        self.sorted_symbol_keys = sorted(tcds_symbols.ALL_REPLACED_SYMBOLS)

    def contents_before_replacement(self, tcds: TestCaseDs) -> str:
        symbols_dict = tcds_symbols.replaced(tcds)
        values_in_determined_order = list(map(symbols_dict.get, self.sorted_symbol_keys))
        return self._content_from_values(values_in_determined_order,
                                         tcds)

    def expected_contents_after_replacement(self, tcds: TestCaseDs) -> str:
        return self._content_from_values(self.sorted_symbol_keys,
                                         tcds)

    def unexpected_contents_after_replacement(self, tcds: TestCaseDs) -> str:
        """
        :return: Gives a variation of the expected result, that is not equal to the expected result.
        """
        return self._content_from_values(tuple(reversed(self.sorted_symbol_keys)),
                                         tcds)

    @staticmethod
    def _content_from_values(values_in_determined_order: iter,
                             tcds: TestCaseDs) -> str:
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


class ReplacedSymbolsFileContentsGeneratorForSubDirRelationshipBetweenHdsActAndCase:
    def __init__(self,
                 name_of_parent_dir__rel_hds_symbol: str,
                 name_of_sub_dir__rel_hds_symbol: str):
        self.name_of_parent_dir__rel_hds_symbol = name_of_parent_dir__rel_hds_symbol
        self.name_of_sub_dir__rel_hds_symbol = name_of_sub_dir__rel_hds_symbol

    """
    Generates contents where one of the rel-home symbols (home/act, home/case)
    is a sub directory of the other.
    """

    def contents_before_replacement(self, tcds: TestCaseDs) -> str:
        symbols_dict = tcds_symbols.symbols_rel_hds(tcds.hds)

        just_some_stuff_that_should_not_be_replaced = str(tcds.sds.root_dir)

        ret_val = '\n'.join([
            symbols_dict[self.name_of_parent_dir__rel_hds_symbol],
            just_some_stuff_that_should_not_be_replaced,
            symbols_dict[self.name_of_sub_dir__rel_hds_symbol], ])
        return ret_val

    def expected_contents_after_replacement(self, tcds: TestCaseDs) -> str:
        just_some_stuff_that_should_not_be_replaced = str(tcds.sds.root_dir)

        ret_val = '\n'.join([
            self.name_of_parent_dir__rel_hds_symbol,
            just_some_stuff_that_should_not_be_replaced,
            self.name_of_sub_dir__rel_hds_symbol,
        ])
        return ret_val

    def unexpected_contents_after_replacement(self, tcds: TestCaseDs) -> str:
        """
        :return: Gives a variation of the expected result, that is not equal to the expected result.
        """
        symbols_dict = tcds_symbols.symbols_rel_hds(tcds.hds)

        value_of_parent_dir = symbols_dict[self.name_of_parent_dir__rel_hds_symbol]
        value_of_sub_dir = symbols_dict[self.name_of_parent_dir__rel_hds_symbol]
        sub_dir_suffix_relative_the_parent_dir = value_of_sub_dir[len(value_of_parent_dir):]

        just_some_stuff_that_should_not_be_replaced = str(tcds.sds.root_dir)

        ret_val = '\n'.join([
            self.name_of_parent_dir__rel_hds_symbol + sub_dir_suffix_relative_the_parent_dir,
            just_some_stuff_that_should_not_be_replaced,
            self.name_of_parent_dir__rel_hds_symbol,
        ])
        return ret_val
