import asyncio
import time


async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what, time.strftime('%X'))


async def main1():
    print(f"started at {time.strftime('%X')}")

    # Nothing happens if we just call "say_after(1, 'hello')".
    # A coroutine object is created but not awaited,
    # so it *won't run at all*.
    # say_after(1, 'hello')

    await say_after(1, 'hello')
    await say_after(2, 'world')

    print(f"finished at {time.strftime('%X')}")


async def main2():
    # Schedule say_after(1, 'hello') to run soon concurrently
    # with "main()".
    task1 = asyncio.create_task(
        say_after(1, 'hello'))

    task2 = asyncio.create_task(
        say_after(2, 'world'))

    print(f"started at {time.strftime('%X')}")

    # "task1" can now be used to cancel "nested()", or
    # can simply be awaited to wait until it is complete:

    # Wait until both tasks are completed (should take
    # around 2 seconds.)
    await task1
    await task2

    print(f"finished at {time.strftime('%X')}")


if __name__ == '__main__':
    # asyncio.run(main1())
    asyncio.run(main2())
