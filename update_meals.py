import os, requests, random, json

# 配置
GIST_ID = "a05bf384ba10cf0c9c4f69a3f85f5a12"
GIST_TOKEN = os.getenv("GIST_TOKEN")

# --- 2026 膳食引擎数据库 ---
# 碳水池：分为“通用型”和“饮酒保护型”
carbs_pool = ["糙米饭", "全麦皮塔饼", "藜麦沙拉", "小米干饭", "燕麦大米饭", "荞麦面"]
potato_vault = ["厚切蒸土豆", "烤土豆块", "土豆泥"] # 专门用于需要强力垫底的场景

# 蛋白质池：地中海核心
proteins = ["三文鱼", "白灼虾", "清蒸鲈鱼", "金枪鱼", "滑鸡片", "瘦牛肉", "嫩豆腐", "酱羊肉"]

# 蔬菜池：强调深色和十字花科（2026指南重点）
veggies = ["西兰花", "羽衣甘蓝", "菠菜", "西葫芦", "彩椒", "紫甘蓝", "芦笋", "木耳", "芹菜"]

def generate_smart_meal(category):
    # 2026 黄金配比：2份蔬果 + 1份优质蛋白 + 1份复合碳水 + 1份单不饱和脂肪
    p = random.choice(proteins)
    v_list = random.sample(veggies, 2)
    
    if category == "dinner":
        # 饮酒护肝逻辑：高B族 + 淀粉垫底
        # 此时土豆出现概率提升至 80%，因为它是天然的胃黏膜保护层
        s = random.choice(potato_vault) if random.random() < 0.8 else random.choice(carbs_pool)
        menu = f"🌙 [护肝防醉] {p} + {'拌'.join(v_list)} + {s}"
        shop = f"采购：{p}、{v_list[0]}、{v_list[1]}、{s}、特级初榨橄榄油"
        
    elif category == "chinese_dinner":
        # 中式平衡逻辑：不再强求土豆，从碳水池随机选择
        s = random.choice(carbs_pool + potato_vault) 
        menu = f"🥢 中式膳食：{random.choice(['清蒸', '小炒'])}{p} + {v_list[0]}炒{v_list[1]} + {s}"
        shop = f"采购：{p}、{v_list[0]}、{v_list[1]}、{s}"
        
    elif category == "brunch":
        # 早午餐逻辑：Logic & Aesthetics
        s = random.choice(["全麦面包", "藜麦", "蒸土豆"])
        menu = f"🥪 审美拼盘：{s} + {p} + {v_list[0]} + 牛油果"
        shop = f"采购：{s}、{p}、{v_list[0]}、牛油果"
    
    else: # snack
        fruit = random.choice(["蓝莓", "无花果", "石榴", "猕猴桃"])
        nut = random.choice(["核桃", "腰果", "希腊酸奶"])
        return f"🍎 能量补给：{fruit} + {nut} | 采购：{fruit}、{nut}"

    return f"{menu} | {shop}"

def run():
    new_data = {cat: [generate_smart_meal(cat) for _ in range(50)] for cat in ["brunch", "dinner", "chinese_dinner", "snack"]}
    
    headers = {"Authorization": f"token {GIST_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    payload = {"files": {"ducky_meals.json": {"content": json.dumps(new_data, ensure_ascii=False, indent=2)}}}
    r = requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=headers, json=payload)
    print(f"2026 Engine Sync: {r.status_code}")

if __name__ == "__main__":
    run()
