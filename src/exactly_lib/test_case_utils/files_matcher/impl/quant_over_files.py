import contextlib
from typing import Iterator

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.files_matcher import config
from exactly_lib.test_case_utils.matcher.impls import quantifier_matchers
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel
from exactly_lib.util.description_tree.renderer import DetailsRenderer


def _element_detail_renderer(element: FileMatcherModel) -> DetailsRenderer:
    return custom_details.path_primitive_details_renderer(element.path.describer)


@contextlib.contextmanager
def _file_elements_from_model(tcds: Tcds,
                              environment: ApplicationEnvironment,
                              model: FilesMatcherModel
                              ) -> Iterator[FileMatcherModel]:
    yield (
        file_element.as_file_matcher_model()
        for file_element in model.files()
    )


ELEMENT_SETUP = quantifier_matchers.ElementSetup(
    quantifier_matchers.ElementRendering(
        config.QUANTIFICATION_OVER_FILE_ARGUMENT,
        syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.singular_name,
        _element_detail_renderer,
    ),
    _file_elements_from_model,
)
