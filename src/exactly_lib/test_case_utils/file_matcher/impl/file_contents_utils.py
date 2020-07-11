from abc import ABC
from typing import Generic, Sequence, Callable, TypeVar

from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.definitions import matcher_model, misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity.syntax_elements import SyntaxElementInfo
from exactly_lib.processing import exit_values
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.sdv_structure import references_from_objects_with_symbol_references
from exactly_lib.test_case_file_structure import ddv_validators
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils import file_properties, path_check
from exactly_lib.test_case_utils.described_dep_val import LogicWithDetailsDescriptionSdv, LogicWithDetailsDescriptionDdv
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.file_matcher.impl.base_class import FileMatcherDdvImplBase, FileMatcherImplBase, \
    FileMatcherAdvImplBase
from exactly_lib.test_case_utils.file_matcher.impl.model_constructor import ModelConstructor
from exactly_lib.test_case_utils.matcher.impls import sdv_components
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.file_matcher import FileMatcherDdv, FileMatcherModel, FileMatcherSdv
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue
from exactly_lib.type_system.logic.matcher_base_class import MODEL, MatcherAdv, MatcherDdv, \
    MatcherWTrace
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class NamesSetup:
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


def _empty_sed_list() -> Sequence[SyntaxElementDescription]:
    return ()


class DocumentationSetup:
    def __init__(self,
                 names: NamesSetup,
                 options: Sequence[a.ArgumentUsage],
                 get_syntax_elements: Callable[[], Sequence[SyntaxElementDescription]] = _empty_sed_list,
                 ):
        self.names = names
        self.options = options
        self.get_syntax_elements = get_syntax_elements


CONTENTS_MATCHER_MODEL = TypeVar('CONTENTS_MATCHER_MODEL')


def sdv(
        names: NamesSetup,
        model_constructor: LogicWithDetailsDescriptionSdv[ModelConstructor[CONTENTS_MATCHER_MODEL]],
        contents_matcher: MatcherSdv[CONTENTS_MATCHER_MODEL],
) -> FileMatcherSdv:
    def make_ddv(symbols: SymbolTable) -> FileMatcherDdv:
        return _FileContentsMatcherDdv(names,
                                       model_constructor.resolve(symbols),
                                       contents_matcher.resolve(symbols))

    return sdv_components.MatcherSdvFromParts(
        references_from_objects_with_symbol_references((model_constructor,
                                                        contents_matcher)),
        make_ddv,
    )


class _FileContentsMatcher(FileMatcherImplBase,
                           Generic[CONTENTS_MATCHER_MODEL],
                           ABC):
    def __init__(self,
                 names: NamesSetup,
                 model_constructor: ModelConstructor[CONTENTS_MATCHER_MODEL],
                 contents_matcher: MatcherWTrace[CONTENTS_MATCHER_MODEL],
                 ):
        super().__init__()
        self._names = names
        self._model_constructor = model_constructor
        self._expected_file_check = file_properties.must_exist_as(names.accepted_file_type,
                                                                  follow_symlinks=True)
        self._contents_matcher = contents_matcher

    @property
    def name(self) -> str:
        return self._names.name

    def _structure(self) -> StructureRenderer:
        return _new_structure_tree(self.name,
                                   self._model_constructor.describer,
                                   self._contents_matcher)

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        self._hard_error_if_file_is_not_existing_of_expected_type(model)

        contents_matcher_model = self._model_constructor.make_model(model)
        contents_matcher_model_result = self._contents_matcher.matches_w_trace(contents_matcher_model)
        return (
            self._new_tb()
                .append_details(self._model_constructor.describer)
                .append_child(contents_matcher_model_result.trace)
                .build_result(contents_matcher_model_result.value)
        )

    def _hard_error_if_file_is_not_existing_of_expected_type(self, model: FileMatcherModel):
        mb_failure = path_check.failure_message_or_none(self._expected_file_check, model.path)
        if mb_failure:
            raise HardErrorException(mb_failure)


class _FileContentsMatcherAdv(FileMatcherAdvImplBase,
                              Generic[CONTENTS_MATCHER_MODEL],
                              ):
    def __init__(self,
                 names: NamesSetup,
                 model_constructor: ApplicationEnvironmentDependentValue[ModelConstructor[CONTENTS_MATCHER_MODEL]],
                 contents_matcher: MatcherAdv[CONTENTS_MATCHER_MODEL],
                 ):
        self._names = names
        self._model_constructor = model_constructor
        self._contents_matcher = contents_matcher

    def primitive(self, environment: ApplicationEnvironment) -> MatcherWTrace[MODEL]:
        return _FileContentsMatcher(self._names,
                                    self._model_constructor.primitive(environment),
                                    self._contents_matcher.primitive(environment))


class _FileContentsMatcherDdv(FileMatcherDdvImplBase):
    def __init__(self,
                 names: NamesSetup,
                 model_constructor: LogicWithDetailsDescriptionDdv[ModelConstructor[CONTENTS_MATCHER_MODEL]],
                 contents_matcher: MatcherDdv[CONTENTS_MATCHER_MODEL],
                 ):
        self._names = names
        self._model_constructor = model_constructor
        self._contents_matcher = contents_matcher
        self._validators = ddv_validators.all_of((model_constructor.validator,
                                                  contents_matcher.validator))

    def structure(self) -> StructureRenderer:
        return _new_structure_tree(
            self._names.name,
            self._model_constructor.describer,
            self._contents_matcher,
        )

    @property
    def validator(self) -> DdvValidator:
        return self._validators

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        return _FileContentsMatcherAdv(self._names,
                                       self._model_constructor.value_of_any_dependency(tcds),
                                       self._contents_matcher.value_of_any_dependency(tcds))


class FileContentsSyntaxDescription(grammar.PrimitiveExpressionDescriptionWithNameAsInitialSyntaxToken):
    def __init__(self, documentation: DocumentationSetup):
        self._documentation = documentation

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        matcher_arguments = [
            a.Single(a.Multiplicity.MANDATORY,
                     self._documentation.names.contents_matcher_syntax_element.argument)
        ]
        return list(self._documentation.options) + matcher_arguments

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        tp = TextParser({
            '_file_type_': file_properties.TYPE_INFO[self._documentation.names.accepted_file_type].name,
            '_matcher_type_': self._documentation.names.contents_matcher_syntax_element.singular_name,
            'HARD_ERROR': exit_values.EXECUTION__HARD_ERROR.exit_identifier,
            'MODEL': matcher_model.FILE_MATCHER_MODEL,
            'SYMBOLIC_LINKS_ARE_FOLLOWED': misc_texts.SYMBOLIC_LINKS_ARE_FOLLOWED,
        })

        ret_val = tp.fnap(_FILE_CONTENTS_MATCHER_HEADER_DESCRIPTION)
        ret_val += tp.fnap(MATCHER_FILE_HANDLING_DESCRIPTION)

        return ret_val

    @property
    def syntax_elements(self) -> Sequence[SyntaxElementDescription]:
        return self._documentation.get_syntax_elements()

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return cross_reference_id_list([
            self._documentation.names.contents_matcher_syntax_element,
        ])


def _new_structure_tree(name: str,
                        options: DetailsRenderer,
                        contents_matcher: MatcherWTrace) -> StructureRenderer:
    return renderers.NodeRendererFromParts(
        name,
        None,
        (options,),
        (contents_matcher.structure(),),
    )


_FILE_CONTENTS_MATCHER_HEADER_DESCRIPTION = """\
Matches {_file_type_:s} who's contents satisfies {_matcher_type_}.
"""

MATCHER_FILE_HANDLING_DESCRIPTION = """\
The result is {HARD_ERROR} for {MODEL:a} that is not {_file_type_:a}.

{SYMBOLIC_LINKS_ARE_FOLLOWED}.
"""
