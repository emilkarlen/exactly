from exactly_lib.impls.description_tree.tree_structured import WithCachedNodeDescriptionBase
from exactly_lib.impls.types.string_transformer.impl.sources import transformed_by_program
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_transformer import StringTransformer


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


class _RunStringTransformer(WithCachedNodeDescriptionBase, StringTransformer):
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

    def transform(self, model: StringSource) -> StringSource:
        return transformed_by_program.transformed_by_program(
            self._name,
            self._program,
            self._ignore_exit_code,
            self._environment,
            model,
        )
