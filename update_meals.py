import requests
import json
import os
import random
import time

# --- 核心配置 ---
GIST_ID = os.environ.get('GIST_ID')
GITHUB_TOKEN = os.environ.get('GH_TOKEN')
FOOD_API_KEY = os.environ.get('FOOD_API_KEY')

def fetch_real_data():
    if not FOOD_API_KEY:
        print("❌ 缺少 FOOD_API_KEY，请检查 GitHub Secrets")
        return []

    # 扩大搜索范围，增加随机性
    tags = ["mediterranean", "chinese", "brunch", "healthy", "clean_eating"]
    tag = random.choice(tags)
    
    # 每次抓取 3 道
    url = f"https://api.spoonacular.com/recipes/random?number=3&tags={tag}&apiKey={FOOD_API_KEY}"
    
    try:
        r = requests.get(url, timeout=20)
        if r.status_code != 200:
            print(f"API 响应错误: {r.status_code}")
            return []
        
        recipes = r.json().get('recipes', [])
        results = []
        
        for res in recipes:
            title = res.get('title', '精品推荐')
            # 自动分类逻辑
            d_types = [dt.lower() for dt in res.get('dishTypes', [])]
            if 'breakfast' in d_types or 'brunch' in d_types: cat = "brunch"
            elif 'snack' in d_types: cat = "snack"
            elif tag == "chinese": cat = "chinese_dinner"
            else: cat = "dinner"

            # 强制加入当前秒数作为“动态 ID”，确保存档不重复
            now_stamp = time.strftime("%H:%M")
            
            entry = (
                f"Main: [维度穿透] {title} ({now_stamp}) | "
                f"Side: 有机时蔬配比 | "
                f"Staple: 复合碳水配比 | "
                f"Shop: [Fresh] {title}核心食材, 优质油脂"
            )
            results.append({"cat": cat, "entry": entry})
        return results
    except Exception as e:
        print(f"网络异常: {e}")
        return []

def run_evolution():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    try:
        # 1. 下载当前数据
        print(f"正在读取 Gist: {GIST_ID} ...")
        r = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=headers)
        gist_data = r.json()
        
        if 'files' not in gist_data:
            print("❌ 找不到 Gist 文件，请检查 GIST_ID")
            return

        content = json.loads(gist_data['files']['ducky_meals.json']['content'])

        # 2. 真实抓取
        new_items = fetch_real_data()
        
        added = 0
        if new_items:
            for item in new_items:
                cat = item['cat']
                entry = item['entry']
                # 强制插入：即使有重复，也会因为时间戳不同而存入
                content[cat].insert(0, entry)
                content[cat] = content[cat][:15] # 保持 15 条
                added += 1

            # 3. 强制回写
            updated = {"ducky_meals.json": {"content": json.dumps(content, ensure_ascii=False, indent=2)}}
            patch_r = requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=headers, json={"files": updated})
            
            if patch_r.status_code == 200:
                print(f"✅ 进化成功！已强行注入 {added} 道新菜谱。")
            else:
                print(f"❌ 回写失败: {patch_r.status_code}")
        else:
            print("⚠️ 未获取到新数据。")

    except Exception as e:
        print(f"❌ 运行崩溃: {e}")

if __name__ == "__main__":
    run_evolution()
