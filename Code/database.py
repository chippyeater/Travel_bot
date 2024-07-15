import sqlite3

def create_travel_database():
    conn = sqlite3.connect('travel.db')
    cursor = conn.cursor()

    # 创建基础信息表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS basic (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    departure TEXT,
    destination TEXT,
    arrival_date TEXT,
    arrival_time TEXT,
    departure_date TEXT,
    departure_time TEXT,
    theme TEXT
    )
    ''')

    # 创建酒店信息表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hotels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    check_in_date TEXT,
    check_out_date TEXT,
    price_per TEXT,
    price_total TEXT,
    booking_link TEXT
    )
    ''')

    # 创建航班信息表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    origin TEXT,
    destination TEXT,
    departure_date TEXT,
    departure_time TEXT,
    arrival_time TEXT,
    flight_id TEXT,
    price TEXT,
    link TEXT,
    contact TEXT
    )
    ''')
    
    # 创建收藏夹
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        type TEXT,
        opening_hours TEXT,
        estimated_visit_time TEXT,
        reservation_required TEXT,
        ticket_price TEXT,
        contact_info TEXT,
        selected_reviews TEXT
    )
    ''')
    
    # 创建行程表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS itinerary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day TEXT,
    attraction_name TEXT,
    description TEXT,
    visit_time TEXT,
    location TEXT,
    reservation_required TEXT,
    ticket_price TEXT,
    contact_info TEXT,
    transportation TEXT,
    additional_notes TEXT
    )
    ''')
    
    # 创建旅行记账表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        item TEXT,
        amount TEXT,
        currency TEXT,
        category TEXT
    )
    ''')

    conn.commit()
    conn.close()

def main():
    create_travel_database()
