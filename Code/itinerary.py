import sqlite3
from call_openai import call_openai_api
import json
import data_abouts

# 定义期望的JSON格式
spots_json = {
    "景点": [
        {"景点名称": "string", "是否必去": "string", "详细地址": "string"},
    ]
}

itinerary1_json = {
    "行程规划": [
        {
            "Day 1": [
                {"景点名称": "string", "位置": "string"},
            ]
        }
    ]
}

itinerary2_json = {
    "行程规划": [
        {
            "Day 1": [
                {"景点名称": "string", "位置": "string", "预计参观时间段": "string"},
            ]
        }
    ]
}

itinerary3_json = {
    "行程规划": [
        {
            "Day 1": [
                {"景点名称": "string", "位置": "string", "预计参观时间段": "string", "交通": "string"},
            ]
        }
    ]
}

itinerary4_json = {
    "行程规划": [
        {
            "Day 1": [
                {
                    "景点名称": "string", "位置": "string", "预计参观时间段": "string", "交通": "string",
                    "描述": "string", "是否需要预定": "string", "门票价格": "string",
                    "联系方式": "string", "注意事项": "string"
                },
            ]
        }
    ]
}

# 第一步：生成景点详细地址
def generate_address_prompt(favorites, recommendation):
    prompt = f"""
    请为以下景点生成详细地址（精确到街道）：
    必去景点列表：{json.dumps(favorites, ensure_ascii=False, indent=4)}
    推荐去景点列表：{json.dumps(recommendation, ensure_ascii=False, indent=4)}
    输出格式严格按照如下JSON字符串的格式：
    {json.dumps(spots_json, ensure_ascii=False, indent=4)}
    """
    return prompt

def get_spots_addresses(favorites, recommendation):
    prompt_content = generate_address_prompt(favorites, recommendation)
    messages = [
        {"role": "system", "content": "你是一个地图助手，通晓全国旅游热点城市的景点位置信息。"},
        {"role": "user", "content": prompt_content}
    ]
    response = call_openai_api(messages)
    spots = data_abouts.extract_json_from_string(response)
    return spots

# 第二步：将景点分配到各天
def step2_prompt(requests, spots):
    prompt = f"""
    请根据以下景点列表和我的旅游行程信息，将景点合理分配到每天的行程中，每天可以有多个景点：
    旅游行程信息：{json.dumps(requests, ensure_ascii=False, indent=4)}
    景点列表：{json.dumps(spots, ensure_ascii=False, indent=4)}
    输出格式严格按照如下JSON字符串的格式：
    {json.dumps(itinerary1_json, ensure_ascii=False, indent=4)}
    """
    return prompt

def step2(requests, spots):
    prompt_content = step2_prompt(requests, spots)
    messages = [
        {"role": "system", "content": "你是一个行程规划助手，擅长根据用户的个性化需求定制日程或行程。"},
        {"role": "user", "content": prompt_content}
    ]
    response = call_openai_api(messages)
    itinerary_days = data_abouts.extract_json_from_string(response)
    return itinerary_days

# 第三步：根据景点位置的分布安排餐食和时间段
def step3_prompt(itinerary_days):
    prompt = f"""
    请根据以下行程安排的景点，开放时间和预计游览时间，为每个景点安排具体的时间段，规划每天多个景点的参观顺序并将推荐的美食作为景点添加到行程中：
    行程安排：{json.dumps(itinerary_days, ensure_ascii=False, indent=4)}
    输出格式严格按照如下JSON字符串的格式：
    {json.dumps(itinerary2_json, ensure_ascii=False, indent=4)}
    """
    return prompt

def step3(itinerary_days):
    prompt_content = step3_prompt(itinerary_days)
    messages = [
        {"role": "system", "content": "你是一个旅行助手，通晓全国旅游热点城市的景点和美食的信息。"},
        {"role": "user", "content": prompt_content}
    ]
    response = call_openai_api(messages)
    time_schedules = data_abouts.extract_json_from_string(response)
    return time_schedules

# 第四步：交通
def step4_prompt(itinerary_days):
    prompt = f"""
    请根据以下行程安排每个景点具体的时间段和距离，生成景点之间转换时最推荐的一种交通方式和预计通行时间（例如：“推荐打车，大约20分钟”）：
    行程安排：{json.dumps(itinerary_days, ensure_ascii=False, indent=4)}
    输出格式严格按照如下JSON字符串的格式：
    {json.dumps(itinerary3_json, ensure_ascii=False, indent=4)}
    """
    return prompt

def step4(itinerary_days):
    prompt_content = step4_prompt(itinerary_days)
    messages = [
        {"role": "system", "content": "你是一个旅行助手，通晓全国旅游热点城市的交通信息。"},
        {"role": "user", "content": prompt_content}
    ]
    response = call_openai_api(messages)
    time_schedules = data_abouts.extract_json_from_string(response)
    return time_schedules

# 第五步：其他信息
def step5_prompt(itinerary_days):
    prompt = f"""
    请根据以下行程安排的每个景点生成描述、是否需要预定、门票价格、联系方式和注意事项：
    行程安排：{json.dumps(itinerary_days, ensure_ascii=False, indent=4)}
    输出格式严格按照如下JSON字符串的格式：
    {json.dumps(itinerary4_json, ensure_ascii=False, indent=4)}
    """
    return prompt

def step5(itinerary_days):
    prompt_content = step5_prompt(itinerary_days)
    messages = [
        {"role": "system", "content": "你是一个旅行助手，通晓全国旅游热点城市的景点和活动信息。"},
        {"role": "user", "content": prompt_content}
    ]
    response = call_openai_api(messages)
    time_schedules = data_abouts.extract_json_from_string(response)
    return time_schedules

# 插入行程安排到数据库
def insert_itinerary_data(data):
    conn = sqlite3.connect('travel.db')
    cursor = conn.cursor()
    
    for day_itinerary in data['行程规划']:
        for day, spots in day_itinerary.items():
            for spot in spots:
                if isinstance(spot, list): spot = spot[0]
                cursor.execute('''
                INSERT INTO itinerary (
                    day, attraction_name, description, visit_time, location, transportation,
                    reservation_required, ticket_price, contact_info, additional_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    day, spot['景点名称'], spot['描述'], spot['预计参观时间段'], spot['位置'], spot.get('交通', ''),
                    spot['是否需要预定'], spot['门票价格'], spot['联系方式'], spot['注意事项']
                ))
    
    conn.commit()
    conn.close()

# 获取当前行程安排
def get_current_itinerary(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT day, attraction_name, description, visit_time, location, transportation, reservation_required, ticket_price, contact_info, additional_notes
    FROM itinerary
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    itinerary = {}
    for row in rows:
        day = row[0]
        if day not in itinerary:
            itinerary[day] = []
        itinerary[day].append({
            "景点名称": row[1], "描述": row[2], "预计参观时间段": row[3], "位置": row[4], "交通": row[5],
            "是否需要预定": row[6], "门票价格": row[7], "联系方式": row[8], "注意事项": row[9]
        })
    return itinerary

def main(requests, favorites, recommendations):
    # 生成景点的详细地址
    after_step1 = get_spots_addresses(favorites, recommendations)
    
    # 分配景点到各天
    after_step2 = step2(requests, after_step1)

    # 分配餐食和每天的时间安排
    after_step3 = step3(after_step2)

    # 安排交通
    after_step4 = step4(after_step3)
    
    # 其他信息
    after_step5 = step5(after_step4)

    # 插入行程安排到数据库
    insert_itinerary_data(after_step5)

    return get_current_itinerary('travel.db')

