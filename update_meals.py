import requests
import json
import os
import re

# --- 核心配置 ---
GIST_ID = os.environ.get('GIST_ID')
GITHUB_TOKEN = os.environ.get('GH_TOKEN')

def fetch_real_web_trends():
    """
    真正联网：抓取下厨房(Xiachufang)或高质量食谱站点的实时趋势
    并根据 [维度穿透] 逻辑进行清洗
    """
    trends = []
    # 示例：抓取下厨房周度最受欢迎 (这是一个真实的网页接口)
    # 注意：实际生产中我们可以对接多个 RSS 订阅源
    target_url = "https://www.xiachufang.com/explore/" 
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Mobile/15E148 Safari/604.1"
    }

    try:
        r = requests.get(target_url, headers=headers, timeout=10)
        # 提取页面中的菜谱名称 (使用正则简单模拟爬虫逻辑)
        # 实际逻辑会更复杂，这里确保演示真实联网动作
        raw_names = re.findall(r'alt="([^"]+)"', r.text)
        
        # --- ORIGIN 过滤器：只保留符合你五大菜系及地中海审美的关键词 ---
        keywords = ["清蒸", "凉拌", "酸笋", "柠檬", "橄榄", "牛里脊", "虾", "菌菇", "和牛", "地中海"]
        
        for name in raw_names:
            if any(k in name for k in keywords):
                # 结构化：将互联网标题自动转化为你的 [维度穿透] 格式
                # 自动分配配料模块
                dish = f"Main: [全网热搜] {name} | Side: 时令有机时蔬沙拉 | Staple: 复合全谷物 | Shop: [Provisions] 初榨橄榄油, 海盐, 黑胡椒, 基础调味"
                if dish not in trends:
                    trends.append(dish)
        
        return trends[:5] # 每次只进货 5 道最精华的
    except Exception as e:
        print(f"联网抓取失败: {e}")
        return []

def evolve_system():
    if not GIST_ID or not GITHUB_TOKEN:
        print("未检测到密钥，请检查 Actions Secrets 设置。")
        return

    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # 1. 获取当前数据
    r = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=headers)
    gist = r.json()
    filename = 'ducky_meals.json'
    content = json.loads(gist['files'][filename]['content'])
    
    # 2. 真正联网进货
    print("正在连接互联网抓取最新菜谱...")
    new_dishes = fetch_real_web_trends()
    
    # 3. 注入数据池 (插入到各分类顶部)
    if new_dishes:
        for dish in new_dishes:
            # 简单逻辑：包含中式关键词的进 chinese_dinner，其余进 dinner
            if any(k in dish for k in ["酸笋", "本帮", "川", "粤", "滇"]):
                if dish not in content['chinese_dinner']:
                    content['chinese_dinner'].insert(0, dish)
            else:
                if dish not in content['dinner']:
                    content['dinner'].insert(0, dish)
        
        print(f"成功抓取到 {len(new_dishes)} 道互联网趋势菜品。")
    
    # 4. 保持精简
    for cat in content:
        content[cat] = content[cat][:20]

    # 5. 回传更新
    updated_files = {filename: {"content": json.dumps(content, ensure_ascii=False, indent=2)}}
    requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=headers, json={"files": updated_files})

if __name__ == "__main__":
    evolve_system()
