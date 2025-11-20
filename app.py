import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, g, redirect, url_for

app = Flask(__name__)

# --- การตั้งค่าฐานข้อมูล PostgreSQL ---

DB_NAME = "ct526"
DB_USER = "test"
DB_PASSWORD = "password"  
DB_HOST = "192.168.37.128" 
DB_PORT = "5432"

# ข้อมูลนักศึกษา
STUDENT_ID = "68130755" 
STUDENT_NAME = "Phatcharaphorn Tain" 

# --- Connect Database ---

def connect_db():
    
    try:
       
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except Exception as e:
      
        print(f"Database connection error: {e}")
        return None

@app.before_request
def setup_db():
    """ตั้งค่าการเชื่อมต่อ DB ก่อนแต่ละ Request"""

    g.db = connect_db()

@app.teardown_request
def close_db(exception):
    """ปิดการเชื่อมต่อ DB หลังแต่ละ Request เสร็จสิ้น"""
    conn = getattr(g, 'db', None)
    if conn is not None:
        conn.close()

# --- Route ---

@app.route('/')
def index():
   
    return render_template('index.html', 
                           student_name=STUDENT_NAME, 
                           student_id=STUDENT_ID)

@app.route('/movie')
def movie_list():
    
    conn = getattr(g, 'db', None)
    movies = []
    error = None

    if conn is None:
        
        error = "ไม่สามารถเชื่อมต่อฐานข้อมูลได้ โปรดตรวจสอบการตั้งค่า DB, IP, และสถานะ PostgreSQL Service"
    else:
        try:
            
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
              
                cur.execute("SELECT MID, M_name, release_date, genre, country FROM movies ORDER BY MID;")
                movies = cur.fetchall()
            
           
            conn.commit()

        except psycopg2.Error as db_error:
           
            conn.rollback()
            error = f"เกิดข้อผิดพลาดในการ Query ข้อมูล: {db_error}"
        except Exception as e:
            error = f"เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}"

    return render_template('movie.html', movies=movies, error=error)

 # รันแอปพลิเคชัน Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80, debug=True)