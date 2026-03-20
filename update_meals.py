import requests
import json
import os
import re

# --- 核心配置 ---
GIST_ID = os.environ.get('GIST_ID')
GITHUB_TOKEN = os.environ.get('GH_TOKEN')

def get_clean_dish_name(title):
    """
    针对新源的极致清洗：只保留核心菜名，剔除所有营销号后缀
    """
    # 1. 剔除常见的博主营销后缀
    garbage_words = ["的小厨房", "私房菜", "教程", "全攻略", "必读", "分享", "测评", "推荐"]
    for word in garbage_words:
        title = title.replace(word, "")
    
    # 2. 提取最像菜名的部分（通常是冒号后面，或者书名号里的）
    if "：" in title: title = title.split("：")[-1]
    if "【" in title: title = re.search(r'【(.*?)】', title).group(1) if re.search(r'【(.*?)】', title) else title
    
    # 3. 强制只留汉字，长度控制在 2-10 字之间（博主名通常带符号或过长）
    pure_hanzi = re.sub(r'[^\u4e00-\u9fa5]', '', title)
    return pure_hanzi if 2 <= len(pure_hanzi) <= 10 else None

def classify_to_origin_button(name):
    """
    根据菜名逻辑，自动分流到四个按钮，并匹配 50:25:25 营养模板
    """
    # Brunch
    if any(k in name for k in ["蛋", "吐司", "三明治", "贝果", "燕麦", "煎饼", "滑蛋", "早"]):
        return "brunch", "芝麻菜沙拉与半个牛油果", "全麦欧包/低GI燕麦"
    # Snack
    elif any(k in name for k in ["酸奶", "坚果", "能量", "水果", "奇亚籽", "莓", "碗"]):
        return "snack", "抗氧化浆果 (蓝莓/草莓)", "无糖糙米饼/黑巧克力"
    # 中式晚餐
    elif any(k in name for k in ["蒸", "炒", "笋", "酱", "腐", "肉", "鱼", "虾", "粤", "川", "滇"]):
        return "chinese_dinner", "白灼/清炒时令青菜 (加倍分量)", "五谷杂粮饭 (1/4碗)"
    # 默认：地中海晚餐
    return "dinner", "地中海烤西葫芦与甜椒", "蒜香藜麦/盐烤红薯"

def evolve_origin_engine():
    # 切换到更稳定的高质量美食数据聚合源 (这里使用一个通用的精品 RSS 转换接口)
    # 这个源只返回标题，不包含杂乱的博主 ID
    url = "https://rsshub.app/xiachufang/user/1000547/collections" # 抓取特定精品收藏夹，数据更纯净
    
    try:
        print("正在连接精品数据源，执行 ORIGIN 饮食引擎进化...")
        headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_0)"}
        response = requests.get(url, headers=headers, timeout=20)
        
        # 解析 RSS 里的标题 (XML 格式)
        raw_titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', response.text)
        
        # 准备云端数据
        auth_headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=auth_headers)
        content = json.loads(r.json()['files']['ducky_meals.json']['content'])

        # 获取已存在的菜名指纹
        existing_names = set()
        for cat in content:
            for dish in content[cat]:
                name_core = dish.split('|')[0].replace("Main: [维度穿透] ", "").strip()
                existing_names.add(name_core)

        added_count = 0
        for raw_t in raw_titles:
            # 过滤掉非菜谱类的标题（比如“我的收藏”）
            if "收藏" in raw_t or len(raw_t) < 3: continue
            
            clean_name = get_clean_dish_name(raw_t)
            if not clean_name or clean_name in existing_names: continue
            
            # 分流逻辑
            category, side, staple = classify_to_origin_button(clean_name)
            
            # 组装 ORIGIN 标准格式
            new_entry = (
                f"Main: [维度穿透] {clean_name} | "
                f"Side: {side} | "
                f"Staple: {staple} | "
                f"Shop: [Fresh] {clean_name}核心食材, 优质油脂, 海盐"
            )
            
            content[category].insert(0, new_entry)
            content[category] = content[category][:15] # 限制数量
            existing_names.add(clean_name)
            added_count += 1

        # 上传更新
        updated_data = {"ducky_meals.json": {"content": json.dumps(content, ensure_ascii=False, indent=2)}}
        requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=auth_headers, json={"files": updated_data})
        print(f"✅ 进化完成！新增 {added_count} 道精品菜谱。")

    except Exception as e:
        print(f"❌ 运行异常: {e}")

if __name__ == "__main__":
    evolve_origin_engine()
