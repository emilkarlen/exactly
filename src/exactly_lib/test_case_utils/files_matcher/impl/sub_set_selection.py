from typing import Sequence

from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.symbol.logic.file_matcher import FileMatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.matcher import property_matcher
from exactly_lib.test_case_utils.matcher.impls import property_matcher_describers
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetterSdv, PropertyGetterDdv, MODEL, T, \
    PropertyGetterAdv, PropertyGetter
from exactly_lib.type_system.description.structure_building import StructureBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.file_matcher import FileMatcherDdv, FileMatcher, FileMatcherAdv
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, FilesMatcherSdvType
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.description_tree import details
from exactly_lib.util.symbol_table import SymbolTable


def sub_set_selection_matcher(selector: FileMatcherSdv,
                              matcher_on_selection: FilesMatcherSdvType) -> FilesMatcherSdvType:
    return property_matcher.PropertyMatcherSdv(
        matcher_on_selection,
        _SubsetGetterSdv(selector),
        property_matcher_describers.GetterWithMatcherAsChild(),
    )


class _SubsetGetter(PropertyGetter[FilesMatcherModel, FilesMatcherModel],
                    WithCachedTreeStructureDescriptionBase):
    NAME = ' '.join([
        option_syntax.option_syntax(instruction_arguments.SELECTION_OPTION.name),
        syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.singular_name,
    ])

    @staticmethod
    def new_structure_renderer(predicate: StructureRenderer) -> StructureRenderer:
        return (
            StructureBuilder(_SubsetGetter.NAME)
                .append_details(details.Tree(predicate))
                .as_render()
        )

    def __init__(self, predicate: FileMatcher):
        super().__init__()
        self._predicate = predicate

    def _structure(self) -> StructureRenderer:
        return self.new_structure_renderer(self._predicate.structure())

    def get_from(self, model: FilesMatcherModel) -> FilesMatcherModel:
        return model.sub_set(self._predicate)


class _SubsetGetterAdv(PropertyGetterAdv[FilesMatcherModel, FilesMatcherModel]):
    def __init__(self, predicate: FileMatcherAdv):
        self._predicate = predicate

    def applier(self, environment: ApplicationEnvironment) -> PropertyGetter[FilesMatcherModel, FilesMatcherModel]:
        return _SubsetGetter(self._predicate.applier(environment))


class _SubsetGetterDdv(PropertyGetterDdv[FilesMatcherModel, FilesMatcherModel]):
    def __init__(self, predicate: FileMatcherDdv):
        self._predicate = predicate

    def structure(self) -> StructureRenderer:
        return _SubsetGetter.new_structure_renderer(self._predicate.structure())

    @property
    def validator(self) -> DdvValidator:
        return self._predicate.validator

    def value_of_any_dependency(self, tcds: Tcds) -> PropertyGetterAdv[MODEL, T]:
        return _SubsetGetterAdv(self._predicate.value_of_any_dependency(tcds))


class _SubsetGetterSdv(PropertyGetterSdv[FilesMatcherModel, FilesMatcherModel]):
    def __init__(self, predicate: FileMatcherSdv):
        self._predicate = predicate

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._predicate.references

    def resolve(self, symbols: SymbolTable) -> PropertyGetterDdv[FilesMatcherModel, FilesMatcherModel]:
        return _SubsetGetterDdv(self._predicate.resolve(symbols))
