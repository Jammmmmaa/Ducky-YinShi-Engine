import requests
import json
import os
import re

# --- 核心配置 ---
GIST_ID = os.environ.get('GIST_ID')
GITHUB_TOKEN = os.environ.get('GH_TOKEN')

def extract_pure_dish_name(raw_text):
    """
    极致清洗：不仅去掉符号，还要精准切除博主名称和无意义后缀
    """
    # 1. 过滤掉纯博主名的条目（通常这种条目很短或者包含"的"）
    if "的厨房" in raw_text or "的小课堂" in raw_text or "私房" in raw_text:
        # 尝试拆分，例如 "阿曼达的厨房：清蒸鱼" -> 取 "清蒸鱼"
        if "：" in raw_text: return raw_text.split("：")[-1]
        if ":" in raw_text: return raw_text.split(":")[-1]
        # 如果是 "阿曼达的清蒸鱼"，去掉 "阿曼达的"
        raw_text = re.sub(r'.*?的', '', raw_text)

    # 2. 去除表情、特殊符号、括号内容
    t = re.sub(r'\(.*?\)|（.*?）|\[.*?\]|【.*?】', '', raw_text)
    t = re.sub(r'[^\u4e00-\u9fa5]', '', t) # 强制只保留汉字，彻底杀掉英文 ID 和表情

    # 3. 常见无意义后缀清理
    for suffix in ["做法", "分享", "全攻略", "秘籍", "超简单", "懒人版", "必学"]:
        t = t.replace(suffix, "")
        
    return t

def get_category_config(dish_name):
    """
    根据菜名核心词，精准分配到四个按钮，并匹配 ORIGIN 营养模板
    """
    t = dish_name
    # Brunch 逻辑
    if any(k in t for k in ["蛋", "吐司", "三明治", "贝果", "燕麦", "煎饼", "滑蛋", "早", "松饼"]):
        return "brunch", "芝麻菜沙拉与半个牛油果", "全麦欧包/低GI燕麦"
    # Snack 逻辑
    elif any(k in t for k in ["酸奶", "坚果", "能量", "水果", "奇亚籽", "莓", "碗", "零食"]):
        return "snack", "抗氧化浆果 (蓝莓/草莓)", "无糖糙米饼/黑巧克力"
    # 中式晚餐 逻辑
    elif any(k in t for k in ["蒸", "炒", "笋", "酱", "腐", "肉", "鱼", "虾", "粤", "川", "滇", "丝", "片"]):
        return "chinese_dinner", "白灼/清炒时令青菜 (加倍)", "五谷杂粮饭 (1/4碗)"
    # 默认：地中海/西式晚餐
    return "dinner", "地中海烤西葫芦与甜椒", "蒜香藜麦/盐烤红薯"

def run_evolution():
    url = "https://www.xiachufang.com/explore/"
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_0)"}

    try:
        response = requests.get(url, headers=headers, timeout=15)
        # 换一种抓取方式：匹配所有可能是标题的文本
        raw_list = re.findall(r'alt="([^"]+)"', response.text)
        
        auth_headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=auth_headers)
        content = json.loads(r.json()['files']['ducky_meals.json']['content'])

        # 建立指纹库进行去重（提取现有菜谱里的汉字核心）
        existing_fingerprints = set()
        for cat in content:
            for dish in content[cat]:
                core = re.sub(r'[^\u4e00-\u9fa5]', '', dish.split('|')[0])
                existing_fingerprints.add(core)

        added_count = 0
        for raw_item in raw_list:
            pure_name = extract_pure_dish_name(raw_item)
            
            # 过滤：太短的（可能是博主名）、已存在的、带黑名单词的
            if len(pure_name) < 2 or pure_name in existing_fingerprints:
                continue
            if any(b in raw_item for b in ["炸", "糖", "蛋糕", "红烧肉", "五花肉"]):
                continue

            # 分流
            cat, side, staple = get_category_config(pure_name)
            
            # 组装
            new_entry = (
                f"Main: [维度穿透] {pure_name} | "
                f"Side: {side} | "
                f"Staple: {staple} | "
                f"Shop: [Fresh] {pure_name}主料, 基础调味, 优质油脂"
            )
            
            content[cat].insert(0, new_entry)
            content[cat] = content[cat][:15] # 数量限制
            existing_fingerprints.add(pure_name)
            added_count += 1
            if added_count >= 10: break # 每次进货量控制在 10 个以内

        # 上传
        updated = {"ducky_meals.json": {"content": json.dumps(content, ensure_ascii=False, indent=2)}}
        requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=auth_headers, json={"files": updated})
        print(f"✅ 进化成功：新增 {added_count} 道纯净菜谱。")

    except Exception as e:
        print(f"❌ 运行异常: {e}")

if __name__ == "__main__":
    run_evolution()
