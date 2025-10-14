Contributing
============

Contributions are welcome! Follow this guide to contribute to vlrdevapi.

Getting Started
---------------

Development Setup
~~~~~~~~~~~~~~~~~

Clone and install in development mode:

.. code-block:: bash

   git clone https://github.com/vanshbordia/vlrdevapi.git
   cd vlrdevapi
   pip install -e .[dev]

This installs the library in editable mode with development dependencies.

Running Tests
-------------

Run All Tests
~~~~~~~~~~~~~

.. code-block:: bash

   pytest tests/lib/

Run Specific Test File
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pytest tests/lib/test_search.py -v

Run with Coverage
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pytest tests/lib/ --cov=vlrdevapi

Code Quality
------------

Linting
~~~~~~~

Check code style:

.. code-block:: bash

   ruff check src/

Formatting
~~~~~~~~~~

Format code:

.. code-block:: bash

   ruff format src/

Contribution Guidelines
-----------------------

Before Submitting
~~~~~~~~~~~~~~~~~

1. **Tests**: All tests must pass
2. **New Features**: Add tests for new functionality
3. **Documentation**: Update relevant docs
4. **Code Style**: Follow existing patterns
5. **Type Hints**: Include type annotations

Pull Request Process
--------------------

1. **Fork** the repository
2. **Create** a feature branch from main
3. **Make** your changes
4. **Test** your changes locally
5. **Commit** with clear messages
6. **Push** to your fork
7. **Submit** a pull request

Code Style Guidelines
---------------------

- Use type hints for all functions
- Follow PEP 8 conventions
- Write descriptive docstrings
- Keep functions focused and small
- Use meaningful variable names

Testing Guidelines
------------------

- Write tests for all new features
- Use fixtures for test data
- Mock external dependencies
- Test edge cases and error conditions

Documentation Guidelines
------------------------

- Update API docs for new functions
- Add examples for new features
- Keep documentation concise
- Use proper RST formatting

Questions?
----------

- Open an issue on GitHub
- Check existing issues and PRs
- Review the codebase for examples

License
-------

By contributing, you agree that your contributions will be licensed under the MIT License.
