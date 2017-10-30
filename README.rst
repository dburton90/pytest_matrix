Pytest Matrix
^^^^^^^^^^^^

This plugin provide simple way how to generate multiple test from combinations from setup data.


Quickstart:
=============

.. code:: Python

    import pytest
    from pytest_matrix import TestMatrixMixin
    from myproject import my_func


    class MyTestCase(TestMatrixMixin):
        def test_my_fn(self, arg_first, arg_second, result):
            assert my_function(arg_first, arg_second) == result

        MY_FN_FIXTURES_NAMES = ['arg_first']
        MY_FN_FIXTURES = [
            {
                'arg_first': ['val_1', 'val_2'],
            }
        ]

        @pytest.fixture
        def arg_first_val_1(self):
            return 'val_1'

        @pytest.fixture
        def arg_first_val_2(self):
            return 'val_2'

        @pytest.fixture
        def arg_second(self):
            return 'val'

        @pytest.fixture
        def result(self, arg_first, arg_second):
            # prepare expected result base on arg_first and arg_second fixture
            # in each test the arg_first parameter will have different value
            return ...

Please notice *result* fixture and *arg_first* fixture. There is no *arg_first* fixture definition, the *arg_first* is created by py.test during test generation and you get access to current value of *arg_first*, same as test function receive.

This will generate tests:
-------------------------
- MyTestCase::test_my_fn[arg_first_val_1|arg_second|result]
- MyTestCase::test_my_fn[arg_first_val_2|arg_second|result]


Test Data
=========

Every test function must be prefixed with '*test_*'
For every test function must be defined two class attributes. If test function is named '*test_my_function*',
there must be defined *MY_FUNCTION_FIXTURES_NAMES* and *MY_FUNCTION_FIXTURES* lists.
You must define them in every class (they are not inherited).

MY_FUNCTION_FIXTURES_NAMES:
---------------------------
- list of names of fixtures to be combined in test
- names of fixtures to be combined
- you can define fixtures, which *ARE NOT* defined in test as parameter, these fixtures will be
  stored in request.param and also it will be accessible by other fixtures

MY_FUNCTION_FIXTURES:
---------------------
- list of fixture combinations
- each combination is dict
    - keys are same as in *MY_FUNCTION_FIXTURES_NAMES*
    - values are list of fixture name
        - fixture name is combination of parameter name and the list item

Fixtures definitions:
---------------------
- For every item in *MY_FUNCTION_FIXTURES* must exists fixture. Does not have to be in same class.
- Fixtures names are defined in *MY_FUNCTION_FIXTURES*. The name si combination of key and each item in list.

.. code:: Python

    MY_FN_FIXTURES = [
        {
            'par': ['a', 'b'],
        }
    ]
    # will search for fixtures *par_a* and *par_b*


*WARNING:*
Be aware that every test has his own fixture context. This is useful when you want to access current value
of function parameter by fixture name, but can be easily overlooked.
Example:

.. code:: Python

    class MyTestCase(TestMatrixMixin):
        def test_my_fn(self, par, result):
            # some test

        MY_FN_FIXTURES_NAMES = ['par']
        MY_FN_FIXTURES = [
            {
                'par': ['a', 'b'],
            }
        ]

        @pytest.fixture
        def par_a(self):
            return 'val_a'

        @pytest.fixture
        def par_b(self):
            return 'val_b'

        @pytest.fixture
        def par(self):
            # THIS WILL NEVER BE USED IN GENERATED TESTS
            # the context of the generated test inject in every test to par fixture either par_a or par_b

        @pytest.fixture
        def result(self, par):
            # par is either value of par_a or par_b, it depends on test


Test Generator
--------------
The test are generated for cartesian product of defined fixture_names.

.. code:: Python

    class MyTestCase(TestMatrixMixin):
        def test_my_fn(self, s, b):
            # some test

        MY_FN_FIXTURES_NAMES = ['a', 'b']
        MY_FN_FIXTURES = [
            {
                'a': ['x', 'y'],
                'b': ['i', 'j'],
            },
            {
                'a': ['x', 'y'],
                'b': ['k', 'l'],
            }
        ]

this will generate tests:
- test_my_fn[a_x|b_i]
- test_my_fn[a_x|b_j]
- test_my_fn[a_y|b_i]
- test_my_fn[a_y|b_j]
- test_my_fn[a_x|b_k]
- test_my_fn[a_x|b_l]
- test_my_fn[a_y|b_k]
- test_my_fn[a_y|b_l]


MIXIN and inheritance
=====================

IS_MIXIN
--------
You can define tests in separate class and reuse them in multiple other class. You usually don't want to collect these tests and run them. So you can add class attribute *IS_MIXIN = True* and tests in this class
will not be collected by pytest.

If you use some of these mixins you have to define *_FIXTURES_NAMES* and *_FIXTURES* for each test. It could happen, that you won't use some of the tests, or you do not want generate from some of the tests.

SKIP_TEST
---------
You can skip tests by writing the test name in *SKIP_TESTS* class attribute.

NOT_GENERATE_TESTS
------------------
Write name of test you don't want to generate ot *NOT_GENEREATE_TESTS* attribute. Difference between NOT_GENERATE_TESTS and SKIP_TESTS is that NOT_GENERATE_TESTS will be actually run, but they will not be paramatrize.

Attributes *IS_MIXIN*, *SKIP_TESTS* and *NOT_GENERATE_TESTS* are not inherited from parent class.

Example:

.. code:: Python

    class MyTestMixin(TestMatrixMixin):
        IS_MIXIN = True

        def test_a(self):
            pass

        def test_b(self):
            pass


    class RealTest(MyTestMixin)

        SKIP_TESTS = ['test_a']
        NOT_GENERATE_TESTS = ['test_b']


    class DeeperInheritanceTest(RealTest):
        SKIP_TESTS = ['test_b']

        A_FIXTURES_NAMES = ['par']
        A_FIXTURES = [
            {
                'par': ['a', 'b'],
            }
        ]

        @pytest.fixture
        def par_a(self):
            return 'val_a'

        @pytest.fixture
        def par_b(self):
            return 'val_b'


This will skip:
- RealTest.test_a
- DeeperInheritanceTest.test_b

And run these tests:
- RealTest.test_b
- DeeperInheritanceTest.test_a[par_a]
- DeeperInheritanceTest.test_a[par_b]


TODO:
=====
[X] exclude test if test's cls TestMatrixMixin.is_mixin == True
[X] force to define _FIXTURES and _FIXTURES_NAMES in every class, except mixin class
[X] raise error if _FIXTURES keys are not exactly same as _FIXTURE_NAMES
[ ] edit function to control use of all fixtures combinations
[X] check names of fixtures combinations are same as defined FIXTURES_NAMES
[X] allow skip tests
[X] allow not generate tests
[ ] validate sctructure of SKIP_TESTS, NOT_GENERATE_TESTS, FIXTURE_NAMES and FIXTURES
