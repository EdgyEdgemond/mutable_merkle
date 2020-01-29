#!/usr/bin/env python
import setuptools

import mutable_merkle


tests_requires = (
    # https://github.com/pytest-dev/pytest/issues/3579
    "pytest >= 3.7.2",
    "pytest-cov",
    "pytest-random-order",
)

setuptools.setup(
    name="mutable_merkle",
    version=mutable_merkle.VERSION,
    description="A Merkle tree supporting append, update, remove operations.",
    url="https://github.com/EdgyEdgemond/mutable_merkle",
    author="Daniel Edgecombe",
    author_email="edgy.edgemond@gmail.com",
    install_requires=(),
    include_package_data=True,
    packages=setuptools.find_packages(include=("mutable_merkle*",)),
    python_requires=">=3.5",
    extras_require={

        # Useful tools for managing releases
        "release": (
            "bump2version<1.0.0",
            "changelog_gen",
        ),

        # Useful tools for profiling and inspecting code.
        "dev": (
            "flake8",
            "flake8-commas",
            "flake8-isort",
            "flake8-quotes",
            "isort>=4.3.15",
        ),

        # Handy if you want to run specific tests using the ``pytest``
        # command (``setup.py test`` runs all tests by default, and it's
        # a bit tricky to pass args to that command).
        "test": tests_requires,

    },

    # Configure test dependencies and runner.
    # https://docs.pytest.org/en/latest/goodpractices.html#integrating-with-setuptools-python-setup-py-test-pytest-runner
    setup_requires=["pytest-runner"],
    test_suite="tests",
    tests_require=tests_requires,
)
