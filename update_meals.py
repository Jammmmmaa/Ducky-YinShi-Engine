import os, requests, random, json

# 配置
GIST_ID = "a05bf384ba10cf0c9c4f69a3f85f5a12"
GIST_TOKEN = os.getenv("GIST_TOKEN")

# 深度细化的中式与地中海食材库
data_pool = {
    "ch_protein": ["清蒸鲈鱼", "白灼基围虾", "蒜蓉蒸扇贝", "豉汁蒸排骨", "姜葱炒蟹", "板栗炖鸡", "荷包蛋", "卤牛肉", "滑鸡片", "香煎豆腐"],
    "ch_veg": ["干煸芸豆", "手撕包菜", "蒜泥白肉垫底黄瓜", "清炒菜心", "虎皮青椒", "蚝油生菜", "香菇油菜", "西红柿炒蛋", "上汤娃娃菜"],
    "ch_staple": ["土豆丝", "土豆片", "土豆泥", "蒸土豆", "山药", "红薯", "糙米饭", "小米粥"],
    "med_protein": ["煎三文鱼", "煎鳕鱼", "希腊酸奶", "鹰嘴豆", "金枪鱼沙拉"],
    "med_fats": ["特级初榨橄榄油", "牛油果", "核桃仁", "坚果碎", "奇亚籽"],
    "fruit": ["石榴", "无花果", "蓝莓", "草莓", "猕猴桃", "苹果"]
}

def build_meal(style):
    if style == "chinese":
        # 真正的中式菜肴组合逻辑
        p = random.choice(data_pool["ch_protein"])
        v = random.choice(data_pool["ch_veg"])
        s = random.choice(data_pool["ch_staple"])
        # 强制加入橄榄油健康元素
        return f"🥢 中式晚餐：{p} + {v} + 配主食({s}) (推荐用橄榄油烹饪)"
    
    elif style == "dinner":
        # 饮酒护肝专项
        p = random.choice(data_pool["ch_protein"] + data_pool["med_protein"])
        v = random.choice(data_pool["ch_veg"])
        # 饮酒必须有淀粉垫底
        s = random.choice(["蒸土豆", "土豆泥", "糙米饭"])
        return f"🌙 [饮酒护肝]：{p} (高蛋白) + {v} + {s} (淀粉垫底护胃)"
    
    elif style == "brunch":
        # 延续地中海三明治风格
        return f"🥪 早午餐：全麦面包 + {random.choice(['牛油果', '嫩豆腐'])} + {random.choice(['三文鱼', '滑鸡片', '煎蛋'])} + 橄榄油"
    
    else:
        # 审美品味加餐
        return f"🍎 加餐：{random.choice(data_pool['fruit'])} + {random.choice(['原味坚果', '希腊酸奶', '85%黑巧'])}"

# 每次生成 50 条，保证多样性
new_meals = {
    "brunch": [build_meal("brunch") for _ in range(50)],
    "dinner": [build_meal("dinner") for _ in range(50)],
    "chinese_dinner": [build_meal("chinese") for _ in range(50)],
    "snack": [build_meal("snack") for _ in range(50)]
}

# 更新 Gist
headers = {"Authorization": f"token {GIST_TOKEN}", "Accept": "application/vnd.github.v3+json"}
payload = {"files": {"ducky_meals.json": {"content": json.dumps(new_meals, ensure_ascii=False, indent=2)}}}
r = requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=headers, json=payload)
print(f"Status: {r.status_code}")
