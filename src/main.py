import hashlib
import time


def increment_string(string: str) -> str:
    # if the last character is z it needs to not overflow
    if string[-1] == "z":
        try:
            return increment_string(string[:-1]) + "a"
        # if the string is empty the length needs to be increased
        except IndexError:
            return (len(string) + 1) * "a"
    return string[:-1] + chr(ord(string[-1]) + 1)


def decrypt(start: str, end: str, digest: bytes) -> str:
    if len(end) < len(start):
        raise ValueError
    while start != end:
        if hashlib.md5(start.encode()).digest() == digest:
            return start
        start = increment_string(start)
    return ""


def main():
    start = time.perf_counter()
    print(decrypt("aaaaaaaa", "zzzzzzzz", hashlib.md5(b"abcdefgh").digest()))
    end = time.perf_counter()
    print(end - start)


if __name__ == "__main__":
    main()
