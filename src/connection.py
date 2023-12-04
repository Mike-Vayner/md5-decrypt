import asyncio
import concurrent.futures

from brute_force import brute_force

rqueue = asyncio.Queue[bytes]()


async def send(writer: asyncio.StreamWriter, executor: concurrent.futures.Executor):
    while True:
        data = await rqueue.get()
        if data == b"ok":
            continue
        writer.write(b"ok")
        await writer.drain()
        start, stop, digest = (
            part.split(b":")[1].decode() for part in data.split(b",")
        )
        result = await brute_force(start, stop, digest, executor=executor)
        if result is None:
            writer.write(b"failed:next")
        else:
            writer.write(f"success:{result}".encode())
        await writer.drain()


async def recv(reader: asyncio.StreamReader, queue: asyncio.Queue[bytes]):
    while True:
        data = await reader.read(128)
        if data.startswith(b"end"):
            await queue.put(data)
            return
        await rqueue.put(data)
