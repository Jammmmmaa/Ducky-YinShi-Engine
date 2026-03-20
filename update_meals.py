import requests
import json
import os
import random

# --- 核心配置 ---
GIST_ID = os.environ.get('GIST_ID')
GITHUB_TOKEN = os.environ.get('GH_TOKEN')
FOOD_API_KEY = os.environ.get('FOOD_API_KEY')

# 简单的内置翻译映射（针对常见健康食材）
TRANSLATION_MAP = {
    "Chicken": "嫩煎鸡胸", "Salmon": "大西洋三明治", "Salad": "油醋时蔬沙拉",
    "Beef": "草饲牛肉", "Shrimp": "基围虾", "Avocado": "牛油果",
    "Egg": "滑蛋", "Toast": "全麦吐司", "Bowl": "能量碗",
    "Roasted": "烤", "Grilled": "炙烤", "Steamed": "清蒸",
    "Garlic": "蒜香", "Lemon": "柠檬", "Mediterranean": "地中海风味"
}

def translate_title(eng_title):
    """
    将英文菜名转化为符合 ORIGIN 审美的中文
    """
    for eng, chn in TRANSLATION_MAP.items():
        if eng in eng_title:
            return f"{chn}{eng_title.split()[-1] if len(eng_title.split())>1 else ''}"
    return "地中海风味精选" if "Salad" in eng_title else "高蛋白能量餐"

def fetch_real_data():
    if not FOOD_API_KEY:
        print("❌ 缺少 FOOD_API_KEY")
        return []

    # 随机抓取：地中海、早餐、中式风格、健康零食
    tags = ["mediterranean", "breakfast", "chinese", "snack"]
    selected_tag = random.choice(tags)
    
    url = f"https://api.spoonacular.com/recipes/random?number=5&tags={selected_tag}&apiKey={FOOD_API_KEY}"
    
    try:
        r = requests.get(url, timeout=20)
        if r.status_code != 200:
            print(f"API 报错: {r.status_code}")
            return []
        
        recipes = r.json().get('recipes', [])
        structured_results = []
        
        for res in recipes:
            raw_title = res.get('title', '')
            chn_title = translate_title(raw_title)
            
            # 1. 自动分流逻辑
            d_types = [dt.lower() for dt in res.get('dishTypes', [])]
            if 'breakfast' in d_types or 'brunch' in d_types:
                cat = "brunch"
                side, staple = "半个牛油果/芝麻菜", "全麦欧包"
            elif 'snack' in d_types or 'appetizer' in d_types:
                cat = "snack"
                side, staple = "抗氧化蓝莓", "无糖糙米饼"
            elif selected_tag == "chinese":
                cat = "chinese_dinner"
                side, staple = "白灼清炒绿叶菜", "五谷杂粮饭"
            else:
                cat = "dinner"
                side, staple = "地中海烤西葫芦", "蒜香藜麦"

            # 2. 提取真实配料（前4样）
            ingredients = [i.get('name') for i in res.get('extendedIngredients', [])[:3]]
            shop_list = ", ".join(ingredients) if ingredients else "核心蛋白质, 优质油脂"

            # 3. 按照 [维度穿透] 格式组装
            entry = (
                f"Main: [维度穿透] {chn_title} | "
                f"Side: {side} (25%纤维) | "
                f"Staple: {staple} (25%碳水) | "
                f"Shop: [Fresh] {shop_list}, 海盐, 橄榄油"
            )
            structured_results.append({"cat": cat, "entry": entry})
            
        return structured_results
    except Exception as e:
        print(f"抓取异常: {e}")
        return []

def run_evolution():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    try:
        # 获取 Gist
        r = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=headers)
        gist_data = r.json()
        content = json.loads(gist_data['files']['ducky_meals.json']['content'])

        # 执行真实抓取
        new_items = fetch_real_data()
        
        added = 0
        if new_items:
            for item in new_items:
                cat = item['cat']
                entry = item['entry']
                if entry not in content[cat]:
                    content[cat].insert(0, entry)
                    content[cat] = content[cat][:15]
                    added += 1

            # 写回
            updated = {"ducky_meals.json": {"content": json.dumps(content, ensure_ascii=False, indent=2)}}
            requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=headers, json={"files": updated})
            print(f"✅ 成功！新增 {added} 道真实分类菜谱。")
        else:
            print("⚠️ 未抓取到新数据，请检查 API 额度。")

    except Exception as e:
        print(f"❌ 运行失败: {e}")

if __name__ == "__main__":
    run_evolution()
