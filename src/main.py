import asyncio
import concurrent.futures

from connection import recv, send


async def main():
    reader, writer = await asyncio.open_connection("10.30.56.235", 9999)
    writer.write(b"amogus")
    await writer.drain()
    my_id = await reader.read(6)
    writer.write(my_id)
    await writer.drain()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        try:
            queue = asyncio.Queue[bytes]()
            future = asyncio.gather(recv(reader, queue), send(writer, executor))
            while True:
                end = await queue.get()
                if end.startswith(b"end"):
                    future.cancel()
                    print(end.rsplit(b":", 1)[1].decode())
        except KeyboardInterrupt:
            writer.write(b"failed:end")
            await writer.drain()
            await reader.read()
            return


if __name__ == "__main__":
    asyncio.run(main())
