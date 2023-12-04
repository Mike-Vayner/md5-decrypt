import asyncio
import concurrent.futures
import functools
import hashlib
import itertools
import string
import sys
from collections.abc import Iterable
from typing import TypeVar


def _increment_string(source: str, charset: str = string.ascii_lowercase) -> str:
    for i in range(-1, -len(source) - 1, -1):
        if source[i] == charset[-1]:
            continue
        keep = source[:i]
        replace = charset[charset.find(source[i]) + 1]
        fill = charset[0] * -(i + 1)
        return keep + replace + fill
    return charset[0] * (len(source) + 1)


def _iterate_strings(start: str, sentinel: str | None = None) -> Iterable[str]:
    while start != sentinel:
        yield start
        start = _increment_string(start)


def _check_password(iterable: Iterable[str], digest: str) -> str | None:
    for s in iterable:
        if hashlib.md5(s.encode()).hexdigest() == digest:
            return s
    return None


async def brute_force(
    start: str,
    stop: str,
    digest: str,
    *,
    executor: concurrent.futures.Executor | None = None,
) -> str | None:
    loop = asyncio.get_running_loop()
    check = functools.partial(_check_password, digest=digest)
    combinations = _iterate_strings(start, _increment_string(stop))
    if sys.version_info >= (3, 12):
        chunks: Iterable[tuple[str, ...]] = itertools.batched(combinations, 1024)
    else:
        T_co = TypeVar("T_co", covariant=True)

        def batched(iterable: Iterable[T_co], n: int) -> Iterable[tuple[T_co, ...]]:
            if n < 1:
                raise ValueError("n must be at least one")
            it = iter(iterable)
            while batch := tuple(itertools.islice(it, n)):
                yield batch

        chunks = batched(combinations, 1024)
    futures = [loop.run_in_executor(executor, check, chunk) for chunk in chunks]
    for future in asyncio.as_completed(futures):
        if password := await future:
            if executor:
                executor.shutdown(False, cancel_futures=True)
            return password
    return None


if __name__ == "__main__":
    import argparse

    class Args(argparse.Namespace):
        start: str
        stop: str
        digest: str

    async def main():
        parser = argparse.ArgumentParser()
        for arg in "start", "stop", "digest":
            parser.add_argument(arg)
        args = parser.parse_args(namespace=Args())

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            password = await brute_force(
                args.start, args.stop, args.digest, executor=executor
            )
            print(password or "Not found!")

    asyncio.run(main())
