import os, requests, random, json

# 配置
GIST_ID = "a05bf384ba10cf0c9c4f69a3f85f5a12"
GIST_TOKEN = os.getenv("GIST_TOKEN")

# --- 2026 地中海主厨库 ---
data_store = {
    "brunch": [
        {"name": "北非番茄烩蛋 (Shakshuka) + 全麦面包", "shop": "番茄、鸡蛋、洋葱、橄榄油、全麦面包"},
        {"name": "希腊酸奶熏三文鱼拼盘 + 混合坚果", "shop": "熏三文鱼(开袋)、希腊酸奶、黄瓜、核桃"},
        {"name": "全麦牛油果滑蛋吐司 (餐厅经典版)", "shop": "全麦面包、牛油果、鸡蛋、黑胡椒"},
        {"name": "地中海暖沙拉：蒸土豆+水浸金枪鱼+生菜", "shop": "土豆、金枪鱼罐头、生菜、橄榄油"}
    ],
    "chinese_dinner": [
        {"name": "清蒸柠檬鲈鱼 + 蒜蓉菜心 + 糙米饭", "shop": "鲈鱼、菜心、柠檬、糙米"},
        {"name": "西芹腰果炒虾仁 + 凉拌木耳 + 蒸土豆", "shop": "虾仁、西芹、腰果、木耳、土豆"},
        {"name": "板栗焖鸡块 + 蚝油手撕包菜 + 杂粮粥", "shop": "鸡肉、板栗、圆白菜、杂粮"},
        {"name": "番茄炒蛋 + 蒜蓉蒸扇贝 + 糙米饭", "shop": "番茄、鸡蛋、扇贝、西兰花"}
    ],
    "dinner": [
        {"name": "[护肝垫底] 醋溜土豆丝 + 卤牛肉 + 拍黄瓜", "shop": "土豆、熟牛肉、黄瓜、陈醋"},
        {"name": "[饮酒必备] 肉沫土豆泥 + 蒜泥白肉(瘦) + 蒸西兰花", "shop": "土豆、瘦肉末、里脊肉、西兰花"},
        {"name": "[解酒推荐] 番茄牛腩煲 + 白灼秋葵 + 蒸南瓜", "shop": "牛腩、番茄、秋葵、南瓜"},
        {"name": "[清淡修复] 丝瓜豆腐汤 + 姜葱滑鸡 + 糙米饭", "shop": "丝瓜、嫩豆腐、鸡肉、葱姜"}
    ],
    "snack": [
        {"name": "无花果 + 希腊酸奶 + 蜂蜜", "shop": "无花果、酸奶、蜂蜜"},
        {"name": "蓝莓 + 85%黑巧克力 + 一把核桃", "shop": "蓝莓、黑巧、核桃"}
    ]
}

def generate_entry(category):
    item = random.choice(data_store[category])
    # 2026逻辑提醒：确保橄榄油的使用
    return f"{item['name']} | 准备清单：{item['shop']}"

def run():
    new_data = {cat: [generate_entry(cat) for _ in range(50)] for cat in data_store.keys()}
    headers = {"Authorization": f"token {GIST_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    payload = {"files": {"ducky_meals.json": {"content": json.dumps(new_data, ensure_ascii=False, indent=2)}}}
    r = requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=headers, json=payload)
    print(f"2026 主厨引擎同步: {r.status_code}")

if __name__ == "__main__":
    run()
