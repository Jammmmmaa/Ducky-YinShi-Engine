import requests
import json
import os
import random

# --- 核心配置 ---
GIST_ID = os.environ.get('GIST_ID')
GITHUB_TOKEN = os.environ.get('GH_TOKEN')
FOOD_API_KEY = os.environ.get('FOOD_API_KEY')

def run_evolution():
    if not FOOD_API_KEY or not GITHUB_TOKEN or not GIST_ID:
        print("❌ 环境变量缺失！请检查 Secret 设置。")
        return

    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # 1. 尝试连接 API (增加中文参数)
    print(f"--- 正在诊断 API 连接 ---")
    # tags 包含你的四个分类逻辑
    tag_list = ["breakfast", "main course", "chinese", "snack"]
    selected_tag = random.choice(tag_list)
    
    # 加入 &addRecipeInformation=true 和 &language=zh (虽然API中文支持有限，但能增强识别)
    api_url = f"https://api.spoonacular.com/recipes/random?number=3&tags={selected_tag}&apiKey={FOOD_API_KEY}"
    
    try:
        api_res = requests.get(api_url, timeout=20)
        print(f"API 状态码: {api_res.status_code}")
        
        if api_res.status_code != 200:
            print(f"❌ API 通信失败！报错信息: {api_res.text}")
            return

        recipes = api_res.json().get('recipes', [])
        if not recipes:
            print("⚠️ API 通了，但没返回任何菜谱。可能是 Tags 匹配太严，尝试扩大搜索...")
            return

        print(f"✅ 成功从 API 抓取到 {len(recipes)} 道菜。")

        # 2. 获取并解析 Gist
        gist_res = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=headers)
        gist_data = gist_res.json()
        
        if 'files' not in gist_data:
            print("❌ Gist ID 可能错误，无法读取文件。")
            return
            
        content = json.loads(gist_data['files']['ducky_meals.json']['content'])

        # 3. 处理数据并分类 (加入 50:25:25 逻辑)
        for r in recipes:
            eng_title = r.get('title')
            # 简单的关键词翻译映射
            chn_title = eng_title.replace("Chicken", "鸡肉").replace("Salmon", "三文鱼").replace("Salad", "沙拉").replace("Beef", "牛肉").replace("Rice", "饭")
            
            # 分类判定
            types = [t.lower() for t in r.get('dishTypes', [])]
            if 'breakfast' in types or 'brunch' in types: cat = "brunch"
            elif 'snack' in types or 'fingerfood' in types: cat = "snack"
            elif "chinese" in str(r.get('cuisines', [])).lower(): cat = "chinese_dinner"
            else: cat = "dinner"

            # 组装符合 ORIGIN 审美的条目
            entry = (
                f"Main: [维度穿透] {chn_title} | "
                f"Side: 时令有机绿叶菜 (25% 纤维) | "
                f"Staple: 复合全谷物 (25% 碳水) | "
                f"Shop: [Fresh] {chn_title}核心食材, 优质油脂"
            )
            
            # 强制插入（避开去重逻辑，看看能不能写进去）
            content[cat].insert(0, entry)
            content[cat] = content[cat][:15]

        # 4. 推送回 Gist
        updated_files = {"ducky_meals.json": {"content": json.dumps(content, ensure_ascii=False, indent=2)}}
        patch_res = requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=headers, json={"files": updated_files})
        
        if patch_res.status_code == 200:
            print("🚀 进化成功！数据已强制推送到 Gist。")
        else:
            print(f"❌ 写入 Gist 失败: {patch_res.status_code}, 详情: {patch_res.text}")

    except Exception as e:
        print(f"💥 运行崩溃: {e}")

if __name__ == "__main__":
    run_evolution()
