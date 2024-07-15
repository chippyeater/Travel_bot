# main.py
import database
import basic
import attractions_pick
import hotels
import data_abouts
import build_favorites
import itinerary
import travel_expenses
from travel_expenses import TravelExpenses

def format_itinerary(itinerary):
    for day, attractions in itinerary.items():
        print(f"{day}:")
        for attraction in attractions:
            print(f"  景点名称: {attraction['景点名称']}")
            print(f"  描述: {attraction['描述']}")
            print(f"  预计参观时间段: {attraction['预计参观时间段']}")
            print(f"  位置: {attraction['位置']}")
            print(f"  交通: {attraction['交通']}")
            print(f"  是否需要预定: {attraction['是否需要预定']}")
            print(f"  门票价格: {attraction['门票价格']}")
            print(f"  联系方式: {attraction.get('联系方式', '无')}")
            print(f"  注意事项: {attraction['注意事项']}")
            print("\n")


def test():
    print("开始执行一站式旅游行程规划服务...")
    
    # 执行 database.py
    print("执行数据库初始化...")
    database.main()
    
    # 执行 build_favorites.py
    print("处理用户喜好...")
    
    places = [
        "故宫",
        "天坛",
        "颐和园",
        "圆明园"
    ]

    for place in places:
        build_favorites.main(f"我想将{place}加入收藏夹。")

    # 显示收藏夹内容
    print("收藏夹目前状态：\n")
    build_favorites.display_favorites()
    
    input1 = "我下周三打算从沈阳出发去北京玩儿4天，可以帮我规划一下行程吗？"
    requests = basic.main(input1)

    # 执行 attractions_pick.py
    print("初始景点筛选...")
    favorites, recommendations = attractions_pick.main(requests)
    
    print("检索到您的收藏夹里该城市的景点有:", data_abouts.print_list(favorites, "name"))
    print("根据您的喜好推荐的景点有:", data_abouts.print_list(recommendations, "景点名称"))

    itinerary_final = itinerary.main(requests, recommendations, favorites)
    print("当前您的行程如下：\n")
    format_itinerary(itinerary_final)
    
    # 执行 hotel.py
    print("搜索及酒店预定...\n请输入想要预定的酒店星级：")
    input2 = "我想预定4星级酒店"
    hotels.main(itinerary_final, input2)

    print("一站式旅游行程规划服务执行完毕！快开始旅程吧！")
        
    # 其他功能
    expenses = TravelExpenses()

    input2 = "我想记账，今晚的晚餐吃了烤鸭，花了130元人民币"

    # 旅行记账
    expense = travel_expenses.main(input2)
    expenses.add_expense(expense)
    print("所有支出：", expenses.get_expenses())

    
    
if __name__ == '__main__':
    test()
