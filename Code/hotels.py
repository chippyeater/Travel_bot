import sqlite3
import json
import call_openai
import data_abouts

# 期望的酒店JSON格式
hotel_json = {
    "酒店":[
        {
            "名字": "string",
            "入住日期": "string",
            "离店日期": "string",
            "每晚价格": "string",
            "总价": "string",
            "购买链接": "string"
        }
    ]
}

def extract_hotel_type(user_input):
    messages = [
        {"role": "system", "content": "你是一个旅行助手。"},
        {"role": "user", "content": "请从用户描述中提取对酒店的星级要求，只回复几星级即可，不要有多余的字。"}
    ]
    response = call_openai.call_openai_api(messages)
    return response

# 构建提示信息，确保输出符合期望的JSON格式
def generate_hotels_prompt(itinerary, hotel_type):
    prompt = f"""
    请根据我的旅游行程信息：{itinerary}，上网查询至少三个具体可选的{hotel_type}酒店。
    输出格式应为如下JSON：
    {json.dumps(hotel_json, ensure_ascii=False, indent=4)}
    """
    return prompt

def extract_hotels(itinerary, hotel_type):
    prompt_content = generate_hotels_prompt(itinerary, hotel_type)
    messages = [
        {"role": "system", "content": "你是一个酒店预定助手，假如你可以查询各大酒店的信息并帮用户进行预定（生成模拟的信息，详细的数据）。"},
        {"role": "user", "content": prompt_content}
    ]
    response = call_openai.call_openai_api(messages)
    hotels = data_abouts.extract_json_from_string(response)
    selected_hotel = select_hotel(hotels)
    return selected_hotel

def provide_feedback(hotel):
    feedback_message = f"""
    你已成功预定酒店：{hotel['名字']}
    入住日期：{hotel['入住日期']}
    离店日期：{hotel['离店日期']}
    每晚价格：{hotel['每晚价格']}
    总价：{hotel['总价']}
    购买链接：{hotel['购买链接']}
    """
    print(feedback_message)

def select_hotel(hotels):
    for i in range(len(hotels['酒店'])):
        hotel = hotels['酒店'][i]
        print(f"{i + 1}. 名字：{hotel['名字']}\n入住日期：{hotel['入住日期']}\n离店日期：{hotel['离店日期']}\n每晚价格：{hotel['每晚价格']}\n总价：{hotel['总价']}\n购买链接：{hotel['购买链接']}\n")

    choice = int(input("请选择一个酒店（输入数字）：")) - 1
    if 0 <= choice < len(hotels['酒店']):
        selected_hotel = hotels['酒店'][choice]
        provide_feedback(selected_hotel)
        return selected_hotel
    else:
        print("无效选择")
        return None

# 解析JSON字符串并插入到数据库中
def insert_hotel_data(hotel):
    conn = sqlite3.connect('travel.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO hotels (
            name, check_in_date, check_out_date, price_per, price_total, booking_link
        ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            hotel['名字'], hotel['入住日期'], hotel['离店日期'], hotel['每晚价格'], hotel['总价'], hotel['购买链接']
        ))
    
    conn.commit()
    conn.close()

def main(itinerary, user_input):
    if itinerary:
        hotel_type = extract_hotel_type(user_input)
        selected_hotel = extract_hotels(itinerary, hotel_type)
        if selected_hotel:
            insert_hotel_data(selected_hotel)
        return selected_hotel
    else:
        print("无法提取您的行程信息。")
        return None

