import requests
import json
import os
import re

# --- 核心配置 ---
GIST_ID = os.environ.get('GIST_ID')
GITHUB_TOKEN = os.environ.get('GH_TOKEN')

def clean_title(title):
    """
    清洗菜名：去掉博主名、表情符号、多余空格
    例如：'小红书博主A的减脂低卡三明治✨' -> '三明治'
    """
    t = re.sub(r'\(.*?\)|（.*?）|\[.*?\]', '', title) # 去掉括号内容
    t = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', t) # 只留汉字字母数字
    # 去掉常见的博主后缀或前缀词
    for word in ["的小食堂", "的厨房", "私房菜", "做法", "分享", "保姆级", "超简单"]:
        t = t.replace(word, "")
    return t

def classify_logic(clean_name):
    """
    硬核分类器：根据清洗后的核心词精准分流
    """
    t = clean_name.lower()
    
    # 1. Brunch: 强调早餐属性
    if any(k in t for k in ["蛋", "吐司", "三明治", "贝果", "燕麦", "煎饼", "滑蛋", "舒芙蕾", "松饼"]):
        return "brunch", "芝麻菜沙拉与半个牛油果", "全麦欧包/低GI燕麦"
    
    # 2. Snack: 强调小份量与天然能量
    elif any(k in t for k in ["酸奶", "坚果", "能量", "水果", "奇亚籽", "莓果", "椰子", "碗"]):
        return "snack", "抗氧化浆果 (蓝莓/草莓)", "无糖糙米饼/黑巧克力"

    # 3. 中式晚餐: 强调中式烹饪法与特定食材
    elif any(k in t for k in ["蒸", "炒", "笋", "酱", "腐", "肉饼", "鱼", "虾", "粤", "川", "滇", "丝", "片"]):
        return "chinese_dinner", "白灼/清炒时令青菜 (加倍)", "五谷杂粮饭 (1/4碗)"
        
    # 4. 地中海/西式晚餐 (默认)
    else:
        return "dinner", "地中海烤西葫芦与甜椒", "蒜香藜麦/盐烤红薯"

def run_evolution():
    url = "https://www.xiachufang.com/explore/"
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_0)"}

    try:
        response = requests.get(url, headers=headers, timeout=15)
        raw_titles = re.findall(r'alt="([^"]+)"', response.text)
        
        # 获取当前云端数据
        auth_headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=auth_headers)
        content = json.loads(r.json()['files']['ducky_meals.json']['content'])

        # 获取现有的所有核心菜名（用于深度去重）
        existing_names = []
        for cat in content:
            for dish in content[cat]:
                # 提取 Main: [XXX] 之后的原始菜名
                match = re.search(r'\] (.*?) \|', dish)
                if match:
                    existing_names.append(clean_title(match.group(1)))

        added_count = 0
        for raw_t in raw_titles[:30]:
            c_name = clean_title(raw_t)
            
            # --- 核心去重逻辑 ---
            # 如果清洗后的核心菜名已经存在，或者名字太短，则跳过
            if c_name in existing_names or len(c_name) < 2:
                continue
            
            # 过滤黑名单
            if any(b in raw_t for b in ["炸", "糖醋", "蛋糕", "甜点", "红烧肉", "可乐", "重油"]):
                continue

            # 执行分类与结构化
            cat, side, staple = classify_logic(c_name)
            
            structured_dish = (
                f"Main: [互联网实时] {c_name} | "
                f"Side: {side} | "
                f"Staple: {staple} | "
                f"Shop: [Fresh] {c_name}主料, 特级初榨橄榄油, 海盐"
            )

            content[cat].insert(0, structured_dish)
            content[cat] = content[cat][:15] # 每个分类只留最鲜活的 15 条
            existing_names.append(c_name) # 放入临时列表防止本次运行内重复
            added_count += 1
        
        # 写回 Gist
        updated = {"ducky_meals.json": {"content": json.dumps(content, ensure_ascii=False, indent=2)}}
        requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=auth_headers, json={"files": updated})
        print(f"✅ 进化完成！新增 {added_count} 道非重复菜谱。")

    except Exception as e:
        print(f"❌ 运行异常: {e}")

if __name__ == "__main__":
    run_evolution()
