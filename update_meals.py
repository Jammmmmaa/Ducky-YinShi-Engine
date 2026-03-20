import requests
import json
import os
import random

# --- 核心配置 ---
GIST_ID = os.getenv('GIST_ID')
GITHUB_TOKEN = os.getenv('GH_TOKEN')
FOOD_API_KEY = os.getenv('FOOD_API_KEY')

# --- 扩展 ORIGIN 翻译库 (覆盖早中晚加所有场景) ---
TRANS_DICT = {
    "Egg": "滑蛋", "Toast": "吐司", "Avocado": "牛油果", "Oat": "燕麦", "Pancake": "松饼", # Brunch
    "Shrimp": "基围虾", "Ginger": "姜葱", "Soy": "酱香", "Stir-fry": "小炒", "Fish": "鲜鱼", # Chinese
    "Chicken": "鸡胸", "Beef": "草饲牛", "Salad": "沙拉", "Roasted": "炉烤", "Lemon": "青柠", # Dinner
    "Yogurt": "酸奶碗", "Nut": "坚果", "Berry": "浆果", "Smoothie": "奶昔", "Dark Chocolate": "黑巧", # Snack
    "Garlic": "蒜香", "Mediterranean": "地中海", "Healthy": "纤体", "Bowl": "能量碗"
}

def origin_translate(title):
    """提取关键词并重组为具有逻辑美感的中文菜名"""
    words = title.replace("-", " ").split()
    matched = [TRANS_DICT[w.capitalize()] for w in words if w.capitalize() in TRANS_DICT]
    if not matched: return "地中海高蛋白精选"
    return "".join(dict.fromkeys(matched))

def run_evolution():
    if not all([GIST_ID, GITHUB_TOKEN, FOOD_API_KEY]): return

    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # 策略：分四次请求，每次针对一个特定标签，确保各分类平衡
    # 1. breakfast(Brunch), 2. chinese(中式), 3. snack(加餐), 4. main course(西式晚餐)
    plans = [
        {"tag": "breakfast", "cat": "brunch", "side": "有机芝麻菜/牛油果", "staple": "全麦欧包"},
        {"tag": "chinese", "cat": "chinese_dinner", "side": "白灼时令青菜 (加倍)", "staple": "五谷杂粮饭"},
        {"tag": "snack", "cat": "snack", "side": "抗氧化蓝莓", "staple": "无糖糙米饼"},
        {"tag": "main course", "cat": "dinner", "side": "地中海烤西葫芦", "staple": "盐烤红薯"}
    ]

    try:
        # 获取 Gist 现有内容
        gist_res = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=headers)
        content = json.loads(gist_res.json()['files']['ducky_meals.json']['content'])
        
        total_added = 0

        for plan in plans:
            # 针对每个分类精准进货 3 道真实菜谱
            api_url = f"https://api.spoonacular.com/recipes/random?number=3&tags={plan['tag']}&apiKey={FOOD_API_KEY}"
            res = requests.get(api_url, timeout=15).json()
            recipes = res.get('recipes', [])

            for r in recipes:
                chn_name = origin_translate(r.get('title', ''))
                cat = plan['cat']
                
                # 提取配料
                ing = [i.get('name') for i in r.get('extendedIngredients', [])[:3]]
                shop = ", ".join(ing) if ing else "核心蛋白质"

                entry = (
                    f"Main: [维度穿透] {chn_name} | "
                    f"Side: {plan['side']} (25%纤维) | "
                    f"Staple: {plan['staple']} (25%碳水) | "
                    f"Shop: [Fresh] {shop}, 海盐, 优质油脂"
                )

                if entry not in content[cat]:
                    content[cat].insert(0, entry)
                    content[cat] = content[cat][:15] # 限制货架容量
                    total_added += 1

        # 更新 Gist
        updated = {"ducky_meals.json": {"content": json.dumps(content, ensure_ascii=False, indent=2)}}
        requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=headers, json={"files": updated})
        print(f"✅ 进化完成！全分类覆盖，共新增 {total_added} 道真实菜谱。")

    except Exception as e:
        print(f"💥 异常: {e}")

if __name__ == "__main__":
    run_evolution()
