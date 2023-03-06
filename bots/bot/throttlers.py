import functools
import asyncio
from typing import Coroutine, Literal


def throttler_decorator(
    delay: float,
    measure: Literal["end_to_start", "start_to_start"] = "start_to_start",
):
    delay = delay + 0.0001
    def decorator(actual_func: Coroutine) -> Coroutine:
        queue = None

        async def _single_query(future, args, kwargs):
            try:
                result = await actual_func(*args, **kwargs)
            except Exception as err:
                future.set_exception(err)
            else:
                future.set_result(result)

        async def _work_loop():
            nonlocal queue
            while True:
                try:
                    future, args, kwargs = await asyncio.wait_for(
                        queue.get(), delay
                    )
                except asyncio.TimeoutError:
                    queue = None
                    return
                task = _single_query(future, args, kwargs)
                if measure == "start_to_start":
                    asyncio.create_task(task)
                else:
                    await task
                queue.task_done()
                await asyncio.sleep(delay)

        @functools.wraps(actual_func)
        async def query(*args, **kwargs):
            nonlocal queue
            future = asyncio.Future()
            if queue is None:
                queue = asyncio.Queue()
                asyncio.create_task(_work_loop())
            await queue.put((future, args, kwargs))
            return await future

        return query

    return decorator


class ThrottledResource:
    def __init__(self, delay: float, func_to_throttle: Coroutine):
        self._delay = delay + 0.0001
        self._func = func_to_throttle
        self._queue = asyncio.Queue()
        self._task = None

    def start(self):
        self._task = asyncio.create_task(self._work_loop())

    def stop(self):
        self._task.cancel()
        self._task = None

    async def query(self, params):
        future = asyncio.Future()
        await self._queue.put((future, params))
        result = await future
        return result

    async def _single_response(self, params, future):
        try:
            result = await self._func(params)
        except Exception as err:
            future.set_exception(err)
        else:
            future.set_result(result)

    async def _work_loop(self):
        while True:
            future, params = await self._queue.get()
            asyncio.create_task(self._single_response(params, future))
            self._queue.task_done()
            await asyncio.sleep(self._delay)
