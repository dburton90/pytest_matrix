Pytest Matrix
^^^^^^^^^^^^^

Easy fixture combinations.

Instalition
-----------

``pip install pytest_matrix``

Quickstart:
=============

.. code:: Python

    import pytest
    from myproject import my_func

        @pytest.mark.matrix(names=['arg_firs'],
                            combs=[
                                    {
                                       'arg_first': ['val_1', 'val_2'],
                                    },
                                   ])
        def test_my_fn(self, arg_first, arg_second, result):
            assert my_function(arg_first, arg_second) == result


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

**OR**

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

This will generate tests:
-------------------------
- MyTestCase::test_my_fn[arg_first_val_1|arg_second|result]
- MyTestCase::test_my_fn[arg_first_val_2|arg_second|result]


Both examples are equal. But in class you have better scope controlling and other options.

Please notice **result** fixture and **arg_first** fixture. There is no **arg_first** fixture definition, the **arg_first** is created by py.test during test generation and you get access to current value of **arg_first**, same as test function receive.



Test Data
=========

Every test function must be prefixed with '**test_**'
For every test function must be defined two class attributes. If test function is named 'test_**my_function**',
there must be defined **MY_FUNCTION_FIXTURES_NAMES** and **MY_FUNCTION_FIXTURES** lists.
You must define them in every class (they are not inherited).

MY_FUNCTION_FIXTURES_NAMES:
---------------------------
- they are not required, it just could be little bit clearer some times, because you can choose order (the way how test name will be generated)
- list of names of fixtures to be combined in test
- you can define fixtures, which **ARE NOT** defined in test as parameter, these fixtures will be
  stored in request.param and also it will be accessible by other fixtures

MY_FUNCTION_FIXTURES:
---------------------
- list of fixture combinations
- each combination is dict
    - keys are same as in **MY_FUNCTION_FIXTURES_NAMES**
    - values are list of fixture name
        - fixture name is combination of parameter name and the list item

Fixtures definitions:
---------------------
- For every item in **MY_FUNCTION_FIXTURES** must exists fixture. It does not have to be in same class.
- Fixtures names are defined in **MY_FUNCTION_FIXTURES**. The name si combination of key and each item in list.

.. code:: Python

    MY_FN_FIXTURES = [
        {
            'par': ['a', 'b'],
        }
    ]
    # will search for fixtures **par_a** and **par_b**


**WARNING:**
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


Simple Fixtures
---------------
There are two simple fixtures types: String (with prefix '@') and Integer  (with prefix '#')

.. code:: Python

    import pytest
    from myproject import my_func

        @pytest.mark.matrix(names=['arg_firs'],
                            combs=[
                                    {
                                       'arg_first': ['#1', '@2'],
                                    },
                                   ])
        def test_my_fn(self, arg_first):
            assert arg_first in (1, '2')


There is no need to define fixtures arg_first_#1 (returning int(1)), arg_first_@2 (returning str(2)). It is impossible have functions (fixture definition) with these names in python anyway :).


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
-------------------------
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
You can define tests in separate class and reuse them in multiple other class. You usually don't want to collect these tests and run them. So you can add class attribute **IS_MIXIN = True** and tests in this class
will not be collected by pytest.

If you use some of these mixins you have to define **_FIXTURES** for each test. It could happen, that you won't use some of the tests, or you do not want generate from some of the tests.

SKIP_TEST
---------
You can skip tests by writing the test name in **SKIP_TESTS** class attribute.

NOT_GENERATE_TESTS
------------------
Write name of test you don't want to generate ot **NOT_GENEREATE_TESTS** attribute. Difference between NOT_GENERATE_TESTS and SKIP_TESTS is that NOT_GENERATE_TESTS will be actually run, but they will not be paramatrize.

Attributes **IS_MIXIN**, **SKIP_TESTS** and **NOT_GENERATE_TESTS** are not inherited from parent class.

Example:

.. code:: Python

    class MyTestMixin(TestMatrixMixin):
        IS_MIXIN = True

        def test_a(self):
            pass

        def test_b(self):
            pass


    class RealTest(MyTestMixin):

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
---------------
- RealTest.test_a
- DeeperInheritanceTest.test_b

And run these tests:
--------------------
- RealTest.test_b
- DeeperInheritanceTest.test_a[par_a]
- DeeperInheritanceTest.test_a[par_b]


Combination Tester
==================
Sometimes you want test if you covered all combinations of specific fixtures. You can define the combinations you want to cover in class attribute **COMBINATIONS_COVER**.

test_combcover_fn_fx_x_y PASSED
-------------------------------
.. code:: python

    class TestCombinations(TestMatrixMixin):
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

        # **COMBINATIONS**
        COMBINATIONS_COVER = [
            {
                "fixture_names": ['x', 'y'],
                "fixture_functions": ['fn', 'fx'],
            }
        ]

        def test_fx(self):
            pass

        def test_fn(self):
            pass

        @pytest.fixture
        def x_a(self):
            pass

        #... rest of class with rest of fixtures (x_b, y_c, y_d, z_j, z_k)

This will generate test **test_combcover_fn_fx_x_y**. The prefix for combination cover test is **test_combcover_** followed by names of functions (*test_fx* and *test_fn*) separated by underscore: **fn_fx_** and suffix are names of fixtures (their combinations we want to cover) **x_y**.

This concrete test will find all types of **x** *('a', 'b')* and **y** *('c', 'd')* fixtures, combine them *([x_a|y_c], [x_b|y_c], [x_a|y_d], [x_b|y_d])* and compare them with combinations manually defined in **_FIXTURES** configuration *(fn: [x_a|y_c], [x_b|y_c], [x_a|y_d] and fx: [x_b|y_d])*. If they are not equal, the test will fail and print all uncovered combinations. But this test will pass.


test_combcover_fn_x_y FAILED
-------------------------------
Now we added other test combination.

.. code:: python

    class TestCombinations(TestMatrixMixin):
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

        # other configs

        COMBINATIONS_COVER = [
            {
                "fixture_names": ['x', 'y'],
                "fixture_functions": ['fn', 'fx'],
            },
            {
                "fixture_names": ['x', 'y'],
                "fixture_functions": ['fn'],  # **TEST ONLY ONE TEST'S FIXTURE COMBINATIONS**
            },
        ]

        # rest of the class...

This will generate two tests **test_combcover_fn_fx_x_y** *PASSED* and **test_combcover_fn_x_y** *FAILED*. The second test failed because combination of *[x_b|y_d]* is not covered in **FN_FIXTURES**. It will be also shown in test_result.

test_combcover_fx_x_y FAILED OR PASSED according to scope
---------------------------------------------------------

There are two type of scopes which combcover can use when looking for all types of fixtures.
    - *class* scope:
        - default scope
        - the combcover will look in ALL **_FIXTURES** defined in same class
    - *functions* scope:
        - the combcover will look for fixture types only in these **_FIXTURES** from functions define in combcover config

.. code:: python

    class TestCombinations(TestMatrixMixin):
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

        # **COMBINATIONS**
        COMBINATIONS_COVER = [
            {
                "fixture_names": ['x', 'y'],
                "fixture_functions": ['fx'],
                "scope": 'class',  # this is not required *class* is default scope
            }
        ]
        # rest of the class...


The test will find all types of **x** *('a', 'b')* and **y** *('c', 'd')* in **ALL** fixtures, combine them *([x_a|y_c], [x_b|y_c], [x_a|y_d], [x_b|y_d])* and compare them with combinations manually defined in **FX_FIXTURES** configuration *([x_b|y_d])*. The result of the test will be **FAILED** and missing combinations will be: *[x_a|y_c], [x_b|y_c], [x_a|y_d]*

If you remove the *scope* key from **COMBINATIONS_COVER** the test will be **PASSED**, because combcover will be looking for only for fixtures type defined in **FX_FIXTURES** *(x_a and y_d)*.

.. code:: python

    class TestCombinations(TestMatrixMixin):
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

        # **COMBINATIONS**
        COMBINATIONS_COVER = [
            {
                "fixture_names": ['x', 'y'],
                "fixture_functions": ['fx'],
                "scope": 'functions',  # this is required
            }
        ]
        # rest of the class...

This combocover test will PASS


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
[ ] check for duplicity in _FIXTURES and COMBINATION_COVER
