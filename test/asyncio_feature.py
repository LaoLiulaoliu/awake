#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio

future = asyncio.Future()

async def coro1():
  await asyncio.sleep(1)
  future.set_result('data')

async def coro2():
  print(await future)

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait([
  coro1(), 
  coro2()
]))
loop.close()
