import pathlib
from abc import ABC, abstractmethod
from typing import ContextManager, Iterator

from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, \
    MatcherAdv, MatcherWTrace
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.util.file_utils import TmpDirFileSpace


class StringMatcherModel(ABC):
    """
    Access to the string/file to check, with functionality designed to
    help assertions on the contents of the file.
    """

    @abstractmethod
    def with_transformation(self, string_transformer: StringTransformer) -> 'StringMatcherModel':
        pass

    @property
    @abstractmethod
    def string_transformer(self) -> StringTransformer:
        """
        :return: The string transformer that transforms the source of the model,
        before used for matching.
        """
        pass

    @abstractmethod
    def transformed_file_path(self, tmp_file_space: TmpDirFileSpace) -> pathlib.Path:
        """
        Gives a path to a file with contents that has been transformed using the transformer.
        """
        pass

    @abstractmethod
    def lines(self) -> ContextManager[Iterator[str]]:
        """
        Gives the lines of the file contents to check.

        Lines are generated each time this method is called,
        so if it is needed to iterate over them multiple times,
        it might be better to store the result in a file,
        using transformed_file_path.
        """
        pass


StringMatcher = MatcherWTrace[StringModel]

StringMatcherAdv = MatcherAdv[StringModel]

StringMatcherDdv = MatcherDdv[StringModel]

StringMatcherSdv = MatcherSdv[StringModel]
