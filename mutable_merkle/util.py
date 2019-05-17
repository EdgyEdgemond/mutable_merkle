from hashlib import sha256
from hashlib import sha512


SUPPORTED_HASHES = {
    "sha256": sha256,
    "sha512": sha512,
}

HASH_LEN = {
    "sha256": 32,
    "sha512": 64,
}


def get_hashfn(hash_type):
    return SUPPORTED_HASHES[hash_type]


def get_hash_len(hash_type):
    return HASH_LEN[hash_type]


def combine(left, right, hashfn):
    return hash(left + right, hashfn)


def hash(value, hashfn):
    return bytearray(hashfn(value).digest())


def verify_proof(proof, leaf):
    hash_type = proof.pop(0)
    hashfn = get_hashfn(bytes.fromhex(hash_type).decode())
    for i in range(len(proof) - 1):
        if proof[i][0] == "R":
            leaf = combine(leaf, proof[i][1], hashfn)
        else:
            leaf = combine(proof[i][1], leaf, hashfn)

    return leaf == proof[-1][1]


def combine_proofs(child_proof, parent_proof):
    return child_proof[:-1] + parent_proof[1:]
