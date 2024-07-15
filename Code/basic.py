import sqlite3
import json
import call_openai
import data_abouts

# 期望的行程需求JSON格式
requests_json = {
    "出发地": "string",
    "目的地": "string",
    "出发日期": "string",
    "返回日期": "string",
    "旅行主题": "string"
}

# 期望的航班JSON格式
flight_json = {
    "航班信息":
    [{
        "出发地": "string",
        "目的地": "string",
        "出发日期": "string",
        "起飞时间": "string",
        "落地时间": "string",
        "航班号": "string",
        "价格": "string",
        "购买链接": "string",
        "航空公司联系方式": "string"
    }]
}

def generate_details_prompt(user_input):
    prompt = f"""
    请从用户描述中提取出发地、目的地、出发日期、返回日期和旅行主题。
    用户描述：{user_input}
    输出格式应为如下JSON：
    {json.dumps(requests_json, ensure_ascii=False, indent=4)}
    """
    return prompt

def extract_trip_details(user_input):
    prompt_content = generate_details_prompt(user_input)
    messages = [
        {"role": "system", "content": "你是一个旅行助手。"},
        {"role": "user", "content": prompt_content}
    ]
    response = call_openai.call_openai_api(messages)
    details = data_abouts.extract_json_from_string(response)
    return details

def insert_trip_details(db_path, requests, flights):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO basic (departure, destination, arrival_date, arrival_time, departure_date, departure_time, theme)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (requests['出发地'], requests['目的地'], requests['出发日期'], flights['去程航班']['落地时间'],
          requests['返回日期'], flights['返程航班']['起飞时间'], requests['旅行主题']))
    
    conn.commit()
    conn.close()

# 构建提示信息，确保输出符合期望的JSON格式
def generate_flights_prompt(requests, flight_type):
    prompt = f"""
    请根据我的旅游行程信息：{requests}，上网查询至少三个具体可选的{flight_type}航班。
    输出格式应为如下JSON：
    {json.dumps(flight_json, ensure_ascii=False, indent=4)}
    """
    return prompt

def extract_flights(requests, flight_type):
    prompt_content = generate_flights_prompt(requests, flight_type)
    messages = [
        {"role": "system", "content": "你是一个航班预定助手，假如你可以查询各大航空公司在2024年的航班信息并帮用户进行预定（生成模拟的信息，详细的数据）。"},
        {"role": "user", "content": prompt_content}
    ]
    response = call_openai.call_openai_api(messages)
    flights = data_abouts.extract_json_from_string(response)
    flight = select_flight(flights, flight_type)
    return flight

def provide_feedback(flight, flight_type):
    feedback_message = f"""
    你已成功预定{flight_type}：
    航班号：{flight['航班号']}
    出发地：{flight['出发地']}
    目的地：{flight['目的地']}
    出发时间：{flight['出发日期']} {flight['起飞时间']}
    到达时间：{flight['出发日期']} {flight['落地时间']}
    价格：{flight['价格']}
    购买链接：{flight['购买链接']}
    航空公司联系方式：{flight['航空公司联系方式']}
    """
    print(feedback_message)

def select_flight(flights, flight_type):
    print(f"\n可选的{flight_type}：")
    for i, flight in enumerate(flights['航班信息']):
        print(f"{i + 1}. {flight['航班号']} 从 {flight['出发地']} 到 {flight['目的地']} \n出发时间：{flight['出发日期']} {flight['起飞时间']} \n到达时间：{flight['出发日期']} {flight['落地时间']} \n价格：{flight['价格']}")

    choice = int(input(f"请选择一个{flight_type}（输入数字）：")) - 1
    if 0 <= choice < len(flights['航班信息']):
        selected_flight = flights['航班信息'][choice]
        provide_feedback(selected_flight, flight_type)
        return selected_flight
    else:
        print("无效选择")
        return None

# 解析JSON字符串并插入到数据库中
def insert_flight_data(flight, flight_type):
    conn = sqlite3.connect('travel.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO flights (
            type, origin, destination, departure_date, departure_time, arrival_time,
            flight_id, price, link, contact
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            flight_type, flight['出发地'], flight['目的地'], flight['出发日期'], flight['起飞时间'], flight['落地时间'],
            flight['航班号'], flight['价格'], flight['购买链接'], flight['航空公司联系方式']
        ))
    
    conn.commit()
    conn.close()

def main(user_input):
    # 提取出发时间、出发地、目的地等信息
    requests = extract_trip_details(user_input)
    if requests:
        print("请确认您的行程信息：", requests)
        go_flight = extract_flights(requests, "去程航班")
        if go_flight:
            insert_flight_data(go_flight, "去程航班")

        return_flight = extract_flights(requests, "返程航班")
        if return_flight:
            insert_flight_data(return_flight, "返程航班")
            
        insert_trip_details('travel.db', requests, {'去程航班': go_flight, '返程航班': return_flight})

        return requests
    else:
        print("无法提取您的行程信息。")

