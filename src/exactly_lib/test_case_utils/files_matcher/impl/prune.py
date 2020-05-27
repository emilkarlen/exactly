from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.test_case_utils.files_matcher import config
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherSdv
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, FilesMatcherSdv
from exactly_lib.util.cli_syntax import option_syntax
from . import model_modifier_utils


def matcher(dir_selector: FileMatcherSdv,
            matcher_on_result: FilesMatcherSdv) -> FilesMatcherSdv:
    return model_modifier_utils.matcher(
        _CONFIGURATION,
        dir_selector,
        matcher_on_result,
    )


def _get_model(dir_selector: FileMatcher, model: FilesMatcherModel) -> FilesMatcherModel:
    return model.prune(dir_selector)


_CONFIGURATION = model_modifier_utils.Configuration(
    ' '.join([
        option_syntax.option_syntax(config.PRUNE_OPTION.name),
        syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.singular_name,
        syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.singular_name,
    ]),
    _get_model,
)
