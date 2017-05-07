import hashlib
import io


def digest(input_, algorithm='sha256', block_size=8*2**20):
    if not callable(algorithm) and not isinstance(algorithm, str):
        msg = "Expected callable or string"
        raise TypeError(algorithm, msg)

    if isinstance(algorithm, str):
        try:
            algorithm = getattr(hashlib, algorithm)
        except AttributeError as e:
            msg = "Unknow algorithm"
            raise ValueError(algorithm, msg) from e

    m = algorithm()
    if isinstance(input_, str):
        input_ = io.StringIO(bytes(input_))
    elif isinstance(input_, bytes):
        input_ = io.BytesIO(input_)

    while True:
        buff = input_.read(block_size)
        if not buff:
            break

        m.update(buff)

    return m.hexdigest()
