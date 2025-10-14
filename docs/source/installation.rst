Installation
============

Requirements
------------

- Python 3.11 or higher
- pip package manager

Installation
------------

Install via pip:

.. code-block:: bash

   pip install vlrdevapi

This installs vlrdevapi and its dependencies:

- **beautifulsoup4**: HTML parsing
- **lxml**: Fast XML/HTML parser
- **pydantic**: Data validation

Verify Installation
-------------------

.. code-block:: python

   import vlrdevapi as vlr
   print(vlr.__version__)

Development Setup
-----------------

For development work:

.. code-block:: bash

   git clone https://github.com/vanshbordia/vlrdevapi.git
   cd vlrdevapi
   pip install -e .[dev]

This includes additional tools:

- **pytest**: Testing framework
- **ruff**: Linting and formatting

Troubleshooting
---------------

lxml Installation Issues
~~~~~~~~~~~~~~~~~~~~~~~~

**Windows**: If lxml fails to install, use a pre-built wheel:

.. code-block:: bash

   pip install --only-binary :all: lxml

**Linux**: Install development packages first:

.. code-block:: bash

   # Debian/Ubuntu
   sudo apt-get install libxml2-dev libxslt-dev python3-dev

   # Fedora/RHEL
   sudo dnf install libxml2-devel libxslt-devel python3-devel

Connection Issues
~~~~~~~~~~~~~~~~~

If you experience network errors:

1. Check firewall settings
2. Verify access to https://www.vlr.gg
3. The library includes automatic retry logic for transient errors

Next Steps
----------

- See :doc:`quickstart` to get started
- Browse :doc:`examples` for practical use cases
- Read :doc:`api/search` and other API references
