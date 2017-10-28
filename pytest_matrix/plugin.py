import pytest

from pytest_matrix.mixin import MatrixTestBase


def pytest_generate_tests(metafunc):
    if isinstance(metafunc.cls, MatrixTestBase):
        func_name = metafunc.function.__name__[5:].upper()
        func_data = getattr(metafunc.cls, (func_name + MatrixTestBase.FIXTURE_SUFFIX), None)
        if func_data is not None:
            metafunc.fixturenames = list(set(metafunc.fixturenames).union(set(func_data.fixture_names)))
            extra = list((set(func_data.fixture_names).difference(set(metafunc.fixturenames))))
            ids, fixtures = zip(*func_data.generate_fixtures_with_ids())
            metafunc.parametrize(func_data.fixture_names, argvalues=fixtures, ids=ids, indirect=extra)


def pytest_itemcollected(item):
    if isinstance(item.cls, MatrixTestBase) and item.name in item.cls.exclude_tests:
        item.add_marker(pytest.mark.skip(msg="This test has no fixture data."))
