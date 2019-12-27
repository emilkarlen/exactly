import contextlib
from typing import Iterator

from exactly_lib.definitions import actual_file_attributes
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import files_matcher as files_matcher_primitives
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.err_msg import property_description
from exactly_lib.test_case_utils.file_matcher.file_matcher_models import FileMatcherModelForDescribedPath
from exactly_lib.test_case_utils.matcher.impls import quantifier_matchers
from exactly_lib.test_case_utils.string_transformer.impl.identity import IdentityStringTransformer
from exactly_lib.type_system.data import path_description
from exactly_lib.type_system.err_msg.prop_descr import PropertyDescriptor, FilePropertyDescriptorConstructor
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.files_matcher import FileModel, FilesMatcherModel
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment
from exactly_lib.type_system.logic.string_matcher import DestinationFilePathGetter
from exactly_lib.util.description_tree.renderer import DetailsRenderer


class _FilePropertyDescriptorConstructorForFileInDir(FilePropertyDescriptorConstructor):
    def __init__(self, file_in_dir: FileModel):
        self._file_in_dir = file_in_dir

    def construct_for_contents_attribute(self,
                                         contents_attribute: str) -> PropertyDescriptor:
        return path_description.path_value_description(
            property_description.file_property_name(contents_attribute,
                                                    actual_file_attributes.PLAIN_FILE_OBJECT_NAME),
            self._file_in_dir.path.describer,
            True,
        )


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
