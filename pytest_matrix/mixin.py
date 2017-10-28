import re
from collections import defaultdict
from functools import reduce

import itertools

import pytest


class MatrixTestBase(type):

    FIXTURE_SUFFIX = '_FIXTURES'
    TEST_FUNCTION_PREFIX = 'test_'

    @staticmethod
    def is_mixin(dct, bases):
        """
        check if the 'is_mixin' attribute is manually setted to concrete class
        """
        manually_setted = dct.get('is_mixin', False)
        return manually_setted

    def __new__(mcs, name, bases, dct):
        is_mixin = MatrixTestMixin.is_mixin(dct, bases)
        is_test_case = not is_mixin
        dct['is_mixin'] = is_mixin
        new_cls = super().__new__(mcs, name, bases, dct)
        if is_test_case:
            new_cls.exclude_tests = [mcs.TEST_FUNCTION_PREFIX + name
                                     for name in new_cls.get_cleaned_test_names()
                                     if not hasattr(new_cls, name)]
            all_fixtures = new_cls.set_fixture_data()
            new_cls.set_combinations_method(all_fixtures)
            # new_cls.create_sharing_fixtures()
        return new_cls

    def get_cleaned_test_names(cls):
        prefix_len = len(cls.TEST_FUNCTION_PREFIX)
        test_names = (att for att in dir(cls) if att.startswith(cls.TEST_FUNCTION_PREFIX))
        return [att[prefix_len:] for att in test_names]

    def set_fixture_data(cls):
        """
        replace fixture data with FixtureGrouper
        :return:
        """
        all_data = []
        for fixture_name in cls.get_cleaned_test_names():
            fixture_name = fixture_name.upper() + cls.FIXTURE_SUFFIX
            raw_data = getattr(cls, fixture_name, None)
            if raw_data is not None:
                grouper = FixtureGrouper(cls.FIXTURE_NAMES, raw_data)
                setattr(cls, fixture_name, grouper)
                all_data.append(grouper)
        return all_data

    def set_combinations_method(cls, all_fixtures):
        def test_all_combinations_used(self):
            all_combinations = all_fixtures
            if len(all_combinations) > 1:
                all_combinations = reduce(lambda x, y: x + y, all_combinations)
            else:
                all_combinations = all_combinations[0]
            missing_combinations = all_combinations.missing_combinations()
            assert not any(missing_combinations), ("Missing combinations:\n"
                                                   + "\n".join(map(str, missing_combinations)))

        cls.test_all_combinations_used = test_all_combinations_used

    def create_sharing_fixtures(cls):
        for name in cls.FIXTURE_NAMES:
            if not hasattr(cls, name):

                def fixture(request):
                    nodeid = request.node.nodeid
                    reg = re.compile(".*[.+[|\[](?P<name>{}_[_\w]+)".format(name))
                    current_fixture_name = reg.match(nodeid).groupdict()['name']
                    return request.getfixturevalue(current_fixture_name)

                setattr(cls, name, fixture)
                fn = getattr(cls, name)
                pytest.fixture(fn)


class TestMatrixMixin(metaclass=MatrixTestBase):
    """
    define test function:

    class MyTestCase(TestMatrixMixin):
        def test_my_fn(self, arg_first, arg_second, result):
            assert my_function(arg_first, arg_second) == result

        MY_FN_FIXTURE_NAMES = ['arg_first']
        MY_FN_FIXTURES = [
            {
                'arg_first': ['val_1', 'val_2'],
            }

        @pytest.fixtures
        def arg_first_val_1(self):
            return 'val_1'

        @pytest.fixtures
        def arg_first_val_2(self):
            return 'val_2'

        @pytest.fixtures
        def arg_second(self):
            return 'val'

        @pytest.fixtures
        def result(self, arg_first, arg_second):
            # prepare expected result base on arg_first and arg_second fixture
            # in each test the arg_first parameter will have different value
            return ...

    This will generate tests:
        MyTestCase::test_my_fn[arg_first_val_1|arg_second|result]
        MyTestCase::test_my_fn[arg_first_val_2|arg_second|result]

    """
    pass


class FixtureGrouper(list):

    def __init__(self, fixture_names, *args, **kwargs):
        if not (isinstance(fixture_names, list), isinstance(fixture_names, tuple)):
            raise TypeError("fixture_names must be instance of 'list' or 'tuple', not: "
                            "'{fixture_names.__class__.__name__}'".format_map(vars()))
        self._fixture_names = fixture_names
        super().__init__(*args, **kwargs)

    @property
    def fixture_names(self):
        return self._fixture_names

    def generate_single_group_name_combinations(self, group):
        """
        generate combinations of group ordered by fixture_names

        self.names = ['a', 'b']
        group = {'b': ["A", "B", "C"],
                 'a': ["x", "y"]
                 }

        :return: (('a_x', 'y_A'), ('a_x', 'y_B'), ('a_x', 'y_C'),
                  ('a_y', 'y_A'), ('a_y', 'y_B'), ('a_y', 'y_C'),
                  )
        """
        ordered_groups = (tuple("%s_%s" % (name, item) for item in group[name])
                          for name in self.fixture_names)
        return itertools.product(*ordered_groups)

    def __getitem__(self, item):
        return self.generate_single_group_name_combinations(super().__getitem__(item))

    def __delitem__(self, key):
        raise NotImplementedError()

    def __iter__(self):
        for g in super().__iter__():
            yield from self.generate_single_group_name_combinations(g)

    def generate_fixtures_with_ids(self):
        for fixture_names in self:
            ids, fixtures = zip(*((name, pytest.lazy_fixture(name)) for name in fixture_names))
            ids = "|".join(ids)
            yield ids, fixtures

    def missing_combinations(self):
        unique_items = defaultdict(set)
        existing_combinations = set()
        for comb in self:
            for arg_position, arg in enumerate(comb):
                unique_items[arg_position].add(arg)
            existing_combinations.add(comb)
        unique_items.default_factory = None
        all_combinations = set(itertools.product(*unique_items.values()))
        return all_combinations.difference(existing_combinations)

    def __add__(self, other):
        return FixtureGrouper(self.fixture_names, super().__add__(other))


