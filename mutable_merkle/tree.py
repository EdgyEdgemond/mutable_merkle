from mutable_merkle import util


class MerkleTree:
    @classmethod
    def new(cls, leaves, hash_type, hashed=False):
        mt = cls(hash_type)

        if not leaves:
            return mt

        if not hashed:
            leaves = [util.hash(leaf, mt._hashfn) for leaf in leaves]

        mt._leaf_count = len(leaves)

        base_count = 1 << (len(leaves) - 1).bit_length()

        if base_count == 1:
            mt._add_branch()

        else:
            branch_index = 0
            while base_count > 1:
                mt.branches[branch_index] = [mt._empty, mt._empty]
                base_count = int(base_count / 2)
                branch_index += 1
                mt._branch_count += 1

        mt.branches[0] = leaves
        if len(leaves) == 1:
            mt.branches[0].append(mt._empty)

        mt._rebuild_branch(0, 0, mt._leaf_count - 1)

        return mt

    def __init__(self, hash_type, root=None, branches=None, leaf_count=0, branch_count=0):
        self._hash_type = hash_type
        self._hash_len = util.get_hash_len(hash_type)
        self._hashfn = util.get_hashfn(hash_type)

        self._empty = bytearray(self._hash_len)
        self.root = root or self._empty
        self._branch_count = branch_count
        self._leaf_count = leaf_count
        self.branches = branches or {}

    def __eq__(self, other):
        return type(self) == type(other) and self.root == other.root

    def __len__(self):
        return self._leaf_count

    def _add_branch(self):
        self.branches[self._branch_count] = [self.root, self._empty]
        self._branch_count += 1

    def add_leaf(self, value, hashed=False):
        if not hashed:
            value = util.hash(value, self._hashfn)

        if self._branch_count == 0 or self._leaf_count + 1 > self._branch_size(0):
            self._add_branch()

        index = self._leaf_count

        self._update_branch(value, index, 0)

        self._leaf_count += 1

        self._update_parent(value, index, 0)

    def update_leaf(self, value, offset, hashed=False):
        if self._leaf_count == 0 or offset >= self._leaf_count:
            raise IndexError("assignment index out of range")

        if not hashed:
            value = util.hash(value, self._hashfn)

        self._update_branch(value, offset, 0)
        self._update_parent(value, offset, 0)

    def _prune_branch(self, branch_index):
        self.branches[branch_index] = self.branches[branch_index][:int(self._branch_size(branch_index) / 2)]  # noqa

    def _remove_branch(self):
        self.root = self.branches[self._branch_count - 1][0]
        del self.branches[self._branch_count - 1]
        self._branch_count -= 1

    def remove_leaf(self, offset):
        if self._leaf_count == 0:
            raise IndexError("pop from empty list")

        if offset >= self._leaf_count:
            raise IndexError("pop index out of range")

        del self.branches[0][offset]
        self.branches[0].append(self._empty)
        self._leaf_count -= 1

        if self._leaf_count == 0:
            self._remove_branch()
            self.root = self._empty
        elif self._leaf_count > 1 and self._leaf_count <= self._branch_size(0) >> 1:
            for i in range(self._branch_count):
                self._prune_branch(i)
            self._remove_branch()

        if self._branch_count > 0:
            offset = offset - 1 if offset == self._branch_size(0) else offset

            self._rebuild_branch(0, offset, self._leaf_count - 1)

    def _update_parent(self, value, index, branch_index, recurse=True):
        sibling = self._get_sibling(index, branch_index)

        if self._side(index) == "L":
            left, right = value, sibling
        else:
            left, right = sibling, value

        parent = util.combine(left, right, self._hashfn)
        parent_index = self._parent_index(index)
        if branch_index + 1 == self._branch_count:
            self.root = parent
        else:
            self._update_branch(parent, parent_index, branch_index + 1)
            if recurse:
                self._update_parent(parent, parent_index, branch_index + 1)

    def _get_sibling_index(self, index):
        if self._side(index) == "L":
            sibling_index = index + 1
        else:
            sibling_index = index - 1

        return sibling_index

    def _get_sibling(self, index, branch_index):
        sibling_index = self._get_sibling_index(index)

        return self._get(sibling_index, branch_index)

    def _get(self, offset, branch_index):
        if offset < len(self.branches[branch_index]):
            return self.branches[branch_index][offset]
        else:
            return self._empty

    def _update_branch(self, value, offset, branch_index):
        target = self.branches[branch_index]
        if offset < len(target):
            target[offset] = value
        else:
            target.append(value)

    def _rebuild_branch(self, branch_index, start_index, end_index):
        # From the last leaf, zero out any values that used to be populated
        orphaned_leaf_count = self._branch_size(branch_index) - (end_index + 1)
        if orphaned_leaf_count > 0:
            keep_index = (self._branch_size(branch_index) - orphaned_leaf_count)
            self.branches[branch_index] = self.branches[branch_index][:keep_index]
            if start_index == 0 and end_index == 0:
                self.branches[branch_index].append(self._empty)

        start_index = start_index if self._side(start_index) == "L" else start_index - 1
        # Ensure we include the final sibbling in the loop.
        end_index = end_index if self._side(end_index) == "R" else end_index + 1

        for index in range(start_index, end_index, 2):
            value = self._get(index, branch_index)
            self._update_parent(value, index, branch_index, recurse=False)

        start_index = self._parent_index(start_index)
        end_index = self._parent_index(end_index)
        if branch_index + 1 < self._branch_count:
            self._rebuild_branch(branch_index + 1, start_index, end_index)

    def _side(self, index):
        return "R" if index & 1 else "L"

    def _parent_index(self, index):
        return index >> 1

    def _branch_size(self, branch_index):
        leaf_count = len(self.branches[branch_index])
        return 1 << (leaf_count - 1).bit_length()

    def get_proof(self, index):
        chain = [self._hash_type.encode().hex()]
        for branch_index in range(self._branch_count):
            sibling_index = self._get_sibling_index(index)
            sibling = self._get(sibling_index, branch_index)
            chain.append([self._side(sibling_index), bytes(sibling)])
            index = self._parent_index(index)
        chain.append(["ROOT", bytes(self.root)])

        return chain

    def marshal(self):
        return {
            "hash_type": self._hash_type,
            "root": self.root.hex(),
            "branches": {k: b"".join([v for v in leaves]).hex() for k, leaves in self.branches.items()},
            "leaf_count": self._leaf_count,
            "branch_count": self._branch_count,
        }

    @staticmethod
    def _unpack_leaves(leaves, hash_type):
        hash_len = util.get_hash_len(hash_type)
        leaves = bytes.fromhex(leaves)
        return [leaves[i:i + hash_len] for i in range(0, len(leaves), hash_len)]

    @classmethod
    def unmarshal(cls, payload):
        return cls(
            hash_type=payload["hash_type"],
            root=bytes.fromhex(payload["root"]),
            branches={k: cls._unpack_leaves(leaves, payload["hash_type"]) for k, leaves in payload["branches"].items()},
            leaf_count=payload["leaf_count"],
            branch_count=payload["branch_count"],
        )
