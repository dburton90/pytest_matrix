Pytest Matrix
^^^^^^^^^^^^

This plugin provide simple way how to generate multiple test from combinations of setup data.


Base usecase:
=============

.. code:: Python
    import pytest
    from pytest_matrix import TestMatrixMixin
    from myproject import my_func


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
-------------------------
[*] MyTestCase::test_my_fn[arg_first_val_1|arg_second|result]
[*] MyTestCase::test_my_fn[arg_first_val_2|arg_second|result]
