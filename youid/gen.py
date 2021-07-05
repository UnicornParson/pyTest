#!/usr/bin/env python3.8
import sys
if not hasattr(sys, "version_info") or sys.version_info < (3, 5):
    raise SystemExit("This program requires Python 3.5 or later.")
import sqlite3
from datetime import datetime
import time
from reprint import output

alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_"
alphabetSZ = len(alphabet)
initialIdStr = alphabet[0] * 11
lastIdStr = alphabet[alphabetSZ - 1] * 11
progressOutputLine = None
createtableStr = """CREATE TABLE if not exists "youids" (
	"seed"	INTEGER NOT NULL,
	"idstr"	TEXT NOT NULL,
	PRIMARY KEY("seed")
);"""

def seedToStr(seed)->str:
  subindex = seed
  rc = ""
  while subindex >= alphabetSZ:
    rc = alphabet[int(subindex % alphabetSZ)] + rc
    subindex /= alphabetSZ
  rc = alphabet[int(subindex % alphabetSZ)] + rc
  return rc

def makeSeedBound(seedStr, uppercount, lowercount) -> str:
  l = len(seedStr)
  if l > uppercount:
    return seedStr[(-1 * uppercount):]
  return str(alphabet[0] * (lowercount - l)) + seedStr

def strToSeed(s):
  pow = 0
  rc = 0
  for ch in s[::-1]:
    pos = alphabet.find(ch)
    if pos < 0:
      raise ValueError("unknown symbol " + ch  + " in " + s)
    rc += pos * (alphabetSZ ** pow )
    pow += 1
  return rc

def progress(status, remaining, total):
    print(f'copied {total-remaining} from {total}...')


lastIdSeed = strToSeed(lastIdStr)
countPerRun = 100
countPerCommit = 30;
countPerTimeCheck = 10
try:
  sys.stdout.flush()
  sqlite_connection = sqlite3.connect('id.db')
  buSeed = datetime.now().strftime("%d_%m_%Y_%H_%M_%S-%f")
  buName = "id_backup.%s.db" % buSeed
  backup_con = sqlite3.connect(buName)
  print("make backup to " + buName)
  with backup_con:
    sqlite_connection.backup(backup_con, pages=1, progress=progress)

  cursor = sqlite_connection.cursor()
  cursor.execute(createtableStr)
  sqlite_connection.commit()
  cursor.execute("select max(seed) from youids")
  rows = cursor.fetchall()
  initialSeed = 0
  for r in rows:
    initialSeed = int(r[0]) + 1
  commitIndex = 0
  timeIndex = 0
  t0 = time.time()
  for i in range (initialSeed, lastIdSeed):
    s = makeSeedBound(seedToStr(i), 11, 11)
    print(str(i) + "->" + s + " << " + str(strToSeed(s)))
    sys.stdout.flush()
    q = "INSERT INTO 'main'.'youids'('seed','idstr') VALUES (%d,'%s');" % (i, s)
    cursor.execute(q)
    commitIndex += 1
    timeIndex += 1
    if commitIndex >= countPerCommit:
      sqlite_connection.commit()
      commitIndex = 0
    if timeIndex >= countPerTimeCheck:
      delta = time.time() - t0
      print(">>>> " +  str(10.0 / delta) + " ids per second")
      sys.stdout.flush()
      t0 = time.time()
      timeIndex = 0


    
except sqlite3.Error as error:
    print("sqlite connection error", error)
finally:
    if (sqlite_connection):
        sqlite_connection.close()
