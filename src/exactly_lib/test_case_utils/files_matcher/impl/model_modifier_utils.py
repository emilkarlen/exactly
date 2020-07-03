from typing import Sequence, Callable

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.matcher import property_matcher
from exactly_lib.test_case_utils.matcher.impls import property_matcher_describers
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetterSdv, PropertyGetterDdv, MODEL, T, \
    PropertyGetterAdv, PropertyGetter
from exactly_lib.type_system.description.structure_building import StructureBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.file_matcher import FileMatcherDdv, FileMatcher, FileMatcherAdv, \
    FileMatcherSdv
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, FilesMatcherSdv
from exactly_lib.util.description_tree import details
from exactly_lib.util.symbol_table import SymbolTable


class Configuration:
    def __init__(self,
                 name: str,
                 get_model: Callable[[FileMatcher, FilesMatcherModel], FilesMatcherModel],
                 ):
        self.name = name
        self.get_model = get_model


def matcher(configuration: Configuration,
            selector: FileMatcherSdv,
            matcher_on_result: FilesMatcherSdv) -> FilesMatcherSdv:
    return property_matcher.PropertyMatcherSdv(
        matcher_on_result,
        _PrunedModelGetterSdv(configuration, selector),
        property_matcher_describers.GetterWithMatcherAsChild(),
    )


class _ModelGetter(PropertyGetter[FilesMatcherModel, FilesMatcherModel],
                   WithCachedTreeStructureDescriptionBase):

    def __init__(self,
                 configuration: Configuration,
                 predicate: FileMatcher,
                 ):
        super().__init__()
        self._configuration = configuration
        self._predicate = predicate

    @staticmethod
    def new_structure_renderer(name: str, predicate: StructureRenderer) -> StructureRenderer:
        return (
            StructureBuilder(name)
                .append_details(details.Tree(predicate))
                .as_render()
        )

    def _structure(self) -> StructureRenderer:
        return self.new_structure_renderer(self._configuration.name, self._predicate.structure())

    def get_from(self, model: FilesMatcherModel) -> FilesMatcherModel:
        return self._configuration.get_model(self._predicate, model)


class _PrunedModelGetterAdv(PropertyGetterAdv[FilesMatcherModel, FilesMatcherModel]):
    def __init__(self,
                 configuration: Configuration,
                 predicate: FileMatcherAdv,
                 ):
        self._configuration = configuration
        self._predicate = predicate

    def applier(self, environment: ApplicationEnvironment) -> PropertyGetter[FilesMatcherModel, FilesMatcherModel]:
        return _ModelGetter(self._configuration,
                            self._predicate.primitive(environment))


class _PrunedModelGetterDdv(PropertyGetterDdv[FilesMatcherModel, FilesMatcherModel]):
    def __init__(self,
                 configuration: Configuration,
                 predicate: FileMatcherDdv,
                 ):
        self._configuration = configuration
        self._predicate = predicate

    def structure(self) -> StructureRenderer:
        return _ModelGetter.new_structure_renderer(self._configuration.name,
                                                   self._predicate.structure())

    @property
    def validator(self) -> DdvValidator:
        return self._predicate.validator

    def value_of_any_dependency(self, tcds: Tcds) -> PropertyGetterAdv[MODEL, T]:
        return _PrunedModelGetterAdv(self._configuration,
                                     self._predicate.value_of_any_dependency(tcds))


class _PrunedModelGetterSdv(PropertyGetterSdv[FilesMatcherModel, FilesMatcherModel]):
    def __init__(self,
                 configuration: Configuration,
                 predicate: FileMatcherSdv):
        self._configuration = configuration
        self._predicate = predicate

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._predicate.references

    def resolve(self, symbols: SymbolTable) -> PropertyGetterDdv[FilesMatcherModel, FilesMatcherModel]:
        return _PrunedModelGetterDdv(self._configuration,
                                     self._predicate.resolve(symbols))
