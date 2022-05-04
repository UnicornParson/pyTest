#!/usr/bin/env python3
import os
import sys
import time
import psycopg2
import asyncio
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import table
import requests

PART_SIZE = int(10**6 / 2)
ENV_URL = "http://192.168.0.6/env.json"

def mprint(msg):
    print(msg)
    sys.stdout.flush()

async def make_cur():
    resp = requests.get(url=ENV_URL)
    envdata = resp.json()["pressure"]

    print(envdata)
    con = psycopg2.connect(
        database=envdata["database"],
        user=envdata["user"],
        password=envdata["password"],
        host=envdata["host"],
        port=envdata["port"]

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
    mprint(count)
    con.close()
    return count

async def extractPart(start, count, path):
    con, cur = await make_cur()
    mprint("write %d-%d to %s" % (start, start + PART_SIZE, path))
    q = "SELECT * FROM public.pressure ORDER BY dt ASC LIMIT %d OFFSET %d;" % (count, start)
    cur.execute(q)
    columns = ['i','Date', 'Pressure']
    
    idList = []
    pressureList = []
    dtList = []
    columns = ["id", "temperature", "pressure", "altitude", "realaltitude", "dt"]
    df = pd.DataFrame.from_records(cur.fetchall(), columns = columns)
    mprint(df.head())
    df.set_index(columns[0])
    con.close()
    df.to_csv(path_or_buf = (path + ".csv"), columns=columns, header=True, mode="w", index=False)
    df.plot(x="dt", y=["pressure"], figsize=(15, 9))
    plt.savefig(fname = (path + ".png"), format = "png")

async def main():
    mprint("calculate total records count...")
    count = await get_count()
    mprint("count: %d" % count)
    producers = [asyncio.create_task(extractPart(start,
                                                 PART_SIZE,
                                                 ("pressure_%d-%d" % (start, start + PART_SIZE))))
                 for start in range(0, count, PART_SIZE)]
    await asyncio.gather(*producers, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main(), debug=True)
    ## python 3.5 hack
    #loop = asyncio.new_event_loop()
    #loop.run_until_complete(main())