#!/usr/bin/env python

import argparse
import functools
import hashlib
from collections.abc import Iterable
from concurrent import futures


class _Args:
    start: str
    end: str
    digest: str


def _increment_string(string: str) -> str:
    for i in range(-1, -len(string) - 1, -1):
        if string[i] != "z":
            return f"{string[:i]}{chr(ord(string[i]) + 1)}{'a' * -(i + 1)}"
    return "a" * (len(string) + 1)


def _iterate_strings(start: str, end: str) -> Iterable[str]:
    yield start
    while start != end:
        start = _increment_string(start)
        yield start


def _check_password(password: str, digest: str) -> str | None:
    if hashlib.md5(password.encode()).hexdigest() == digest:
        return password
    return None


def decrypt(start: str, end: str, digest: str) -> str | None:
    if len(end) < len(start):
        raise ValueError
    with futures.ProcessPoolExecutor() as executor:
        check = functools.partial(_check_password, digest=digest)
        results = executor.map(check, _iterate_strings(start, end), chunksize=128)
        for res in results:
            if res is not None:
                executor.shutdown(False, cancel_futures=True)
                return res
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("start")
    parser.add_argument("end")
    parser.add_argument("digest")
    args = parser.parse_args(namespace=_Args)

    password = decrypt(args.start, args.end, args.digest)
    print(password or "Password not found")


if __name__ == "__main__":
    main()
