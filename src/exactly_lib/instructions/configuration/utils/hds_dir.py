import pathlib

from exactly_lib.common.help.abs_or_rel_path import abs_or_rel_path_of_existing
from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.help_texts import formatting, instruction_arguments
from exactly_lib.help_texts.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.help_texts.entity import concepts
from exactly_lib.help_texts.entity.conf_params import ConfigurationParameterInfo
from exactly_lib.instructions.configuration.utils.single_arg_utils import single_eq_invokation_variants
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.phases.result import sh


class DirConfParamInstructionDocumentationBase(InstructionDocumentationWithTextParserBase):
    def __init__(self,
                 name: str,
                 conf_param: ConfigurationParameterInfo):
        self.conf_param = conf_param
        super().__init__(name, {
            'conf_param': formatting.conf_param_(conf_param),
            'DIR': _DIR_ARG.name,
        })

    def single_line_description(self) -> str:
        return self._format('Sets the {conf_param} directory')

    def invokation_variants(self) -> list:
        return single_eq_invokation_variants(_DIR_ARG)

    def syntax_element_descriptions(self) -> list:
        return [
            SyntaxElementDescription(_DIR_ARG.name,
                                     abs_or_rel_path_of_existing('directory',
                                                                 _DIR_ARG.name,
                                                                 'current ' + formatting.conf_param_(self.conf_param))),
        ]

    def see_also_targets(self) -> list:
        return cross_reference_id_list([
            self.conf_param,
            concepts.HOME_DIRECTORY_STRUCTURE_CONCEPT_INFO,
        ])


_DIR_ARG = instruction_arguments.DIR_WITHOUT_RELATIVITY_OPTIONS_ARGUMENT


class InstructionBase(ConfigurationPhaseInstruction):
    def __init__(self, argument: str):
        self.argument = argument

    def main(self, configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        new_path = self._new_path(configuration_builder)
        if not new_path.exists():
            return sh.new_sh_hard_error('Directory does not exist: {}'.format(new_path))
        if not new_path.is_dir():
            return sh.new_sh_hard_error('Not a directory: {}'.format(new_path))
        self._set_conf_param_dir(configuration_builder, new_path.resolve())
        return sh.new_sh_success()

    def _new_path(self,
                  configuration_builder: ConfigurationBuilder) -> pathlib.Path:
        delta = pathlib.Path(self.argument)
        if delta.is_absolute():
            return delta
        return self._get_conf_param_dir(configuration_builder) / delta

    def _get_conf_param_dir(self, configuration_builder: ConfigurationBuilder) -> pathlib.Path:
        raise NotImplementedError('abstract method')

    def _set_conf_param_dir(self,
                            configuration_builder: ConfigurationBuilder,
                            path: pathlib.Path):
        raise NotImplementedError('abstract method')
