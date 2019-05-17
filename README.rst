==============
Mutable Merkle
==============

``mutable_merkle`` provides a merkle tree with append, update and remove leaf functionality. This 
is intended to support DLT solutions that are not just append only.

.. code_block:: python

  m1 = mutable_merkle.tree.MerkleTree.new([b"a", b"b", b"c", b"e", b"f"], hash_type="sha256")
  m2 = mutable_merkle.tree.MerkleTree.new([b"a", b"b", b"c", b"d", b"e", b"f"], hash_type="sha256")
  m3 = mutable_merkle.tree.MerkleTree(hash_type="sha256")

  m2.remove_leaf(3)
  for value in [b"a", b"b", b"c", b"e", b"f"]:
      m3.add_leaf(value)

  assert m1.root == m2.root
  assert m1.root == m3.root
