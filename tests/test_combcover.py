import pytest
import re

from pytest_matrix import TestMatrixMixin, exceptions


@pytest.fixture
def combination_test_mixin():
    class TestCombinations(TestMatrixMixin):
        IS_MIXIN = True

        def test_fn(self):
            pass

        @pytest.fixture
        def x_a(self):
            pass

        @pytest.fixture
        def x_b(self):
            pass

        @pytest.fixture
        def y_c(self):
            pass

        @pytest.fixture
        def y_d(self):
            pass

        def test_fx(self):
            pass

        @pytest.fixture
        def z_j(self):
            pass

        @pytest.fixture
        def z_k(self):
            pass
    return TestCombinations


def test_combination_function_passed(combination_test_mixin):

    class TestMyTest(combination_test_mixin):
        FN_FIXTURES = [
            {
                'x': ['a', 'b'],
                'y': ['c'],
            },
            {
                'x': ['a'],
                'y': ['d'],
            }
        ]
        FN_FIXTURES_NAMES = ['x', 'y']

        FX_FIXTURES = [
            {
                'x': ['b'],
                'y': ['d'],
                'z': ['j', 'k']
            }
        ]
        FX_FIXTURES_NAMES = ['x', 'y', 'z']

        COMBINATIONS_COVER = [
            {
                "fixture_names": ['x', 'y'],
                "fixture_functions": ['fn', 'fx'],
            },
            {
                "fixture_names": ['z'],
                "fixture_functions": ['fx'],
            },
        ]

    assert hasattr(TestMyTest, 'test_combocover_fn_fx_x_y')
    assert hasattr(TestMyTest, 'test_combocover_fx_z')
    inst = TestMyTest()
    assert inst.test_combocover_fn_fx_x_y() is None
    assert inst.test_combocover_fx_z() is None


def test_combination_function_failed(combination_test_mixin):

    class TestMyTest(combination_test_mixin):
        FN_FIXTURES = [
            {
                'x': ['a', 'b'],
                'y': ['c'],
            },
            {
                'x': ['a'],
                'y': ['d'],
            }
        ]
        FN_FIXTURES_NAMES = ['x', 'y']

        FX_FIXTURES = [
            {
                'x': ['b'],
                'y': ['d'],
                'z': ['j', 'k']
            }
        ]
        FX_FIXTURES_NAMES = ['x', 'y', 'z']

        COMBINATIONS_COVER = [
            {
                "fixture_names": ['x', 'y'],
                "fixture_functions": ['fn'],
            },
            {
                "fixture_names": ['x', 'y', 'z'],
                "fixture_functions": ['fx'],
            },
        ]

    assert hasattr(TestMyTest, 'test_combocover_fn_x_y')
    assert hasattr(TestMyTest, 'test_combocover_fx_x_y_z')
    inst = TestMyTest()
    with pytest.raises(AssertionError) as exec_info:
        inst.test_combocover_fn_x_y()
    exec_info = str(exec_info.exconly())
    assert "Missing combinations" in exec_info
    assert "[x_b|y_d]" in exec_info
    with pytest.raises(AssertionError) as exec_info:
        inst.test_combocover_fx_x_y_z()


def test_combination_function_scope_failed(combination_test_mixin):
    class TestMyTest(combination_test_mixin):
        FN_FIXTURES = [
            {
                'x': ['a', 'b'],
                'y': ['c'],
            },
            {
                'x': ['a'],
                'y': ['d'],
            }
        ]
        FN_FIXTURES_NAMES = ['x', 'y']

        FX_FIXTURES = [
            {
                'x': ['b'],
                'y': ['d'],
                'z': ['j', 'k']
            }
        ]
        FX_FIXTURES_NAMES = ['x', 'y', 'z']

        COMBINATIONS_COVER = [
            {
                "fixture_names": ['x', 'y', 'z'],
                "fixture_functions": ['fx'],
            },
        ]

    assert hasattr(TestMyTest, 'test_combocover_fx_x_y_z')
    inst = TestMyTest()
    with pytest.raises(AssertionError) as exec_info:
        inst.test_combocover_fx_x_y_z()
    exec_info = str(exec_info.exconly())
    assert "Missing combinations" in exec_info
    assert "[x_a|y_c|z_j]" in exec_info
    assert "[x_a|y_c|z_k]" in exec_info
    assert "[x_b|y_c|z_j]" in exec_info
    assert "[x_b|y_c|z_k]" in exec_info
    assert "[x_a|y_d|z_j]" in exec_info
    assert "[x_a|y_d|z_k]" in exec_info


def test_combination_function_passed_in_function_scope(combination_test_mixin):

    class TestMyTest(combination_test_mixin):
        FN_FIXTURES = [
            {
                'x': ['a', 'b'],
                'y': ['c'],
            },
            {
                'x': ['a'],
                'y': ['d'],
            }
        ]
        FN_FIXTURES_NAMES = ['x', 'y']

        FX_FIXTURES = [
            {
                'x': ['b'],
                'y': ['d'],
                'z': ['j', 'k']
            }
        ]
        FX_FIXTURES_NAMES = ['x', 'y', 'z']

        COMBINATIONS_COVER = [
            {
                "fixture_names": ['x', 'y'],
                "fixture_functions": ['fx', 'fn'],
            },
            {
                "fixture_names": ['x', 'y', 'z'],
                "fixture_functions": ['fx'],
                "scope": combination_test_mixin.FUNCTIONS_SCOPE
            },
        ]

    assert hasattr(TestMyTest, 'test_combocover_fx_fn_x_y')
    assert hasattr(TestMyTest, 'test_combocover_fx_x_y_z')
    inst = TestMyTest()
    assert inst.test_combocover_fx_x_y_z() is None
    assert inst.test_combocover_fx_fn_x_y() is None


@pytest.mark.parametrize(argnames=['names'],
                         argvalues=[
                             (('fn', 'not_existing'), ),
                             (('not_existing'), ),
                             ((), ),
                         ])
def test_invalid_fixture_names(names):

    with pytest.raises(exceptions.InvalidCombinationsFixtureFunctions):
        class Test(TestMatrixMixin):

            FN_FIXTURES_NAMES = ['a', 'b', 'y']
            FN_FIXTURES = [
                {
                    'a': ['a'],
                    'b': ['b'],
                    'y': ['b'],
                }
            ]

            FX_FIXTURE_NAMES = ['a', 'b', 'x']
            FX_FIXTURES = [
                {
                    'a': ['a'],
                    'b': ['b'],
                    'x': ['b'],
                }
            ]

            def test_fn(self):
                pass

            def test_fx(self):
                pass

            COMBINATIONS = [
                {
                    'fixture_names': ['a', 'b'],
                    'fixture_functions': names
                }
            ]


@pytest.mark.parametrize(argnames=['names'],
                         argvalues=[
                             (('a', 'b', 'y'), ),
                             (('a', 'x'), ),
                             (('not_exisitng',), ),
                             ((), )
                         ])
def test_invalid_fixture_names(names):

    with pytest.raises(exceptions.InvalidCombinationsFixtureNames):
        class Test(TestMatrixMixin):

            FN_FIXTURES_NAMES = ['a', 'b', 'y']
            FN_FIXTURES = [
                {
                    'a': ['a'],
                    'b': ['b'],
                    'y': ['b'],
                }
            ]

            FX_FIXTURE_NAMES = ['a', 'b', 'x']
            FX_FIXTURES = [
                {
                    'a': ['a'],
                    'b': ['b'],
                    'x': ['b'],
                }
            ]

            def test_fn(self):
                pass

            def test_fx(self):
                pass

            COMBINATIONS = [
                {
                    'fixture_names': names,
                    'fixture_functions': ['fx', 'fn']
                }
            ]


def test_exclude_generated_test_combinations(testdir):
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
        FN_FIXTURES = [{'y': ['x']}]
        FN_FIXTURES_NAMES = ['y']
        
        COMBINATIONS_COVER = [
            {
                "fixture_names": ['y'],
                "fixture_functions": ['fn'],
                "scope": 'class',
            }
        ]
        
        @pytest.fixture
        def y_x(self):
            pass
        
    class TestOtherTest(TestFirst):
        FN_FIXTURES = [{'y': ['x']}]
        FN_FIXTURES_NAMES = ['y']
        
    """
    path = testdir.makepyfile(source)
    result = testdir.runpytest("{path}".format_map(vars()))

    result.assert_outcomes(passed=3)

    items = testdir.getitems(source)
    assert {(f.name, f.cls.__name__) for f in items} == {
        ('test_fn[y_x]', 'TestFirst'),
        ('test_fn[y_x]', 'TestOtherTest'),
        ('test_combocover_fn_y', 'TestFirst')
    }
