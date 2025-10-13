Contributing
============

Contributions are welcome! This guide will help you get started.

Development Setup
-----------------

Clone and install:

.. code-block:: bash

   git clone https://github.com/vanshbordia/vlrdevapi.git
   cd vlrdevapi
   pip install -e .[dev]

Running Tests
-------------

Run the test suite:

.. code-block:: bash

   pytest tests/lib/

Run with coverage:

.. code-block:: bash

   pytest tests/lib/ --cov=vlrdevapi

Code Style
----------

The project uses ruff for linting and formatting:

.. code-block:: bash

   ruff check src/
   ruff format src/

Guidelines
----------

1. All tests must pass
2. Add tests for new features
3. Update documentation
4. Follow existing code style

Pull Requests
-------------

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

License
-------

MIT License. See LICENSE file for details.
