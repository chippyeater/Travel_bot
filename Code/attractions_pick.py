import requests
import json
import sqlite3
from call_openai import call_openai_api
import data_abouts

# 期望的景点推荐JSON格式
recommendation_json = {
    "景点":
    [{
        "景点名称": "string",
        "描述": "string",
        "游览时间": "string",
        "位置": "string",
        "是否需要预定": "string",
        "门票价格": "string",
    },]
}



def get_favorites_by_city(requests):
    city_name = requests['目的地']
    conn = sqlite3.connect('travel.db')
    conn.row_factory = sqlite3.Row  # 将行工厂设置为 Row，允许通过列名访问
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT name, type, description FROM favorites WHERE description LIKE ?
    ''', (f"%{city_name}%",))
    
    rows = cursor.fetchall()
    conn.close()
    
    # 将每一行转换为字典
    favorites = [dict(row) for row in rows]
    return favorites



# 构建提示信息，确保输出符合期望的JSON格式
def generate_recommendations_prompt(requests, favorites):
    prompt = f"""
    请根据用户的行程需求{requests}，收藏景点:{favorites}，分析用户的喜好并据此推荐多个（除了收藏经典以外的）景点和最近的特别活动。
    输出格式应为如下JSON：
    {json.dumps(recommendation_json, ensure_ascii=False, indent=4)}
    """
    return prompt

def get_recommendations(requests, favorites):
    prompt_content = generate_recommendations_prompt(requests, favorites)
    messages = [
        {"role": "system", "content": "你是一个旅行助手，通晓全国旅游热点城市的景点、美食和特别活动的信息。"},
        {"role": "user", "content": prompt_content}
    ]
    response = call_openai_api(messages)
    recommendations = data_abouts.extract_json_from_string(response)
    return recommendations



def main(requests):
    if requests:
        # 获取收藏夹中的必去景点
        favorites = get_favorites_by_city(requests)

        # 获取网上推荐的景点
        recommendations = get_recommendations(requests, favorites)['景点']
        
        return favorites, recommendations
    else:
        print("无法提取行程详情。")
