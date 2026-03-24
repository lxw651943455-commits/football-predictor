# 通过 RapidAPI 获取 API-Football 密钥

## 步骤1：访问 RapidAPI
1. 打开浏览器访问：https://rapidapi.com/
2. 点击右上角 **"Sign Up"** 注册账号

## 步骤2：注册 RapidAPI 账号
- 填写邮箱（建议使用 Gmail）
- 设置密码（至少8位，包含大小写字母和数字）
- 验证邮箱

## 步骤3：搜索 API-Football
1. 登录后，在搜索框输入：`API-Football`
2. 找到 **"Football API" by API-Sports**
3. 点击进入

## 步骤4：订阅 API
1. 点击 **"Subscribe to Test"** 或 **"Pricing"** 标签
2. 选择 **"Free"** 套餐（100次请求/天）
3. 点击 **"Subscribe"**

## 步骤5：获取 API Key
订阅成功后，您会看到：
```
X-RapidAPI-Key: 你的密钥（类似：ae555cb14dmshf5df4f19cd1e8a6p16f7fajsnb5851f0fefe1）
```

## 步骤6：更新项目配置
复制密钥，更新项目的 `.env` 文件：
```bash
API_FOOTBALL_KEY=从RapidAPI复制的密钥
```

## 步骤7：测试 API
在项目根目录运行：
```bash
cd prediction-engine
python -c "
from services.api_fetcher import create_fetcher_from_env
import asyncio

async def test():
    fetcher = create_fetcher_from_env()
    # 测试获取积分榜
    standings = await fetcher.fetch_standings(39)  # 39 = 英超
    print(f'成功获取英超积分榜，共{len(standings)}队')

asyncio.run(test())
"
```

---

## 替代方案：Football-Data.org

如果 RapidAPI 也有问题，可以尝试：
- 网址：https://www.football-data.org/
- 注册后获取免费 API key
- 需要修改代码适配其 API 格式
