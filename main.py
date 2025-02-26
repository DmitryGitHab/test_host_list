# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
import sqlite3
import datetime
import csv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def main():
    return FileResponse("index.html")


# Модель для валидации данных
class Server(BaseModel):
    ip: str
    ping: int
    received_data_percent: int
    lost_data_percent: int

    # @__pydantic_validator__('ip')
    # def validate_ip(cls, v):
    #     import re
    #     if not re.match(r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$', v):
    #         raise ValueError('Invalid IP address')
    #     return v

# Создание базы данных
def init_db():
    with sqlite3.connect('servers.db') as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            ping INTEGER NOT NULL,
            received_data_percent INTEGER NOT NULL,
            lost_data_percent INTEGER NOT NULL,
            last_ping_date TEXT NOT NULL
        )
        ''')
        conn.commit()

# Инициализация базы данных при старте
init_db()

# Добавление сервера
@app.post("/servers/")
async def add_server(server: Server):
    with sqlite3.connect('servers.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO servers (ip, ping, received_data_percent, lost_data_percent, last_ping_date)
        VALUES (?, ?, ?, ?, ?)
        ''', (server.ip, server.ping, server.received_data_percent, server.lost_data_percent, datetime.datetime.now().isoformat()))
        conn.commit()
        return {"message": "Server added successfully"}

# Получение списка серверов
@app.get("/servers/")
async def get_servers():
    with sqlite3.connect('servers.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM servers')
        servers = cursor.fetchall()
        return {"servers": servers}

# Редактирование сервера
@app.put("/servers/{server_id}")
async def update_server(server_id: int, server: Server):
    with sqlite3.connect('servers.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE servers
        SET ip = ?, ping = ?, received_data_percent = ?, lost_data_percent = ?, last_ping_date = ?
        WHERE id = ?
        ''', (server.ip, server.ping, server.received_data_percent, server.lost_data_percent, datetime.datetime.now().isoformat(), server_id))
        conn.commit()
        return {"message": "Server updated successfully"}

# Удаление сервера
@app.delete("/servers/{server_id}")
async def delete_server(server_id: int):
    with sqlite3.connect('servers.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM servers WHERE id = ?', (server_id,))
        conn.commit()
        return {"message": "Server deleted successfully"}

# Экспорт данных в CSV
@app.get("/export/")
async def export_csv():
    with sqlite3.connect('servers.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM servers')
        servers = cursor.fetchall()
        with open('servers.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['id', 'ip', 'ping', 'received_data_percent', 'lost_data_percent', 'last_ping_date'])
            writer.writerows(servers)
        return {"message": "Data exported to servers.csv"}

# Импорт данных из CSV
@app.post("/import/")
async def import_csv():
    with sqlite3.connect('servers.db') as conn:
        cursor = conn.cursor()
        with open('servers.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Пропуск заголовка
            for row in reader:
                cursor.execute('''
                INSERT INTO servers (ip, ping, received_data_percent, lost_data_percent, last_ping_date)
                VALUES (?, ?, ?, ?, ?)
                ''', (row[1], int(row[2]), int(row[3]), int(row[4]), row[5]))
            conn.commit()
        return {"message": "Data imported from servers.csv"}