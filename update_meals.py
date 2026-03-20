import os, requests, random, json

# 配置
GIST_ID = "a05bf384ba10cf0c9c4f69a3f85f5a12"
GIST_TOKEN = os.getenv("GIST_TOKEN")

def run():
    # 1. 地中海晚餐：侧重 Omega-3, 不饱和脂肪, 餐厅级质感
    med_list = [
        "Main:香煎三文鱼 (橄榄油制)|Side:芝麻菜核桃沙拉|Staple:香草烤土豆|Shop:三文鱼、芝麻菜、核桃、土豆、橄榄油",
        "Main:柠檬烤鳕鱼|Side:烤芦笋配帕玛森干酪|Staple:藜麦饭|Shop:鳕鱼、芦笋、藜麦、柠檬",
        "Main:慢炖番茄海鲜集|Side:羽衣甘蓝甜椒拌橄榄|Staple:全麦皮塔饼|Shop:虾/贝类、番茄、羽衣甘蓝、全麦面包",
        "Main:迷迭香烤鸡腿肉|Side:烤口蘑配蒜片|Staple:法老小麦(或糙米)|Shop:鸡腿、口蘑、大蒜、糙米"
    ]
    
    # 2. 中式晚餐：侧重 2026 膳食指南清淡烹饪, 高纤维
    chi_list = [
        "Main:清蒸姜葱鲈鱼|Side:白灼菜心|Staple:蒸土豆(淀粉护胃)|Shop:鲈鱼、菜心、土豆、葱姜",
        "Main:豉汁蒸排骨|Side:蒜泥西兰花|Staple:糙米饭|Shop:排骨、西兰花、糙米、豆豉",
        "Main:西芹腰果炒虾仁|Side:凉拌木耳丝|Staple:小米粥|Shop:虾仁、西芹、腰果、木耳、小米",
        "Main:酱牛肉拼盘|Side:蚝油生菜|Staple:清蒸山药|Shop:熟牛肉、生菜、山药、蚝油"
    ]

    # 3. 早午餐：快速、高能、美学
    bru_list = [
        "Main:北非番茄烩蛋 (Shakshuka)|Side:新鲜果蔬|Staple:全麦面包|Shop:番茄、鸡蛋、洋葱、全麦面包",
        "Main:牛油果熏三文鱼开放三明治|Side:混合坚果|Staple:全麦吐司|Shop:熏三文鱼、牛油果、全麦面包",
        "Main:希腊酸奶坚果能量碗|Side:无花果/蓝莓|Staple:燕麦/坚果|Shop:希腊酸奶、无花果、蓝莓、核桃"
    ]

    # 4. 加餐
    snk_list = [
        "Main:无花果/石榴|Side:一把原味核桃|Staple:无|Shop:无花果、石榴、核桃",
        "Main:蓝莓|Side:85%黑巧克力|Staple:无|Shop:蓝莓、黑巧克力"
    ]

    new_data = {
        "brunch": [random.choice(bru_list) for _ in range(30)],
        "dinner": [random.choice(med_list) for _ in range(30)],
        "chinese_dinner": [random.choice(chi_list) for _ in range(30)],
        "snack": [random.choice(snk_list) for _ in range(30)]
    }

    headers = {"Authorization": f"token {GIST_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    payload = {"files": {"ducky_meals.json": {"content": json.dumps(new_data, ensure_ascii=False, indent=2)}}}
    r = requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=headers, json=payload)
    print(f"Sync Status: {r.status_code}")

if __name__ == "__main__":
    run()
