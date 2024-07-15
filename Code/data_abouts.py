import json
import re

def extract_json_from_string(input_string):
    # 使用正则表达式找到 JSON 数据
    json_pattern = re.compile(r'\{.*\}', re.DOTALL)
    match = json_pattern.search(input_string)
    
    if match:
        json_string = match.group(0)
        try:
            json_data = json.loads(json_string)
            return json_data
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print("error!!!!!!!\n", json_string)
            return None
    else:
        print("未找到JSON数据")
        print("error!!!!!!!\n", input_string)
        return None
    
def print_list(list_of_dicts, key):
    values = [d[key] for d in list_of_dicts if key in d]
    
    if len(values) == 0:
        return ""
    elif len(values) == 1:
        return values[0]
    else:
        return ", ".join(values[:-1]) + "和" + values[-1]