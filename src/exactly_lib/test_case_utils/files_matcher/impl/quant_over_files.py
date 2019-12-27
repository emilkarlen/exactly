import contextlib
from typing import Iterator

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import files_matcher as files_matcher_primitives
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.file_matcher.file_matcher_models import FileMatcherModelForDescribedPath
from exactly_lib.test_case_utils.matcher.impls import quantifier_matchers
from exactly_lib.test_case_utils.string_transformer.impl.identity import IdentityStringTransformer
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.files_matcher import FileModel, FilesMatcherModel
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment
from exactly_lib.type_system.logic.string_matcher import DestinationFilePathGetter
from exactly_lib.util.description_tree.renderer import DetailsRenderer


def _element_detail_renderer(element: FileMatcherModel) -> DetailsRenderer:
    return custom_details.path_primitive_details_renderer(element.path.describer)


class _ModelsFactory:
    def __init__(self):
        self._id_trans = IdentityStringTransformer()
        self._destination_file_path_getter = DestinationFilePathGetter()

    def file_matcher_model(self, file_element: FileModel) -> FileMatcherModel:
        return FileMatcherModelForDescribedPath(file_element.path)


@contextlib.contextmanager
def _file_elements_from_model(tcds: Tcds,
                              environment: ApplicationEnvironment,
                              model: FilesMatcherModel
                              ) -> Iterator[FileMatcherModel]:
    model_factory = _ModelsFactory()
    yield (
        model_factory.file_matcher_model(file_element)
        for file_element in model.files()
    )


ELEMENT_SETUP = quantifier_matchers.ElementSetup(
    quantifier_matchers.ElementRendering(
        files_matcher_primitives.QUANTIFICATION_OVER_FILE_ARGUMENT,
        syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.singular_name,
        _element_detail_renderer,
    ),
    _file_elements_from_model,
)
