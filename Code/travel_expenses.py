import sqlite3
import json
from call_openai import call_openai_api
import data_abouts


class TravelExpenses:
    def __init__(self, db_name='travel.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            item TEXT,
            amount TEXT,
            currency TEXT,
            category TEXT
        )
        ''')

    def add_expense(self, expense_json):
        # 从JSON数据中提取字段
        date = expense_json["日期"]
        item = expense_json["物品"]
        amount = expense_json["支出金额"]
        currency = expense_json["数目"]
        category = expense_json["花销类别"]

        # 插入数据到数据库
        self.cursor.execute('''
        INSERT INTO expenses (date, item, amount, currency, category)
        VALUES (?, ?, ?, ?, ?)
        ''', (date, item, amount, currency, category))
        self.conn.commit()
    def update_expense(self, expense_id, date, item, amount, currency, category):
        self.cursor.execute('''
        UPDATE expenses
        SET date = ?, item = ?, amount = ?, currency = ?, category = ?
        WHERE id = ?
        ''', (date, item, amount, currency, category, expense_id))
        self.conn.commit()

    def delete_expense(self, expense_id):
        self.cursor.execute('''
        DELETE FROM expenses WHERE id = ?
        ''', (expense_id,))
        self.conn.commit()

    def get_expenses(self):
        self.cursor.execute('SELECT * FROM expenses')
        return self.cursor.fetchall()

    def __del__(self):
        self.conn.close()


expense_json = {
    "日期": "string",
    "支出金额": "string",
    "物品": "string",
    "数目": "string",
    "剩余": "string",
    "花销类别": "string"
}

# 构建提示信息，确保输出符合期望的JSON格式
def generate_expenses_prompt(user_input):
    prompt = f"""
    从以下输入中提取用户想要记的账：'{user_input}'。
    输出格式应为如下JSON：
    {json.dumps(expense_json, ensure_ascii=False, indent=4)}
    """
    return prompt

def extract_expenses(user_input):
    prompt_content = generate_expenses_prompt(user_input)
    messages = [
        {"role": "system", "content": "你是一个自主记账智能机器人，能够自动识别输入的文本中的记账类型、物品、数目、金额等内容。"},
        {"role": "user", "content": prompt_content}
    ]
    response = call_openai_api(messages)
    expense = data_abouts.extract_json_from_string(response)
    return expense


def main(user_input):
    # 解析用户输入
    expense = extract_expenses(user_input)
    # print(f"解析得到的地点名称: {expense}")

    return expense