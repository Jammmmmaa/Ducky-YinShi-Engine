import os, requests, random, json

# 配置
GIST_ID = "a05bf384ba10cf0c9c4f69a3f85f5a12"
GIST_TOKEN = os.getenv("GIST_TOKEN")

# 完全基于你上传图片的 50 种地中海食材库
data_pool = {
    "fats": ["特级初榨橄榄油", "牛油果", "核桃/杏仁/腰果", "奇亚籽/亚麻籽", "南瓜籽/葵花籽", "橄榄", "菲达奶酪"],
    "protein": ["三文鱼", "鲭鱼", "沙丁鱼", "金枪鱼", "鳕鱼", "白灼虾", "生蚝/牡蛎", "贻贝", "鸡胸肉", "鸡蛋", "希腊酸奶"],
    "veg": ["番茄", "菠菜", "羽衣甘蓝", "西兰花", "芦笋", "彩椒", "洋葱", "大蒜", "西葫芦", "茄子", "洋蓟", "胡萝卜", "蘑菇"],
    "fruit": ["柠檬", "蓝莓/草莓/树莓", "橙子/柑橘", "石榴", "西瓜", "无花果", "葡萄", "苹果", "香蕉"],
    "carbs": ["蒸土豆", "烤土豆块", "全麦面包/皮塔饼", "鹰嘴豆泥", "小扁豆", "藜麦", "法老小麦", "燕麦"]
}

def build_meal(style):
    c = random.choice(data_pool["carbs"])
    p = random.choice(data_pool["protein"])
    v = random.choice(data_pool["veg"])
    f = random.choice(data_pool["fats"])
    
    if style == "brunch":
        return f"🥪 早午餐：{c} + {p} + {v} + 搭配{f}"
    elif style == "dinner":
        return f"🌙 [饮酒护肝推荐]：{p} + {v} + {c} (优质蛋白+B族补充)"
    elif style == "chinese":
        return f"🥢 纯中式：{random.choice(['清蒸', '蒜蓉', '快炒'])}{p} + {v} + {c} (橄榄油烹饪)"
    else:
        return f"🍎 加餐：{random.choice(data_pool['fruit'])} + {random.choice(['核桃', '希腊酸奶', '黑巧'])}"

# 每天生成 50 条随机食谱
new_meals = {
    "brunch": [build_meal("brunch") for _ in range(50)],
    "dinner": [build_meal("dinner") for _ in range(50)],
    "chinese_dinner": [build_meal("chinese") for _ in range(50)],
    "snack": [build_meal("snack") for _ in range(50)]
}

# 更新 Gist 接口
headers = {"Authorization": f"token {GIST_TOKEN}", "Accept": "application/vnd.github.v3+json"}
payload = {"files": {"ducky_meals.json": {"content": json.dumps(new_meals, ensure_ascii=False, indent=2)}}}
r = requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=headers, json=payload)

if r.status_code == 200:
    print("✅ 全自动化食谱进化成功！")
else:
    print(f"❌ 更新失败: {r.status_code}")
