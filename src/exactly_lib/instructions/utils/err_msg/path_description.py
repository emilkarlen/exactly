from exactly_lib.instructions.utils.err_msg import property_description
from exactly_lib.symbol.path_resolver import FileRefResolver
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep


class PathValueDescriptor(property_description.ErrorMessagePartConstructor):
    def __init__(self, path_resolver: FileRefResolver):
        self.path_resolver = path_resolver

    def lines(self, environment: InstructionEnvironmentForPostSdsStep) -> list:
        path = self.path_resolver.resolve_value_of_any_dependency(
            environment.path_resolving_environment_pre_or_post_sds)
        return [str(path)]


def path_value_description(property_name: str,
                           path_resolver: FileRefResolver) -> property_description.PropertyDescriptor:
    return property_description.PropertyDescriptorWithConstantPropertyName(
        property_name,
        PathValueDescriptor(path_resolver),
    )
