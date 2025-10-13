Installation
============

Requirements
------------

- Python 3.11 or higher
- pip package manager

Basic Installation
------------------

Install vlrdevapi using pip:

.. code-block:: bash

   pip install vlrdevapi

This will install the library along with its required dependencies:

- beautifulsoup4 (HTML parsing)
- lxml (fast XML/HTML parser)
- pydantic (data validation)

Development Installation
------------------------

For development work, clone the repository and install in editable mode with development dependencies:

.. code-block:: bash

   git clone https://github.com/vanshbordia/vlrdevapi.git
   cd vlrdevapi
   pip install -e .[dev]

This installs additional tools for testing and development:

- pytest (testing framework)
- ruff (linting and formatting)

Verifying Installation
----------------------

Verify the installation by importing the library:

.. code-block:: python

   import vlrdevapi as vlr
   print(vlr.__version__)

Dependencies
------------

Core Dependencies
~~~~~~~~~~~~~~~~~

- **beautifulsoup4** (>=4.12): HTML parsing library
- **lxml** (>=5.0): Fast C-based XML/HTML parser
- **pydantic** (>=2.0): Data validation using Python type hints

Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~

Development dependencies (installed with ``[dev]``):

- **pytest** (>=8.0.0): Testing framework
- **ruff** (>=0.6.0): Fast Python linter and formatter

Test dependencies (installed with ``[test]``):

- **pytest** (>=8.0.0): Testing framework

Troubleshooting
---------------

lxml Installation Issues
~~~~~~~~~~~~~~~~~~~~~~~~

If you encounter issues installing lxml on Windows, you may need to install Visual C++ build tools or use a pre-built wheel:

.. code-block:: bash

   pip install --only-binary :all: lxml

On Linux, you may need to install development packages:

.. code-block:: bash

   # Debian/Ubuntu
   sudo apt-get install libxml2-dev libxslt-dev python3-dev

   # Fedora/RHEL
   sudo dnf install libxml2-devel libxslt-devel python3-devel

Connection Issues
~~~~~~~~~~~~~~~~~

If you experience connection timeouts or network errors, check your firewall settings and ensure you can access https://www.vlr.gg from your network.

The library includes automatic retry logic with exponential backoff for transient network errors.
