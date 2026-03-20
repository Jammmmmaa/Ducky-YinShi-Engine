<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Ducky 营养规划</title>
    <style>
        :root { --p: #2C3E50; --s: #27AE60; --a: #E74C3C; --bg: #F4F7F6; }
        body { font-family: "PingFang SC", sans-serif; background: var(--bg); padding: 20px; margin: 0; color: var(--p); }
        .container { max-width: 400px; margin: 0 auto; }
        
        /* 营养师风格卡片 */
        .plan-card { 
            background: white; border-radius: 24px; padding: 25px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-bottom: 25px;
            border-left: 6px solid var(--s); min-height: 250px;
        }
        .plan-header { border-bottom: 1px solid #EEE; padding-bottom: 15px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }
        .type-label { font-size: 0.75rem; font-weight: 900; color: #999; letter-spacing: 1px; }
        
        .section { margin-bottom: 15px; }
        .section-label { font-size: 0.65rem; color: var(--s); font-weight: 800; margin-bottom: 4px; display: block; }
        .section-val { font-size: 1.15rem; font-weight: 700; color: var(--p); }
        .staple-val { color: #8E44AD; } /* 主食特别颜色标注 */

        .shop-box { background: #F9F9F9; padding: 12px; border-radius: 12px; margin-top: 10px; }
        .shop-title { font-size: 0.6rem; color: #BBB; font-weight: 800; margin-bottom: 5px; }
        .shop-items { font-size: 0.85rem; color: #666; line-height: 1.4; }

        .btn-group { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
        button { 
            background: var(--p); color: white; border: none; padding: 18px 5px; 
            border-radius: 18px; font-weight: 700; cursor: pointer; transition: 0.2s;
        }
        button:active { transform: scale(0.95); opacity: 0.8; }
        .btn-full { grid-column: span 2; }
        .btn-ch { background: #C0392B; }
        .btn-med { background: var(--s); }
        button:disabled { background: #CCC; }

        .footer { text-align: center; font-size: 0.6rem; color: #CCC; margin-top: 20px; }
    </style>
</head>
<body>

<div class="container">
    <div class="plan-card" id="card">
        <div class="plan-header">
            <span class="type-label" id="type-txt">NUTRITION PLAN</span>
            <span id="date-txt" style="font-size: 0.6rem; color: #DDD;">2026-GUIDE</span>
        </div>
        
        <div id="display-area">
            <div class="section">
                <span class="section-label">【主菜 / Main Protein】</span>
                <div class="section-val" id="main-v">等待规划...</div>
            </div>
            <div class="section">
                <span class="section-label">【配菜 / Side Dish】</span>
                <div class="section-val" id="side-v">---</div>
            </div>
            <div class="section">
                <span class="section-label">【碳水 / Staple】</span>
                <div class="section-val staple-val" id="staple-v">---</div>
            </div>
            <div class="shop-box" id="shop-box" style="display:none;">
                <div class="shop-title">📋 准备清单 / PREP LIST</div>
                <div class="shop-items" id="shop-v"></div>
            </div>
        </div>
    </div>

    <div class="btn-group">
        <button class="btn-full" onclick="gen('brunch')" id="b1" disabled>☀️ 餐厅级早午餐</button>
        <button class="btn-ch" onclick="gen('chinese_dinner')" id="b2" disabled>🥢 中式平衡晚餐</button>
        <button class="btn-med" onclick="gen('dinner')" id="b3" disabled>🌿 地中海晚餐</button>
        <button class="btn-full" style="background:#7F8C8D" onclick="gen('snack')" id="b4" disabled>🍏 营养加餐</button>
    </div>
    
    <div class="footer">● 2026 膳食引擎已连接 | Logic & Aesthetics</div>
</div>

<script>
    let data = null;
    const URL = 'https://gist.githubusercontent.com/Jammmmmaa/a05bf384ba10cf0c9c4f69a3f85f5a12/raw/ducky_meals.json?v=' + Date.now();

    async function init() {
        try {
            const r = await fetch(URL);
            data = await r.json();
            document.querySelectorAll('button').forEach(b => b.disabled = false);
        } catch(e) { alert("网络连接失败"); }
    }

    function gen(type) {
        if(!data) return;
        const pool = data[type];
        const raw = pool[Math.floor(Math.random()*pool.length)];
        
        // 解析结构化数据
        const parts = {};
        raw.split('|').forEach(p => {
            const [k, v] = p.split(':');
            parts[k] = v;
        });

        document.getElementById('main-v').innerText = parts.Main;
        document.getElementById('side-v').innerText = parts.Side;
        document.getElementById('staple-v').innerText = parts.Staple;
        document.getElementById('shop-v').innerText = parts.Shop;
        document.getElementById('shop-box').style.display = 'block';
        document.getElementById('type-txt').innerText = type.toUpperCase().replace('_', ' ');
        
        // 视觉反馈
        const card = document.getElementById('card');
        card.style.borderColor = type === 'chinese_dinner' ? '#C0392B' : (type === 'dinner' ? '#27AE60' : '#2C3E50');
    }
    init();
</script>
</body>
</html>
