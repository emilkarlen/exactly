import contextlib
from typing import Iterator

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.types.files_matcher import config
from exactly_lib.impls.types.matcher.impls import quantifier_matchers
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcherModel
from exactly_lib.type_val_prims.matcher.files_matcher import FilesMatcherModel
from exactly_lib.util.description_tree.renderer import DetailsRenderer


def _element_detail_renderer(element: FileMatcherModel) -> DetailsRenderer:
    return custom_details.path_primitive_details_renderer(element.path.describer)


@contextlib.contextmanager
def _file_elements_from_model(tcds: TestCaseDs,
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
        syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT,
        _element_detail_renderer,
    ),
    _file_elements_from_model,
)
