import asyncio

from helpers import decrypt


async def main():
    reader, writer = await asyncio.open_connection()
    writer.write(b"amogus")
    await writer.drain()
    my_id = await reader.read()
    writer.write(my_id)
    await writer.drain()
    while True:
        try:
            data = await asyncio.wait_for(reader.read(), 60)
            writer.write(b"ok")
            start, stop, digest = data.decode().split(",")
            result = decrypt(start, stop, digest)
            if result is not None:
                writer.write(f"success:{result}".encode())
                await writer.drain()
                if await asyncio.wait_for(reader.read(), 60) == b"ok":
                    success = True
                    break
            else:
                writer.write(b"failed")
                await writer.drain()
                await reader.read()
                writer.write(b"next")
                await writer.drain()
        except TimeoutError:
            success = False
            break
    if success:
        writer.write(b"end:success")
        await writer.drain()
        await reader.read()
    else:
        writer.write(b"end:exit")


if __name__ == "__main__":
    asyncio.run(main())
