import pytest
import re

from pytest_matrix import TestMatrixMixin, exceptions


def test_generate(testdir):

    # create a temporary pytest test file
    source = """
    import pytest
    from pytest_matrix import TestMatrixMixin
    
    def my_func(a, b):    
        return a + b
    
    class TestSuite(TestMatrixMixin):
        def test_my_fn(self, arg_first, arg_second, result):
            assert my_func(arg_first, arg_second) == result

        MY_FN_FIXTURES_NAMES = ['arg_first']
        MY_FN_FIXTURES = [
            {
                'arg_first': ['val_a', 'val_b'],
            }
        ]

        @pytest.fixture
        def arg_first_val_a(self):
            return 'val_1'

        @pytest.fixture
        def arg_first_val_b(self):
            return 'val_2'

        @pytest.fixture
        def arg_second(self):
            return 'val'

        @pytest.fixture
        def result(self, arg_first, arg_second):
            return arg_first + arg_second
    """
    testdir.makepyfile(source)
    result = testdir.runpytest()

    result.assert_outcomes(passed=2)

    expected_functions = {
        'test_my_fn[arg_first_val_a]',
        'test_my_fn[arg_first_val_b]',
    }
    items = testdir.getitems(source)
    collected_tests = {f.name for f in items}

    assert expected_functions == collected_tests


def test_generate_from_marker(testdir):

    # create a temporary pytest test file
    source = """
    import pytest
    from pytest_matrix import TestMatrixMixin
    
    
    def my_func(a, b):    
        return a + b
    
    @pytest.mark.matrix(names=['arg_first'], combs=[
            {
                'arg_first': ['val_a', 'val_b']
            }
        ])
    def test_my_fn(arg_first, arg_second, result):
        assert my_func(arg_first, arg_second) == result

    @pytest.fixture
    def arg_first_val_a():
        return 'val_1'

    @pytest.fixture
    def arg_first_val_b():
        return 'val_2'

    @pytest.fixture
    def arg_second():
        return 'val'

    @pytest.fixture
    def result(arg_first, arg_second):
        return arg_first + arg_second
    """
    testdir.makepyfile(source)
    result = testdir.runpytest()

    result.assert_outcomes(passed=2)

    expected_functions = {
        'test_my_fn[arg_first_val_a]',
        'test_my_fn[arg_first_val_b]',
    }
    items = testdir.getitems(source)
    collected_tests = {f.name for f in items}

    assert expected_functions == collected_tests




def test_missing_fixture_names():
    with pytest.raises(exceptions.FixturesNamesMissing):
        class Test(TestMatrixMixin):

            FN_FIXTURES = [{'x': ['x']}]

            def test_fn(self):
                pass


def test_missing_fixtures_definition():
    with pytest.raises(exceptions.FixturesCombinationsMissing):
        class Test(TestMatrixMixin):

            FN_FIXTURES_NAMES = ['x']

            def test_fn(self):
                pass


def test_missing_fixture_names_inherited():
    with pytest.raises(exceptions.FixturesNamesMissing):
        class TestMixin(TestMatrixMixin):
            IS_MIXIN = True

            def test_fn(self):
                pass

        class Test(TestMixin):
            FN_FIXTURES = [{'x': ['x']}]


def test_missing_fixtures_definition_inherited():
    with pytest.raises(exceptions.FixturesCombinationsMissing):
        class TestMixin(TestMatrixMixin):
            IS_MIXIN = True

            def test_fn(self):
                pass

        class Test(TestMixin):
            FN_FIXTURES_NAMES = ['x']


@pytest.mark.parametrize(argnames='names', ids=['more', 'less'],
                         argvalues=[['a', 'b', 'c'], ['a']])
def test_invalid_fixtures_keys(names):
    with pytest.raises(exceptions.InvalidFixturesCombinationsKeys):
        class Test(TestMatrixMixin):

            FN_FIXTURES_NAMES = names
            FN_FIXTURES = [
                {
                    'a': ['a'],
                    'b': ['b'],
                }
            ]

            def test_fn(self):
                pass


def test_not_generate(testdir):
    source = """
    import pytest
    from pytest_matrix import TestMatrixMixin

    class TestMixin(TestMatrixMixin):
        IS_MIXIN = True
        FN_FIXTURES = [{'x': ['x']}]
        FN_FIXTURES_NAMES = ['x']

        def test_fn(self):
            pass

    class TestFirst(TestMixin):
        NOT_GENERATE_TESTS = ['test_fn']
        
    class TestOtherTest(TestFirst):
        FN_FIXTURES = [{'y': ['x']}]
        FN_FIXTURES_NAMES = ['y']
        
        @pytest.fixture
        def y_x(self):
            pass
    """
    testdir.makepyfile(source)
    result = testdir.runpytest()

    result.assert_outcomes(passed=2)

    items = testdir.getitems(source)
    assert {(f.name, f.cls.__name__) for f in items} == {('test_fn[y_x]', 'TestOtherTest'),
                                                         ('test_fn', "TestFirst")}


def test_skip(testdir):
    source = """
    import pytest
    from pytest_matrix import TestMatrixMixin

    class TestMixin(TestMatrixMixin):
        IS_MIXIN = True
        FN_FIXTURES = [{'x': ['x']}]
        FN_FIXTURES_NAMES = ['x']

        def test_fn(self):
            pass

    class TestFirst(TestMixin):
        SKIP_TESTS = ['test_fn']
        
    class TestOtherTest(TestFirst):
        FN_FIXTURES = [{'y': ['x']}]
        FN_FIXTURES_NAMES = ['y']
        
        @pytest.fixture
        def y_x(self):
            pass
    """
    path = testdir.makepyfile(source)
    result = testdir.runpytest("{path}".format_map(vars()))

    result.assert_outcomes(skipped=1, passed=1)

    items = testdir.getitems(source)
    assert {(f.name, f.cls.__name__) for f in items} == {('test_fn[y_x]', 'TestOtherTest'),
                                                         ('test_fn', "TestFirst")}



