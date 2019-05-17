import pytest

import mutable_merkle.util


def pytest_addoption(parser):
    parser.addoption(
        "--hash",
        default="sha256",
        choices=["sha256", "sha512"],
        action="store",
        help="Run tests with the specified hash",
    )


@pytest.fixture(autouse=True)
def skip_by_hash(request):
    option = request.config.getoption("--hash")
    marker = request.node.get_closest_marker("skip_hash")
    if marker and marker.args[0] == option:
        pytest.skip("Skipped as test can't run with this hash function.")


@pytest.fixture(scope="session")
def hashfn(request):
    option = request.config.getoption("--hash")

    return mutable_merkle.util.get_hashfn(option)


@pytest.fixture(scope="session")
def hash_type(request):
    return request.config.getoption("--hash")
