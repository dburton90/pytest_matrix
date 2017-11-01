

class PytestMatrixException(Exception):
    pass


class FixturesCombinationsMissing(PytestMatrixException):
    def __init__(self, class_name, function_name):
        from .mixin import MatrixTestBase
        function_name = function_name.upper()
        msg = "Missing in {function_name}{MatrixTestBase.FIXTURE_SUFFIX} in testing class '{class_name}'"
        super().__init__(msg.format_map(vars()))


class InvalidFixturesCombinationsKeys(PytestMatrixException):

    def __init__(self, class_name, function_name, expected, extra, missing):
        from .mixin import MatrixTestBase
        expected = ", ".join(expected)
        extra = ', '.join(extra)
        missing = ', '.join(missing)
        function_name = function_name.upper()
        msg = ("In testing class '{class_name}' in {function_name}_{MatrixTestBase.FIXTURE_SUFFIX} was "
               "incorrect keys:\nExpected: ")
        if extra:
            msg += "Extra: " + extra + '\n'
        if missing:
            msg += "Missing: " + missing

        super().__init__(msg.format_map(vars()))
