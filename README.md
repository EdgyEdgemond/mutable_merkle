# Mutable Merkle
[![image](https://img.shields.io/pypi/v/mutable_merkle.svg)](https://pypi.org/project/mutable_merkle/)
[![image](https://img.shields.io/pypi/l/mutable_merkle.svg)](https://pypi.org/project/mutable_merkle/)
[![image](https://img.shields.io/pypi/pyversions/mutable_merkle.svg)](https://pypi.org/project/mutable_merkle/)
![style](https://github.com/EdgyEdgemond/mutable_merkle/workflows/style/badge.svg)
![tests](https://github.com/EdgyEdgemond/mutable_merkle/workflows/tests/badge.svg)
[![codecov](https://codecov.io/gh/EdgyEdgemond/mutable_merkle/branch/master/graph/badge.svg)](https://codecov.io/gh/EdgyEdgemond/mutable_merkle)

``mutable_merkle`` provides a merkle tree with append, update and remove leaf functionality. This 
is intended to support solutions that are not just append only.

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

## Serialization

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
