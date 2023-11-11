#!/usr/bin/env python

import argparse
import hashlib
import itertools
from collections.abc import Iterable
from concurrent import futures


class _Args:
    start: str
    end: str
    digest: str


def _increment_string(string: str) -> str:
    # if the last character is z it needs to not overflow
    if string[-1] == "z":
        try:
            return _increment_string(string[:-1]) + "a"
        # if the string is empty the length needs to be increased
        except IndexError:
            return (len(string) + 1) * "a"
    return string[:-1] + chr(ord(string[-1]) + 1)


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
        results = executor.map(
            _check_password, _iterate_strings(start, end), itertools.repeat(digest)
        )
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
