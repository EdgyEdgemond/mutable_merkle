import pytest


LEAF_COUNTS = [1, 2, 8, 32, 256, 1024, 32768, 65536]


def test_list_manipulation(benchmark):
    data = [str(i) * 11 for i in range(10000)]

    def update_list(index, value):
        data[index] = value

    benchmark(update_list, 20, "hello world")


def test_string_manipulation(benchmark):
    data = bytearray("".join([str(i) * 11 for i in range(10000)]).encode())

    def update_string(index, value):
        start = index * 4
        end = start + 4
        data[start:end] = value

    benchmark(update_string, 20, b"hello world")


@pytest.mark.parametrize("count", LEAF_COUNTS)
def test_list_pack(benchmark, count):
    data = [bytearray(32) for i in range(count)]

    def pack():
        return [v.hex() for v in data]

    benchmark(pack)


@pytest.mark.parametrize("count", LEAF_COUNTS)
def test_join_list_pack(benchmark, count):
    data = [bytearray(32) for i in range(count)]

    def pack():
        return b"".join(data).hex()

    benchmark(pack)


@pytest.mark.parametrize("count", LEAF_COUNTS)
def test_list_unpack(benchmark, count):
    data = [bytearray(32).hex() for i in range(count)]

    def pack():
        return [bytes.fromhex(v) for v in data]

    benchmark(pack)


@pytest.mark.parametrize("count", LEAF_COUNTS)
def test_join_list_unpack(benchmark, count):
    data = b"".join([bytearray(32) for i in range(count)]).hex()

    def pack():
        data_ = bytes.fromhex(data)
        return [data_[i:i + 32] for i in range(0, len(data_), 32)]

    benchmark(pack)


@pytest.mark.parametrize("count", LEAF_COUNTS)
def test_join_list_unpack_bytearray(benchmark, count):
    data = b"".join([bytearray(32) for i in range(count)]).hex()

    def pack():
        data_ = bytearray.fromhex(data)
        return [data_[i:i + 32] for i in range(0, len(data_), 32)]

    benchmark(pack)
