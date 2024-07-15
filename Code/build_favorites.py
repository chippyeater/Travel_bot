import json
import sqlite3
from call_openai import call_openai_api
import data_abouts as data_abouts

def parse_user_input(user_input):
    messages = [
        {"role": "system", "content": "你是ChatGPT，一个由OpenAI训练的大型语言模型。请尽可能简明扼要地回答。"},
        {"role": "user", "content": f"从以下输入中提取用户想要添加到收藏夹的地点名称：'{user_input}',只回复地点的名称即可,不要有其他多余的字"}
    ]
    return call_openai_api(messages)

favorites_json = {
    "名称": "string",
    "简介": "string",
    "类型": "string",
    "开放时间": "string",
    "预计游览时间": "string",
    "是否需要预定": "string",
    "门票价格": "string",
    "联系方式": "string",
    "网友评价精选": "string[]",
}

# 构建提示信息，确保输出符合期望的JSON格式
def generate_places_prompt(place_name):
    prompt = f"""
    请提供以下地点的详细旅游信息，网友热评可从微博、孤独星球、马蜂窝、Tripadvisor、豆瓣、知乎、小红书、大众点评等平台上精选2-3条有价值的。
    地点名称：{place_name}
    输出格式应为如下JSON：
    {json.dumps(favorites_json, ensure_ascii=False, indent=4)}
    """
    return prompt

def search_place_info(place_name):
    prompt_content = generate_places_prompt(place_name)
    messages = [
        {"role": "system", "content": "你是一个旅行助手，通晓全国旅游热点城市的景点、美食和特别活动的信息，还可以上网搜集网友对这些景点的热评。"},
        {"role": "user", "content": prompt_content}
    ]
    response = call_openai_api(messages)
    favorites = data_abouts.extract_json_from_string(response)
    return favorites

def favorite_exists(name):
    conn = sqlite3.connect('travel.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT COUNT(*)
    FROM favorites
    WHERE name = ?
    ''', (name,))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count > 0

def add_favorite(name, info):
    if not favorite_exists(name):
        conn = sqlite3.connect('travel.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO favorites (
            name, description, type, opening_hours, estimated_visit_time, reservation_required,
            ticket_price, contact_info, selected_reviews
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (info['名称'], info['简介'], info['类型'], info['开放时间'],
                  info['预计游览时间'], info['是否需要预定'], info['门票价格'],
                  info['联系方式'], json.dumps(info['网友评价精选'], ensure_ascii=False)))

        conn.commit()
        conn.close()

def display_favorites():
    conn = sqlite3.connect('travel.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM favorites')
    rows = cursor.fetchall()
    
    for row in rows:
        print(f"景点: {row[1]}")
        print(f"简介: {row[2]}")
        print(f"类型: {row[3]}")
        print(f"开放时间: {row[4]}")
        print(f"预计游览时间: {row[5]}")
        print(f"是否需要预定: {row[6]}")
        print(f"门票价格: {row[7]}")
        print(f"联系方式: {row[8]}")
        print(f"网友评价精选: {row[9]}")
        print("\n")
    
    conn.close()

def search_attraction_infos(user_input):
    # 解析用户输入
    place_name = parse_user_input(user_input)
    # print(f"解析得到的地点名称: {place_name}")
    
    # 搜索地点信息
    place_info = search_place_info(place_name)
    # print(f"获取的地点信息: {place_info}")

    # 添加到收藏夹
    add_favorite(place_name, place_info)

def main(user_input):    
    search_attraction_infos(user_input)


