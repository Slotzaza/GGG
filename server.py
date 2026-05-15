from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
from datetime import datetime

app = FastAPI()

conn = sqlite3.connect("db.sqlite", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS licenses(
    license_key TEXT,
    hwid TEXT,
    expire_date TEXT
)
""")

conn.commit()

class Data(BaseModel):
    key: str
    hwid: str

@app.post("/check")
def check(data: Data):

    cur.execute(
        "SELECT hwid, expire_date FROM licenses WHERE license_key=?",
        (data.key,)
    )

    row = cur.fetchone()

    if row is None:
        return {"success": False}

    saved_hwid = row[0]

    expire_date = row[1]

    if datetime.now() > datetime.fromisoformat(expire_date):
        return {"success": False}

    if saved_hwid == "":
        cur.execute(
            "UPDATE licenses SET hwid=? WHERE license_key=?",
            (data.hwid, data.key)
        )

        conn.commit()

        return {"success": True}

    if saved_hwid != data.hwid:
        return {"success": False}

    return {"success": True}