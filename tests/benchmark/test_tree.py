import random
from hashlib import sha256
from math import (
    log,
    log2,
)
from uuid import uuid4

import pytest

from mutable_merkle import util
from mutable_merkle.tree import MerkleTree


BOOL = b"\x01"
INT = b"\x02"
UTF8 = b"\x03"
BYTES = b"\x04"


LEAF_COUNTS = [1, 2, 8, 32, 256, 1024, 32768, 65536]


def digest_primitive(obj):
    if isinstance(obj, bool):
        return BOOL + (b"\x01" if obj else b"\x00")

    elif isinstance(obj, int):
        return INT + obj.to_bytes(8, "big", signed=True)

    elif isinstance(obj, str):
        return UTF8 + len(obj).to_bytes(4, "big") + obj.encode()

    elif isinstance(obj, bytes):
        return BYTES + len(obj).to_bytes(4, "big") + obj


def digest(value):
    return sha256(digest_primitive(value)).digest()


# All of the commented tests fail, on purpose. They are very manual benchmarks
# to give a clearer view of what is actually happening.
#
# import math
# import time
#
# @pytest.fixture
# def tree_factory(hash_type):
#     def factory(count):
#         m = MerkleTree.new([], hash_type=hash_type)
#         for _ in range(count):
#             m.add_leaf(digest(uuid4().hex), hashed=True)
#
#         return m
#     return factory
#
#
# @pytest.mark.parametrize("count", LEAF_COUNTS)
# def test_merkle_add_N_hashed_leaves_xxx(count, hash_type, tree_factory):
#     times = []
#     for i in range(5):
#         tree = tree_factory(count)
#         value = digest(uuid4().hex)
#         start = time.time()
#         tree.add_leaf(value, hashed=True)
#         times.append(time.time() - start)
#     average = sum(times) / len(times)
#     assert count == average
#
#
# @pytest.mark.parametrize("count", LEAF_COUNTS)
# def test_merkle_update_N_hashed_leaves_xxx(count, hash_type, tree_factory):
#     times = []
#     for i in range(5):
#         tree = tree_factory(count)
#         value = digest(uuid4().hex)
#         start = time.time()
#         tree.update_leaf(value, 0, hashed=True)
#         times.append(time.time() - start)
#     average = sum(times) / len(times)
#     assert count == average
#
#
# @pytest.mark.parametrize("count", LEAF_COUNTS)
# def test_merkle_remove_N_hashed_leaves_xxx(count, hash_type, tree_factory):
#     times = []
#     for i in range(5):
#         tree = tree_factory(count)
#         value = digest(uuid4().hex)
#         start = time.time()
#         tree.update_leaf(value, math.floor(count / 2), hashed=True)
#         times.append(time.time() - start)
#     average = sum(times) / len(times)
#     assert count == average


@pytest.mark.parametrize("count", LEAF_COUNTS)
def test_merkle_add_N_hashed_leaves(benchmark, count, hash_type):
    def internal():
        m = MerkleTree.new([], hash_type=hash_type)
        for _ in range(count):
            m.add_leaf(digest(uuid4().hex), hashed=True)

    benchmark(internal)


@pytest.mark.parametrize("count", LEAF_COUNTS)
def test_merkle_add_N_unhashed_leaves(benchmark, count, hash_type):
    def internal():
        m = MerkleTree.new([], hash_type=hash_type)
        for _ in range(count):
            m.add_leaf(digest_primitive(uuid4().hex))

    benchmark(internal)


@pytest.mark.parametrize("count", LEAF_COUNTS)
def test_merkle_new_with_N_starting_leaves(benchmark, count, hash_type):
    leaves = [digest(uuid4().hex) for _ in range(count)]

    benchmark(MerkleTree.new, leaves=leaves, hash_type=hash_type)


@pytest.mark.parametrize("count", LEAF_COUNTS)
def test_merkle_update_with_N_starting_leaves(benchmark, count, hash_type):
    leaves = [digest(uuid4().hex) for _ in range(count)]
    m = MerkleTree.new(leaves=leaves, hash_type=hash_type)

    benchmark(m.update_leaf, digest(uuid4().hex), random.randint(0, count - 1))


@pytest.mark.parametrize("count", LEAF_COUNTS)
def test_merkle_get(benchmark, count, hash_type):
    leaves = [digest(uuid4().hex) for _ in range(count)]
    m = MerkleTree.new(leaves=leaves, hash_type=hash_type)

    benchmark(m._get, random.randint(0, count - 1), 0)


@pytest.mark.parametrize("count", LEAF_COUNTS)
def test_merkle_get_sibling(benchmark, count, hash_type):
    leaves = [digest(uuid4().hex) for _ in range(count)]
    m = MerkleTree.new(leaves=leaves, hash_type=hash_type)

    benchmark(m._get_sibling, random.randint(0, count - 1), 0)


@pytest.mark.parametrize("count", LEAF_COUNTS)
def test_merkle_update_byte_string(benchmark, count, hash_type):
    leaves = [digest(uuid4().hex) for _ in range(count)]
    m = MerkleTree.new(leaves=leaves, hash_type=hash_type)

    benchmark(m._update_byte_string, m.branches[0], digest(uuid4().hex), random.randint(0, count - 1))


@pytest.mark.parametrize("count", LEAF_COUNTS)
def test_merkle_update_branch(benchmark, count, hash_type):
    leaves = [digest(uuid4().hex) for _ in range(count)]
    m = MerkleTree.new(leaves=leaves, hash_type=hash_type)

    benchmark(m._update_branch, digest(uuid4().hex), random.randint(0, count - 1), 0)


@pytest.mark.parametrize("count", [2, 8, 32, 256, 1024, 32768, 65536])
def test_merkle_update_parent(benchmark, count, hash_type):
    leaves = [digest(uuid4().hex) for _ in range(count)]
    m = MerkleTree.new(leaves=leaves, hash_type=hash_type)

    benchmark(m._update_parent, digest(uuid4().hex), random.randint(0, count - 1), 0, False)


@pytest.mark.parametrize("count", [2, 8, 32, 256, 1024, 32768, 65536])
def test_merkle_update_parent_recurse(benchmark, count, hash_type):
    leaves = [digest(uuid4().hex) for _ in range(count)]
    m = MerkleTree.new(leaves=leaves, hash_type=hash_type)

    benchmark(m._update_parent, digest(uuid4().hex), random.randint(0, count - 1), 0, True)


@pytest.mark.parametrize("count", [8, 32, 256, 1024, 32768, 65536])
def test_merkle_rebuild_branch_early_key(benchmark, count, hash_type):
    leaves = [digest(uuid4().hex) for _ in range(count)]
    m = MerkleTree.new(leaves=leaves, hash_type=hash_type)

    benchmark(m._rebuild_branch, random.randint(0, count / 4), count, 0)


@pytest.mark.parametrize("count", [8, 32, 256, 1024, 32768, 65536])
def test_merkle_rebuild_branch_mid_key(benchmark, count, hash_type):
    leaves = [digest(uuid4().hex) for _ in range(count)]
    m = MerkleTree.new(leaves=leaves, hash_type=hash_type)

    benchmark(m._rebuild_branch, random.randint(count / 4, count / 2), count, 0)


@pytest.mark.parametrize("count", [8, 32, 256, 1024, 32768, 65536])
def test_merkle_rebuild_branch_late_key(benchmark, count):
    leaves = [digest(uuid4().hex) for _ in range(count)]
    m = MerkleTree.new(leaves=leaves)

    benchmark(m._rebuild_branch, random.randint(3 * (count / 4), count - 1), count, 0)


def test_merkle_hash_siblings(benchmark):
    benchmark(util.combine, digest(uuid4().hex), digest(uuid4().hex))


@pytest.mark.parametrize("count", [2, 8, 32, 256, 1024, 32768, 65536])
def test_log(benchmark, count):
    benchmark(log, count)


@pytest.mark.parametrize("count", [2, 8, 32, 256, 1024, 32768, 65536])
def test_log2(benchmark, count):
    benchmark(log2, count)


@pytest.mark.parametrize("count", [2, 8, 32, 256, 1024, 32768, 65536])
def test_log_bit_length(benchmark, count):
    benchmark(count.bit_length)
