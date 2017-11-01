import pytest

from pytest_matrix.mixin import MatrixTestBase


def pytest_generate_tests(metafunc):
    if isinstance(metafunc.cls, MatrixTestBase):
        function_name = metafunc.function.__name__
        if metafunc.cls.should_be_parametrize(function_name):
            all_fixture_names = metafunc.fixturenames
            parametrize_data = metafunc.cls.get_parametrize_data(function_name, all_fixture_names)
            metafunc.fixturenames = parametrize_data['argnames']
            metafunc.parametrize(**parametrize_data)


def pytest_itemcollected(item):
    if isinstance(item.cls, MatrixTestBase) and item.name in item.cls.SKIP_TESTS:
        item.add_marker(pytest.mark.skip())


def pytest_pycollect_makeitem(collector, name, obj):
    """ prevent collect anything from mixin class and do not collect inherited combocover tests """
    if isinstance(collector.cls, MatrixTestBase):
        if collector.cls.IS_MIXIN or (name.startswith('test_combocover')
                                      and name not in collector.cls.COMBINATIONS_COVER_TESTS):
            return []

