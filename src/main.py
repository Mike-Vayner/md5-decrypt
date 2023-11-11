#!/usr/bin/env python

import argparse
import hashlib


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


def decrypt(start: str, end: str, digest: str) -> str | None:
    if len(end) < len(start):
        raise ValueError
    while start != end:
        if hashlib.md5(start.encode()).hexdigest() == digest:
            return start
        start = _increment_string(start)
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
