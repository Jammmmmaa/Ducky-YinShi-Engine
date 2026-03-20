name: Ducky Menu Auto-Evolve

on:
  schedule:
    - cron: '0 20 * * *' # 北京时间凌晨 4 点执行，为你准备新一天的灵感
  workflow_dispatch: # 允许你随时手动点击测试

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install Dependencies
        run: pip install requests

      - name: Run Update Script
        env:
          # 1. 你的 Gist 钥匙 (对应你截图中的名字)
          GH_TOKEN: ${{ secrets.GIST_TOKEN }}
          # 2. 你的货架 ID
          GIST_ID: "a05bf384ba10cf0c9c4f69a3f85f5a12"
          # 3. 刚刚建立的全球食谱数据库钥匙
          FOOD_API_KEY: ${{ secrets.FOOD_API_KEY }}
        run: |
          python update_meals.py
