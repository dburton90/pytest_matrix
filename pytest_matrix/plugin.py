import pytest
from pytest_lazyfixture import is_lazy_fixture

from pytest_matrix.mixin import MatrixTestBase, FixtureGrouper


def pytest_generate_tests(metafunc):
    marker = None
    try:
        markers = metafunc.function.pytestmark
        markers = [m for m in markers if m.name == 'matrix']
        if len(markers) > 1:
            raise ValueError("{metafunc.definition.nodeid} was marked 'matrix' more than one")
        elif markers:
            marker = markers[0]
    except AttributeError:
        pass
    if marker is not None:
        all_fixture_names = metafunc.fixturenames
        grouper = FixtureGrouper(marker.kwargs['names'], marker.kwargs['combs'])
        parametrize_data = grouper.get_parametrize_data(all_fixture_names)
        metafunc.fixturenames = parametrize_data['argnames']
        metafunc.parametrize(**parametrize_data)
    elif isinstance(metafunc.cls, MatrixTestBase):
        function_name = metafunc.function.__name__
        if metafunc.cls.should_be_parametrize(function_name):
            all_fixture_names = metafunc.fixturenames
            parametrize_data = get_paramatrized_data(metafunc.cls, function_name, all_fixture_names)
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


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    outcome = yield
    result = outcome.get_result()
    if is_lazy_fixture(result):
        result = request.getfixturevalue(result.name)
        fixturedef.cached_result = (result, request.param_index, None)
    return result


def get_paramatrized_data(cls, function_name, all_fixtures):
    function_name = function_name[len(cls.TEST_FUNCTION_PREFIX):]
    fixture_names = MatrixTestBase.get_fixtures_names(cls.__dict__, function_name)
    fixture_combinations = MatrixTestBase.get_raw_fixtures_data(cls.__dict__, function_name)
    grouper = FixtureGrouper(fixture_names, fixture_combinations)
    return grouper.get_parametrize_data(all_fixtures)
