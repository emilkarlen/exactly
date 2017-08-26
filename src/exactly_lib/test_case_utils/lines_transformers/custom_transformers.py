from exactly_lib.test_case_utils.lines_transformers.env_vars_replacement import EnvVarReplacementLinesTransformer

ENV_VAR_REPLACEMENT_TRANSFORMER_NAME = 'env-var-replacement'

CUSTOM_LINES_TRANSFORMERS = {
    ENV_VAR_REPLACEMENT_TRANSFORMER_NAME: EnvVarReplacementLinesTransformer(ENV_VAR_REPLACEMENT_TRANSFORMER_NAME)
}
