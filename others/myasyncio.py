import asyncio

async def greet(name):
    print(f"Hello, {name}!")
    asyncio.sleep(1)
    print(f"Goodbye, {name}!")

async def main():
    await asyncio.gather(
        greet("Alice"),
        greet("Bob"),
        greet("Charlie")
    )
    

asyncio.run(main())

class AsyncContextManager:
    async def __aenter__(self):
        print("Entering context")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        print("Exiting context")

async def main1():
    async with AsyncContextManager() as manager:
        print("Inside context 1")

async def main2():
    async with AsyncContextManager() as manager:
        print("Inside context 2")

async def main3():
    async with AsyncContextManager() as manager:
        print("Inside context 3")

async def _main():
    await asyncio.gather(
        main1(),
        main2(),
        main3()
    )
asyncio.run(_main())

async def async_generator():
    for i in range(3):
        await asyncio.sleep(1)
        yield i

async def main():
    async for value in async_generator():
        print(value)

asyncio.run(main())
