from setuptools import setup


setup(name="pytest_matrix",
      version=0.1,
      description='Provide tools for generating tests from combinations of fixtures.',
      long_description='This plugin provide simple way how to generate multiple test from combinations of setup data.',
      url="https://github.com/dburton90/pytest_matrix.git",
      author="Daniel Bartoň",
      author_email='daniel.barton@seznam.cz',
      license='GPLv3',
      packages=['pytest_matrix'],
      install_requires=[
          'pytest'
      ],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Plugins',
          'Framework :: Pytest',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 3 :: Only',
          'Topic :: Software Development :: Libraries',
      ],
      keywords='pytest mixin pytest_matrix generating tests',
      zip_safe=False,
      entrypoints={
          'pytest11': [
              'pytest_matrix = pytest_matrix.plugin'
          ]
      }
      )
