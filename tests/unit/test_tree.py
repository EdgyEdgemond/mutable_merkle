import pytest

import mutable_merkle.tree


@pytest.mark.parametrize("data,root_hash,expected_depth", (
    (
        [
            b"a",
        ],
        "f73902761f5d940342851b717c1d23bc1f78b1e93d554db2b55b0ef4a045de8f",
        2,
    ),
    (
        [
            b"a",
            b"b",
        ],
        "e5a01fee14e0ed5c48714f22180f25ad8365b53f9779f79dc4a3d7e93963f94a",
        2,
    ),
    (
        [
            b"a",
            b"b",
            b"c",
        ],
        "d0a664079d491a97357efa1ce1eab5aeb566adef78a2b910e8d13e901e192832",
        3,
    ),
    (
        [
            b"a",
            b"b",
            b"c",
            b"d",
        ],
        "14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7",
        3,
    ),
    (
        [
            b"a",
            b"b",
            b"c",
            b"d",
            b"e",
            b"f",
        ],
        "829164284f2becc5d39e4c0657321fa2966506b5d0fed33c836dc6308f6612a0",
        4,
    ),
    (
        [
            b"a",
            b"b",
            b"c",
            b"d",
            b"e",
            b"f",
            b"g",
            b"h",
            b"i",
        ],
        "fcc82f11d33e13a9c9f36587b15fc83a581bd4177d397f05ac56a8234fc1cb67",
        5,
    ),
))
@pytest.mark.skip_hash("sha512")
def test_elements(data, root_hash, expected_depth, hash_type):
    m = mutable_merkle.tree.MerkleTree.new(data, hash_type=hash_type)
    m1 = mutable_merkle.tree.MerkleTree(hash_type=hash_type)
    for value in data:
        m1.add_leaf(value)
    assert m.root.hex() == root_hash
    assert m1.root.hex() == root_hash
    # Root is not in branches.
    assert len(m1.branches) + 1 == expected_depth


def test_equality(hash_type):
    leaves = [b"a", b"b", b"c"]
    m = mutable_merkle.tree.MerkleTree.new(leaves=leaves, hash_type=hash_type)
    m2 = mutable_merkle.tree.MerkleTree.new(leaves=leaves, hash_type=hash_type)

    assert m == m2


def test_equality_hashed_unhashed(hash_type, hashfn):
    leaves = [b"a", b"b", b"c"]
    m = mutable_merkle.tree.MerkleTree.new(leaves=leaves, hash_type=hash_type)
    m2 = mutable_merkle.tree.MerkleTree.new(
        leaves=[hashfn(leaf).digest() for leaf in leaves],
        hashed=True,
        hash_type=hash_type,
    )

    assert m == m2


def test_empty_equality(hash_type):
    m = mutable_merkle.tree.MerkleTree.new(leaves=[], hash_type=hash_type)
    m2 = mutable_merkle.tree.MerkleTree(hash_type=hash_type)

    assert m == m2


def test_empty_hash(hash_type):
    m = mutable_merkle.tree.MerkleTree(hash_type=hash_type)

    m.root == bytearray(mutable_merkle.util.get_hash_len(hash_type))


def test_single_leaf(hash_type, hashfn):
    m = mutable_merkle.tree.MerkleTree(hash_type=hash_type)

    m.add_leaf(b"a")
    assert m.root == hashfn(hashfn(b"a").digest() + bytearray(mutable_merkle.util.get_hash_len(hash_type))).digest()


def test_delete_all_leaves(hash_type):
    m = mutable_merkle.tree.MerkleTree.new([b"a", b"b", b"c", b"d"], hash_type=hash_type)

    m.remove_leaf(3)
    m.remove_leaf(2)
    m.remove_leaf(1)
    m.remove_leaf(0)

    m.root == bytearray(mutable_merkle.util.get_hash_len(hash_type))


def test_delete_last_key_with_truncate(hash_type):
    m = mutable_merkle.tree.MerkleTree.new([b"a", b"b", b"c", b"d", b"e"], hash_type=hash_type)

    m.remove_leaf(4)

    m.root == b""


def test_update_single_leave_tree(hash_type, hashfn):
    m = mutable_merkle.tree.MerkleTree.new([b"a"], hash_type=hash_type)

    m.update_leaf(b"b", 0)

    assert m.root == hashfn(hashfn(b"b").digest() + bytearray(mutable_merkle.util.get_hash_len(hash_type))).digest()


def test_update_out_of_range(hash_type):
    m = mutable_merkle.tree.MerkleTree.new([b"a", b"b", b"c", b"d", b"e"], hash_type=hash_type)

    with pytest.raises(IndexError):
        m.update_leaf(b"f", 5)


def test_update_empty(hash_type):
    m = mutable_merkle.tree.MerkleTree(hash_type=hash_type)

    with pytest.raises(IndexError):
        m.update_leaf(b"a", 0)


def test_remove_out_of_range(hash_type):
    m = mutable_merkle.tree.MerkleTree.new([b"a", b"b", b"c", b"d", b"e"], hash_type=hash_type)

    with pytest.raises(IndexError):
        m.remove_leaf(5)


def test_remove_empty(hash_type):
    m = mutable_merkle.tree.MerkleTree(hash_type=hash_type)

    with pytest.raises(IndexError):
        m.remove_leaf(0)


def test_removal_of_leaf_matches_tree_not_containing_leaf(hash_type):
    m1 = mutable_merkle.tree.MerkleTree.new([b"a", b"b", b"c", b"e", b"f"], hash_type=hash_type)
    m2 = mutable_merkle.tree.MerkleTree.new([b"a", b"b", b"c", b"d", b"e", b"f"], hash_type=hash_type)
    m3 = mutable_merkle.tree.MerkleTree(hash_type=hash_type)

    assert m1.root != m2.root
    assert m1.root != m3.root

    m2.remove_leaf(3)
    for value in [b"a", b"b", b"c", b"e", b"f"]:
        m3.add_leaf(value)

    assert m1.root == m2.root
    assert m1.root == m3.root


def test_update_after_remove_leaf(hash_type):
    m1 = mutable_merkle.tree.MerkleTree.new([b"a", b"b", b"c", b"f"], hash_type=hash_type)
    m2 = mutable_merkle.tree.MerkleTree.new([b"a", b"b", b"c", b"d", b"e"], hash_type=hash_type)
    m3 = mutable_merkle.tree.MerkleTree(hash_type=hash_type)

    assert m1.root != m2.root
    assert m1.root != m3.root

    for value in [b"a", b"b", b"c", b"f"]:
        m3.add_leaf(value)

    m2.remove_leaf(3)
    m2.update_leaf(b"f", 3)

    assert m1.root == m2.root
    assert m1.root == m3.root


def test_removal_of_leaf_matches_tree_not_containing_leaf_drops_below_power_of_two(hash_type):
    m1 = mutable_merkle.tree.MerkleTree.new([b"a", b"b", b"c", b"e"], hash_type=hash_type)
    m2 = mutable_merkle.tree.MerkleTree.new([b"a", b"b", b"c", b"d", b"e"], hash_type=hash_type)
    m3 = mutable_merkle.tree.MerkleTree(hash_type=hash_type)

    assert m1.root != m2.root
    assert m1.root != m3.root

    m2.remove_leaf(3)
    m3.add_leaf(b"a")
    m3.add_leaf(b"b")
    m3.add_leaf(b"c")
    m3.add_leaf(b"e")

    assert m1._branch_count == m2._branch_count
    assert m1.root == m2.root

    assert m1._branch_count == m3._branch_count
    assert m1.root == m3.root


def test_removal_of_leaf_matches_tree_not_containing_leaf_truncates_to_one_key(hash_type):
    m1 = mutable_merkle.tree.MerkleTree.new([b"a"], hash_type=hash_type)
    m2 = mutable_merkle.tree.MerkleTree.new([b"a", b"b", b"c", b"d", b"e"], hash_type=hash_type)
    m3 = mutable_merkle.tree.MerkleTree(hash_type=hash_type)

    assert m1.root != m2.root
    assert m1.root != m3.root

    m2.remove_leaf(3)
    m2.remove_leaf(3)
    m2.remove_leaf(2)
    m2.remove_leaf(1)
    m3.add_leaf(b"a")

    assert m1.root == m2.root
    assert m1._branch_count == m2._branch_count


def test_removal_of_leaf_cleans_orphaned_parents_back_to_null(hash_type):
    m1 = mutable_merkle.tree.MerkleTree.new(
        [b"a", b"b", b"c", b"d", b"e", b"f", b"g", b"h", b"i", b"j"],
        hash_type=hash_type)
    m2 = mutable_merkle.tree.MerkleTree.new(
        [b"a", b"b", b"c", b"d", b"e", b"f", b"g", b"h", b"i", b"j", b"k"],
        hash_type=hash_type)
    m3 = mutable_merkle.tree.MerkleTree(hash_type=hash_type)

    assert m1.root != m2.root
    assert m1.root != m3.root

    m2.remove_leaf(10)
    for l in [b"a", b"b", b"c", b"d", b"e", b"f", b"g", b"h", b"i", b"j"]:
        m3.add_leaf(l)

    assert m1.branches[1] == m2.branches[1]
    assert m1._branch_count == m2._branch_count
    assert m1.root == m2.root


@pytest.mark.skip_hash("sha512")
def test_append_leaves(hash_type):
    hashes = [
        "f73902761f5d940342851b717c1d23bc1f78b1e93d554db2b55b0ef4a045de8f",
        "e5a01fee14e0ed5c48714f22180f25ad8365b53f9779f79dc4a3d7e93963f94a",
        "d0a664079d491a97357efa1ce1eab5aeb566adef78a2b910e8d13e901e192832",
        "14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7",
    ]

    data = [
        b"a",
        b"b",
        b"c",
        b"d",
    ]

    m = mutable_merkle.tree.MerkleTree.new(leaves=[data[0]], hash_type=hash_type)
    assert m.root.hex() == hashes[0]

    for i in range(1, 4):
        m.add_leaf(data[i])

        assert m.root.hex() == hashes[i]


@pytest.mark.parametrize("leaf_count,base_count", (
    (1, 2),
    (2, 2),
    (3, 4),
    (5, 8),
    (15, 16),
    (21, 32),
    (54, 64),
))
def test_tree_expands_base_branch_to_next_power_of_two(leaf_count, base_count, hash_type, hashfn):
    data = [hashfn(bytes(l)).digest() for l in range(leaf_count)]

    m = mutable_merkle.tree.MerkleTree.new(leaves=data, hashed=True, hash_type=hash_type)

    assert m._branch_size(0) == base_count


@pytest.mark.parametrize("leaf_count", (
    1, 2, 3, 5, 15, 21, 54,
))
def test_tree_len(leaf_count, hash_type, hashfn):
    data = [hashfn(bytes(l)).digest() for l in range(leaf_count)]

    m = mutable_merkle.tree.MerkleTree.new(leaves=data, hashed=True, hash_type=hash_type)

    assert len(m) == leaf_count


def test_marshal_empty_tree(hash_type):
    mt = mutable_merkle.tree.MerkleTree(hash_type=hash_type)

    payload = mt.marshal()

    assert mutable_merkle.tree.MerkleTree.unmarshal(payload) == mt


def test_marshal_tree(hash_type):
    mt = mutable_merkle.tree.MerkleTree.new(
        [b"a", b"b", b"c", b"d", b"e", b"f", b"g", b"h", b"i", b"j"],
        hash_type=hash_type,
    )

    payload = mt.marshal()

    assert mutable_merkle.tree.MerkleTree.unmarshal(payload) == mt
    assert mutable_merkle.tree.MerkleTree.unmarshal(payload).branches == mt.branches


def test_get_proof(hash_type, hashfn):
    mt = mutable_merkle.tree.MerkleTree.new(
        [b"a", b"b", b"c", b"d", b"e", b"f", b"g", b"h"],
        hash_type=hash_type,
    )

    sibling = hashfn(b"d").digest()
    parent_sibling = hashfn(hashfn(b"a").digest() + hashfn(b"b").digest()).digest()
    grandparent_sibling = hashfn(
        hashfn(
            hashfn(b"e").digest() + hashfn(b"f").digest(),
        ).digest() + hashfn(
            hashfn(b"g").digest() + hashfn(b"h").digest(),
        ).digest(),
    ).digest()

    assert mt.get_proof(2) == [
        mt._hash_type.encode().hex(),
        ["R", sibling],
        ["L", parent_sibling],
        ["R", grandparent_sibling],
        ["ROOT", mt.root],
    ]


def test_get_proof_after_update_leaf(hash_type, hashfn):
    mt = mutable_merkle.tree.MerkleTree.new(
        [b"a", b"b", b"c", b"d", b"e", b"f", b"g", b"h"],
        hash_type=hash_type,
    )

    mt.update_leaf(b"z", 3)

    sibling = hashfn(b"z").digest()
    parent_sibling = hashfn(hashfn(b"a").digest() + hashfn(b"b").digest()).digest()
    grandparent_sibling = hashfn(
        hashfn(
            hashfn(b"e").digest() + hashfn(b"f").digest(),
        ).digest() + hashfn(
            hashfn(b"g").digest() + hashfn(b"h").digest(),
        ).digest(),
    ).digest()

    assert mt.get_proof(2) == [
        mt._hash_type.encode().hex(),
        ["R", sibling],
        ["L", parent_sibling],
        ["R", grandparent_sibling],
        ["ROOT", mt.root],
    ]


def test_tree_proof_validates(hash_type, hashfn):
    mt = mutable_merkle.tree.MerkleTree.new(
        [b"a", b"b", b"c", b"d", b"e", b"f", b"g", b"h"],
        hash_type=hash_type,
    )

    proof = mt.get_proof(2)

    assert mutable_merkle.util.verify_proof(proof, hashfn(b"c").digest()) is True


def test_verify_merkle_proof_invalid(hash_type, hashfn):
    mt = mutable_merkle.tree.MerkleTree.new(
        [b"a", b"b", b"c", b"d", b"e", b"f", b"g", b"h"],
        hash_type=hash_type,
    )

    proof = mt.get_proof(2)

    assert mutable_merkle.util.verify_proof(proof, hashfn(b"z").digest()) is False


def test_combined_proofs_validates(hash_type, hashfn):
    m1 = mutable_merkle.tree.MerkleTree.new(
        [b"a", b"b", b"c"],
        hash_type=hash_type,
    )
    m2 = mutable_merkle.tree.MerkleTree.new(
        [b"d", b"e", b"f"],
        hash_type=hash_type,
    )
    m3 = mutable_merkle.tree.MerkleTree.new(
        [b"g", b"h", b"i"],
        hash_type=hash_type,
    )
    parent = mutable_merkle.tree.MerkleTree.new(
        [m1.root, m2.root, m3.root],
        hashed=True,
        hash_type=hash_type,
    )

    proof_of_e = m2.get_proof(1)
    proof_of_m2 = parent.get_proof(1)

    combined_proof = mutable_merkle.util.combine_proofs(proof_of_e, proof_of_m2)

    assert mutable_merkle.util.verify_proof(combined_proof, hashfn(b"e").digest())
