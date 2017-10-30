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

# # def pytest_collection_modifyitems(session, config, items):
# #     if isinstance(item.cls, MatrixTestBase) and item.name in item.cls.exclude_tests:
# #         item.add_marker(pytest.mark.skip(msg="This test has no fixture data."))
#
#
def pytest_pycollect_makeitem(collector, name, obj):
    """ prevent collect anything from mixin class """
    # if isinstance(obj, MatrixTestBase):
    #     Class = collector._getcustomclass("Class")
    #     return Class(name, parent=collector)
    if isinstance(collector.cls, MatrixTestBase) and collector.cls.IS_MIXIN:
        return []

