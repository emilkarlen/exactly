from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.string_transformer.impl.models import transformed_by_program
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.program.program import Program
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.type_system.logic.string_transformer import StringTransformer


def transformer(name: str,
                environment: ApplicationEnvironment,
                ignore_exit_code: bool,
                program: Program,
                structure: StructureRenderer,
                ) -> StringTransformer:
    return _RunStringTransformer(
        name,
        environment,
        ignore_exit_code,
        program,
        structure,
    )


class _RunStringTransformer(WithCachedTreeStructureDescriptionBase, StringTransformer):
    def __init__(self,
                 name: str,
                 environment: ApplicationEnvironment,
                 ignore_exit_code: bool,
                 program: Program,
                 structure: StructureRenderer,
                 ):
        super().__init__()
        self._name = name
        self._environment = environment
        self._ignore_exit_code = ignore_exit_code
        self._program = program
        self._structure = structure

    @property
    def name(self) -> str:
        return self._name

    def _structure(self) -> StructureRenderer:
        return self._structure

    def transform(self, model: StringModel) -> StringModel:
        return transformed_by_program.transformed_by_program(
            self._program,
            self._ignore_exit_code,
            self._environment,
            model,
        )
