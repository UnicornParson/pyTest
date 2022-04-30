#!/usr/bin/env python3
import os
import time
import psycopg2
import asyncio

PART_SIZE = int(10**6 / 2)

async def make_cur():
    con = psycopg2.connect(
        database="dataset",
        user="******",
        password="******!",
        host="127.0.0.1",
        port="5432"
    )
    cur = con.cursor()
    if not con or not cur:
        print("no con")
        exit(1)
    return con, cur


async def get_count() -> int:
    con, cur = await make_cur()
    cur.execute("SELECT count(id) FROM public.pressure;")
    count = cur.fetchone()[0]
    print(count)
    con.close()
    return count

async def extractPart(start, count, path):
    con, cur = await make_cur()
    print("write %d-%d to %s" % (start, start + PART_SIZE, path))
    q = "SELECT * FROM public.pressure LIMIT %d OFFSET %d;" % (count, start)
    cur.execute(q)
    with open(path, 'w') as f:
        for row in cur.fetchall():
            # (1398676, 29.9, 99845.0, 123.87, 138.56, datetime.datetime(2022, 2, 6, 20, 5, 5, 952287))
            f.write("%d, %f, %f, %f, %f, %s \n" % row)
        f.flush()
        f.close()
    con.close()

async def main():
    count = await get_count()
    print("count: %d" % count)
    producers = [asyncio.create_task(extractPart(start,
                                                 PART_SIZE,
                                                 ("pressure_%d-%d.csv" % (start, start + PART_SIZE))))
                 for start in range(0, count, PART_SIZE)]
    await asyncio.gather(*producers)


if __name__ == "__main__":
    asyncio.run(main(), debug=True)