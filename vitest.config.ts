# pytest.ini configuration file for nitsuah/kryptos

[pytest]
# Add any additional command line options you want as defaults:
#   --cov-report term-missing: Show missing lines in terminal output
#   --cov-report html: Create an HTML report
#   --cov-report xml: Create an XML report
#   --cov-report annotate: Annotate source code with coverage information
addopts = --cov=kryptos --cov-report term-missing

# Define the root directory for tests.  This is important for coverage.
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Configure coverage.py
[coverage:run]
# Where to find the source code.  This is important for coverage.
source = kryptos

# Exclude patterns to omit from coverage analysis. Adjust as needed.
omit =
    */__init__.py
    .venv/*
    dist/*
    build/*
    */setup.py

[coverage:report]
# Fail if coverage is too low.  Adjust the threshold as needed.
fail_under = 80

# Show missing lines in terminal output.
show_missing = True