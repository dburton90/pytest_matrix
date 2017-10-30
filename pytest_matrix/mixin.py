import re
from collections import defaultdict, Iterable
from functools import reduce

import itertools

import pytest

from . import exceptions


class MatrixTestBase(type):

    FIXTURE_SUFFIX = '_FIXTURES'
    FIXTURE_NAMES_SUFFIX = '_FIXTURES_NAMES'
    TEST_FUNCTION_PREFIX = 'test_'
    HIDDEN_TEST_FUNCTION_PREFIX = '__test_'

    @staticmethod
    def is_mixin(dct, bases):
        """
        check if the 'is_mixin' attribute is manually setted to concrete class
        """
        manually_setted = dct.get('is_mixin', False)
        return manually_setted

    @staticmethod
    def update_dict(dct):
        dct.setdefault('IS_MIXIN', [])
        dct.setdefault('SKIP_TESTS', [])
        dct.setdefault('NOT_GENERATE_TESTS', [])

    def __new__(mcs, name, bases, dct):
        mcs.update_dict(dct)
        new_cls = super().__new__(mcs, name, bases, dct)
        is_test_case = not new_cls.IS_MIXIN
        if is_test_case:
            test_names = new_cls.get_cleaned_test_names()
            for test_name in test_names:
                try:
                    fixture_names = MatrixTestBase.get_fixtures_names(dct, test_name)
                except KeyError:
                    raise exceptions.FixturesNamesMissing(name, test_name)
                try:
                    fixture_combinations = MatrixTestBase.get_raw_fixtures_data(dct, test_name)
                except KeyError:
                    raise exceptions.FixturesCombinationsMissing(name, test_name)
                combinator = FixtureGrouper(fixture_names, fixture_combinations)
                combinator.validate(name, test_name)
                setattr(new_cls, test_name.upper() + mcs.FIXTURE_SUFFIX, combinator)

        return new_cls

    def get_cleaned_test_names(cls):
        """
        :return: list of test's names, and include only tests wich are not in SKIP_TESTS or NOT_GENERATE_TESTS
        """
        prefix_len = len(cls.TEST_FUNCTION_PREFIX)
        test_names = (att for att in dir(cls) if att.startswith(cls.TEST_FUNCTION_PREFIX))
        skip_tests = (att for att in test_names if cls.should_be_parametrize(att))
        return [att[prefix_len:] for att in skip_tests]

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

    @staticmethod
    def get_fixtures_names(dct, function_name):
        name = function_name.upper() + TestMatrixMixin.FIXTURE_NAMES_SUFFIX
        names = dct[name]
        return names

    @staticmethod
    def get_raw_fixtures_data(dct, function_name):
        name = function_name.upper() + TestMatrixMixin.FIXTURE_SUFFIX
        values = dct[name]
        return values

    def should_be_parametrize(cls, function_name):
        return function_name not in itertools.chain(cls.SKIP_TESTS, cls.NOT_GENERATE_TESTS)

    def get_parametrize_data(cls, function_name, real_fixture_names):
        if not function_name.startswith(cls.TEST_FUNCTION_PREFIX):
            raise ValueError("Test name in class {cls.__name__} must start with {cls.TEST_FUNCTION_PREFIX}."
                             " Invalid name: {function_name}".format_map(vars()))
        function_name = function_name[len(cls.TEST_FUNCTION_PREFIX):].upper()
        grouper = getattr(cls, function_name + cls.FIXTURE_SUFFIX)
        grouper_fixture_names = set(grouper.fixture_names)
        all_fixture_names = set(real_fixture_names).union(grouper_fixture_names)
        extra = grouper_fixture_names.difference(all_fixture_names) or False
        ids, fixtures = zip(*grouper.generate_fixtures_with_ids())
        return {
            'argnames': grouper.fixture_names,
            'argvalues': fixtures,
            'ids': ids,
            'indirect': extra
        }





class TestMatrixMixin(metaclass=MatrixTestBase):
    """
    define test function:

    class MyTestCase(TestMatrixMixin):
        def test_my_fn(self, arg_first, arg_second, result):
            assert my_function(arg_first, arg_second) == result

        MY_FN_FIXTURES_NAMES = ['arg_first']
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

    def __getitem__(self, item):
        return generate_single_group_name_combinations(super().__getitem__(item), self.fixture_names)

    def __delitem__(self, key):
        raise NotImplementedError()

    def __iter__(self):
        for g in super().__iter__():
            yield from generate_single_group_name_combinations(g, self.fixture_names)

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

    def validate(self, class_name, function_name):
        for g in super().__iter__():
            if set(g.keys()) != set(self.fixture_names):
                extra = set(g.keys()).difference(set(self.fixture_names))
                missing = set(self.fixture_names).difference(set(g.keys()))
                raise exceptions.InvalidFixturesCombinationsKeys(class_name, function_name,
                                                                 self.fixture_names, extra, missing)


def generate_single_group_name_combinations(group, fixture_names):
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
                      for name in fixture_names)
    return itertools.product(*ordered_groups)

