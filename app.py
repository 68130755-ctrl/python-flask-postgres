import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, g, redirect, url_for

app = Flask(__name__)

# --- การตั้งค่าฐานข้อมูล PostgreSQL ---
# *** โปรดเปลี่ยนค่าเหล่านี้ให้ตรงกับการตั้งค่าฐานข้อมูลของคุณ ***
# เนื่องจาก DB อยู่บน VM (192.168.37.128) และใช้ชื่อผู้ใช้/รหัสผ่านที่กำหนด
DB_NAME = "ct526"
DB_USER = "test"
DB_PASSWORD = "password"  # <-- เปลี่ยนเป็นรหัสผ่านที่ถูกต้อง!
DB_HOST = "192.168.37.128" # <-- IP ของเครื่อง VM ที่รัน PostgreSQL
DB_PORT = "5432"

# ข้อมูลนักศึกษา
STUDENT_ID = "68130755" # รหัสประจำตัวของคุณ
STUDENT_NAME = "Phatcharaphorn Tain" # ชื่อของคุณ

# --- Functions สำหรับจัดการ Database Connection ---

def connect_db():
    """เชื่อมต่อกับฐานข้อมูล PostgreSQL และคืนค่า Connection"""
    try:
        # ใช้ g (global object ใน Flask) เพื่อเก็บ Connection
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        # พิมพ์ข้อผิดพลาดที่เกิดขึ้นจริงใน Terminal เพื่อการ Debug (สำคัญมาก)
        print(f"Database connection error: {e}")
        return None

@app.before_request
def setup_db():
    """ตั้งค่าการเชื่อมต่อ DB ก่อนแต่ละ Request"""
    # g.db คือ Connection object ที่ใช้ใน Request นั้นๆ
    g.db = connect_db()

@app.teardown_request
def close_db(exception):
    """ปิดการเชื่อมต่อ DB หลังแต่ละ Request เสร็จสิ้น"""
    conn = getattr(g, 'db', None)
    if conn is not None:
        conn.close()

# --- Route Definitions ---

@app.route('/')
def index():
    """Page 1: หน้าแรก แสดงชื่อและรหัสพร้อมลิงก์ไปยัง /movie"""
    return render_template('index.html', 
                           student_name=STUDENT_NAME, 
                           student_id=STUDENT_ID)

@app.route('/movie')
def movie_list():
    """Page 2: แสดงข้อมูลภาพยนตร์จากฐานข้อมูลในรูปแบบตาราง"""
    conn = getattr(g, 'db', None)
    movies = []
    error = None

    if conn is None:
        # หากเชื่อมต่อ DB ไม่สำเร็จ (conn เป็น None)
        error = "ไม่สามารถเชื่อมต่อฐานข้อมูลได้ โปรดตรวจสอบการตั้งค่า DB, IP, และสถานะ PostgreSQL Service"
    else:
        try:
            # ใช้ RealDictCursor เพื่อให้ได้ผลลัพธ์เป็น Dictionary (เข้าถึงด้วยชื่อคอลัมน์ได้)
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Query ข้อมูลทั้งหมดจากตาราง movies
                cur.execute("SELECT MID, M_name, release_date, genre, country FROM movies ORDER BY MID;")
                movies = cur.fetchall()
            
            # Commit (ถึงแม้จะเป็น Read Operation ก็ควรทำ)
            conn.commit()

        except psycopg2.Error as db_error:
            # Rollback หากมีข้อผิดพลาด
            conn.rollback()
            error = f"เกิดข้อผิดพลาดในการ Query ข้อมูล: {db_error}"
        except Exception as e:
            error = f"เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}"

    return render_template('movie.html', movies=movies, error=error)


if __name__ == '__main__':
    # รันแอปพลิเคชัน Flask

    app.run(host='0.0.0.0',port=80, debug=True)