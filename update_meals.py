import requests
import json
import os
import re

# --- 核心配置 ---
GIST_ID = os.environ.get('GIST_ID')
GITHUB_TOKEN = os.environ.get('GH_TOKEN')

def classify_and_structure(title):
    """
    ORIGIN 语义分流器：
    根据菜名关键词，自动归类到 iPhone 13 上的四个按钮，并补齐侧菜与主食
    """
    t = title.lower()
    
    # [1. Brunch 逻辑]
    if any(k in t for k in ["蛋", "吐司", "三明治", "贝果", "燕麦", "滑蛋", "早安", "班尼迪克"]):
        cat = "brunch"
        staple = "全麦欧包 / 低GI钢切燕麦"
        side = "芝麻菜沙拉与半个牛油果"
    
    # [2. Snack 逻辑]
    elif any(k in t for k in ["酸奶", "坚果", "能量", "水果", "奇亚籽", "代餐", "碗", "莓果"]):
        cat = "snack"
        staple = "无糖糙米饼 / 少量黑巧克力碎"
        side = "抗氧化浆果 (蓝莓/草莓)"

    # [3. Chinese Dinner 逻辑]
    elif any(k in t for k in ["蒸", "炒", "笋", "酱", "腐", "肉饼", "鱼", "虾", "粤", "川", "滇", "本帮"]):
        cat = "chinese_dinner"
        staple = "五谷杂粮饭 (1/4 碗)"
        side = "白灼/清炒时令青菜 (加倍分量)"
        
    # [4. Dinner (Western/Mediterranean) 逻辑]
    else:
        cat = "dinner"
        staple = "蒜香藜麦 / 盐烤红豆薯"
        side = "地中海烤西葫芦与甜椒"

    # 按照 [维度穿透] 审美重组
    structured = (
        f"Main: [互联网实时] {title} | "
        f"Side: {side} | "
        f"Staple: {staple} | "
        f"Shop: [Fresh] {title}所需主料, 特级初榨橄榄油, 岩盐, 现磨黑胡椒"
    )
    return cat, structured

def run_evolution():
    url = "https://www.xiachufang.com/explore/"
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_0)"}

    try:
        print("正在连接互联网，为 ORIGIN 引擎采集真实数据...")
        response = requests.get(url, headers=headers, timeout=15)
        titles = re.findall(r'alt="([^"]+)"', response.text)
        
        # [严苛过滤逻辑] 踢出不符合 ORIGIN 审美的垃圾内容
        black_list = ["炸", "糖醋", "蛋糕", "甜点", "奶油", "酥", "红烧肉", "可乐", "重油", "五花肉"]
        
        # 获取当前云端 JSON
        auth_headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=auth_headers)
        gist_data = r.json()
        content = json.loads(gist_data['files']['ducky_meals.json']['content'])

        added_count = 0
        for t in titles[:25]: # 扫描前 25 条
            if not any(b in t for b in black_list):
                category, structured_dish = classify_and_structure(t)
                
                # 查重：如果该分类下已存在相同菜名，则跳过
                if structured_dish not in content[category]:
                    content[category].insert(0, structured_dish) # 插入最新鲜的在顶部
                    content[category] = content[category][:15] # 优胜劣汰，只留前 15 名
                    added_count += 1
        
        # 回传更新到 GitHub Gist
        updated_files = {
            "ducky_meals.json": {
                "content": json.dumps(content, ensure_ascii=False, indent=2)
            }
        }
        patch_r = requests.patch(
            f"https://api.github.com/gists/{GIST_ID}", 
            headers=auth_headers, 
            json={"files": updated_files}
        )
        
        if patch_r.status_code == 200:
            print(f"✅ 进化成功：新增 {added_count} 道真实菜谱，已自动归类并对齐营养比例。")
        else:
            print(f"❌ 更新失败，状态码: {patch_r.status_code}")

    except Exception as e:
        print(f"❌ 运行异常: {e}")

if __name__ == "__main__":
    run_evolution()
