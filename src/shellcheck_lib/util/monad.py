def map_m(success_result, argument, functions: iter):
    for function in functions:
        result = function(argument)
        if result != success_result:
            return result
    return success_result
