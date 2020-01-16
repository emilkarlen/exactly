from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Sequence

from exactly_lib.definitions import matcher_model
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity.syntax_elements import SyntaxElementInfo
from exactly_lib.processing import exit_values
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils import file_properties, path_check
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.file_matcher.impl.base_class import FileMatcherDdvImplBase, FileMatcherImplBase, \
    FileMatcherAdvImplBase
from exactly_lib.test_case_utils.files_matcher.new_model_impl import FilesMatcherModelForDir
from exactly_lib.test_case_utils.matcher.impls import sdv_components
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic import files_matcher
from exactly_lib.type_system.logic.file_matcher import FileMatcherDdv, FileMatcherModel, FileMatcherSdvType
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, ApplicationEnvironment, \
    MatcherWTraceAndNegation, MODEL, MatcherAdv, MatcherDdv
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser

CONTENTS_MATCHER_MODEL = TypeVar('CONTENTS_MATCHER_MODEL')


class Setup(Generic[CONTENTS_MATCHER_MODEL], ABC):
    def __init__(self,
                 primitive_name: str,
                 accepted_file_type: file_properties.FileType,
                 contents_matcher_syntax_element: SyntaxElementInfo,
                 ):
        self.primitive_name = primitive_name
        self.accepted_file_type = accepted_file_type
        self.contents_matcher_syntax_element = contents_matcher_syntax_element
        self.name = ' '.join((primitive_name,
                              contents_matcher_syntax_element.singular_name)
                             )

    @abstractmethod
    def make_model(self, model: FileMatcherModel) -> CONTENTS_MATCHER_MODEL:
        pass


def sdv__generic(
        setup: Setup[CONTENTS_MATCHER_MODEL],
        contents_matcher: MatcherSdv[CONTENTS_MATCHER_MODEL],
) -> FileMatcherSdvType:
    def make_ddv(symbols: SymbolTable) -> FileMatcherDdv:
        contents_matcher_ddv = contents_matcher.resolve(symbols)
        return _FileContentsMatcherDdv(setup, contents_matcher_ddv)

    return sdv_components.MatcherSdvFromParts(
        contents_matcher.references,
        make_ddv,
    )


class _FileContentsMatcher(FileMatcherImplBase,
                           Generic[CONTENTS_MATCHER_MODEL],
                           ABC):
    def __init__(self,
                 setup: Setup[CONTENTS_MATCHER_MODEL],
                 contents_matcher: MatcherWTraceAndNegation[CONTENTS_MATCHER_MODEL],
                 ):
        super().__init__()
        self._setup = setup
        self._expected_file_check = file_properties.must_exist_as(setup.accepted_file_type,
                                                                  follow_symlinks=True)
        self._contents_matcher = contents_matcher

    @property
    def name(self) -> str:
        return self._setup.name

    def _structure(self) -> StructureRenderer:
        return _new_structure_tree(self.name,
                                   self._contents_matcher)

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        self._hard_error_if_file_is_not_existing_of_expected_type(model)

        contents_matcher_model = self._setup.make_model(model)
        contents_matcher_model_result = self._contents_matcher.matches_w_trace(contents_matcher_model)
        return (
            self._new_tb()
                .append_child(contents_matcher_model_result.trace)
                .build_result(contents_matcher_model_result.value)
        )

    def _hard_error_if_file_is_not_existing_of_expected_type(self, model: FileMatcherModel):
        mb_failure = path_check.failure_message_or_none(self._expected_file_check, model.path)
        if mb_failure:
            raise HardErrorException(mb_failure)

    @staticmethod
    def _files_matcher_model(model: FileMatcherModel) -> files_matcher.FilesMatcherModel:
        return FilesMatcherModelForDir(
            model.path,
            None,
        )


class _FileContentsMatcherAdv(FileMatcherAdvImplBase,
                              Generic[CONTENTS_MATCHER_MODEL],
                              ):
    def __init__(self,
                 setup: Setup[CONTENTS_MATCHER_MODEL],
                 contents_matcher: MatcherAdv[CONTENTS_MATCHER_MODEL],
                 ):
        self._setup = setup
        self._contents_matcher = contents_matcher

    def applier(self, environment: ApplicationEnvironment) -> MatcherWTraceAndNegation[MODEL]:
        return _FileContentsMatcher(self._setup,
                                    self._contents_matcher.applier(environment))


class _FileContentsMatcherDdv(FileMatcherDdvImplBase):
    def __init__(self,
                 setup: Setup[CONTENTS_MATCHER_MODEL],
                 contents_matcher: MatcherDdv[CONTENTS_MATCHER_MODEL],
                 ):
        self._setup = setup
        self._contents_matcher = contents_matcher

    def structure(self) -> StructureRenderer:
        return _new_structure_tree(
            self._setup.name,
            self._contents_matcher,
        )

    @property
    def validator(self) -> DdvValidator:
        return self._contents_matcher.validator

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        return _FileContentsMatcherAdv(self._setup,
                                       self._contents_matcher.value_of_any_dependency(tcds))


class FileContentsSyntaxDescription(grammar.SimpleExpressionDescription):
    def __init__(self, setup: Setup):
        self._setup = setup

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            a.Single(a.Multiplicity.MANDATORY,
                     self._setup.contents_matcher_syntax_element.argument)
        ]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        tp = TextParser({
            '_file_type_': file_properties.TYPE_INFO[self._setup.accepted_file_type].name,
            '_matcher_type_': self._setup.contents_matcher_syntax_element.singular_name,
            'HARD_ERROR': exit_values.EXECUTION__HARD_ERROR.exit_identifier,
            'MODEL': matcher_model.FILE_MATCHER_MODEL,
        })
        return tp.fnap(_FILE_CONTENTS_MATCHER_SED_DESCRIPTION)

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return cross_reference_id_list([
            self._setup.contents_matcher_syntax_element,
        ])


def _new_structure_tree(name: str, contents_matcher: MatcherWTraceAndNegation) -> StructureRenderer:
    return renderers.NodeRendererFromParts(
        name,
        None,
        (),
        (contents_matcher.structure(),),
    )


_FILE_CONTENTS_MATCHER_SED_DESCRIPTION = """\
Matches {_file_type_:s} who's contents satisfies {_matcher_type_}.


The result is {HARD_ERROR} for {MODEL:a} that is not {_file_type_:a}.
"""
