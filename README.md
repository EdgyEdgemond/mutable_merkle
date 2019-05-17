Mutable Merkle
==============

``mutable_merkle`` provides a merkle tree with append, update and remove leaf functionality. This 
is intended to support DLT solutions that are not just append only.

```python
  m1 = mutable_merkle.tree.MerkleTree.new([b"a", b"b", b"c", b"e", b"f"], hash_type="sha256")
  m2 = mutable_merkle.tree.MerkleTree.new([b"a", b"b", b"c", b"d", b"e", b"f"], hash_type="sha256")
  m3 = mutable_merkle.tree.MerkleTree(hash_type="sha256")

  m2.remove_leaf(3)
  for value in [b"a", b"b", b"c", b"e", b"f"]:
      m3.add_leaf(value)

  assert m1.root == m2.root
  assert m1.root == m3.root
```

Serialization
-------------

Along with update and remove leaf functionality, ``mutable_merkle`` has been designed
around being serializable as well. This supports storage of the merkle tree as well
as transmission of the proofs.


```python
  mt = mutable_merkle.tree.MerkleTree.new(
      [b"a", b"b", b"c", b"d", b"e", b"f", b"g", b"h", b"i", b"j"],
      hash_type=hash_type,
  )

  payload = mt.marshal()

  mt_reload = mutable_merkle.tree.MerkleTree.unmarshal(payload)

  assert mt == mt_reload
```
