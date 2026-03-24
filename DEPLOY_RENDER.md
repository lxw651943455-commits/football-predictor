# Render 免费部署指南

## 免费方案对比

| 平台 | 免费额度 | 优点 | 缺点 |
|------|---------|------|------|
| **Render** | 750 小时/月 | 稳定，部署简单 | 免费版会休眠（15分钟无访问） |
| Fly.io | $5 信用 | 全球 CDN | 配置稍复杂 |
| Koyeb | 免费 | 快速部署 | 额度较少 |

**推荐使用 Render** - 已准备好配置文件。

---

## 部署步骤

### 1. 准备工作

确保你的代码已经推送到 GitHub：
```bash
git add .
git commit -m "准备部署到 Render"
git push
```

### 2. 部署到 Render

1. 打开 https://dashboard.render.com
2. 用 GitHub 登录
3. 点击 **"New +"** → **"Web Service"**
4. 选择 GitHub 仓库：`football-predictor`
5. 填写配置：

   | 字段 | 值 |
   |------|-----|
   | Name | `football-backend` |
   | Root Directory | `backend` |
   | Build Command | `npm install` |
   | Start Command | `node server-simple.js` |
   | Plan | **FREE** |

6. 点击 **"Create Web Service"**

### 3. 获取后端 URL

部署完成后（约 3-5 分钟），你会得到一个 URL：
```
https://football-backend.onrender.com
```

### 4. 更新前端 API 地址

需要更新前端的 `.env` 文件：

```bash
# 前端目录
cd frontend

# 创建生产环境配置
echo "VITE_API_BASE_URL=https://football-backend.onrender.com" > .env.production

# 重新部署前端
git add .env.production
git commit -m "更新生产环境 API 地址"
git push
```

---

## 注意事项

⚠️ **免费版休眠机制**：
- 15 分钟无请求会自动休眠
- 休眠后首次访问需要 ~30 秒唤醒
- 不影响核心功能，只是首次访问稍慢

✅ **解决方案**：
- 定期 ping 保持活跃（可选）
- 或升级到付费版（$7/月）

---

## 测试部署

部署完成后，访问：
```
https://football-backend.onrender.com/health
```

应该看到：
```json
{
  "status": "healthy",
  "service": "football-predictor-backend-simple"
}
```

---

## 其他方案

如果 Render 部署失败，可以尝试：

### Fly.io
```bash
# 安装 flyctl
powershell -c "iwr https://fly.io/install.ps1 | iex"

# 登录
flyctl auth login

# 部署
flyctl launch
```

### Koyeb
访问：https://www.koyeb.com
- 直接连接 GitHub
- Root Directory: `backend`
- Start Command: `node server-simple.js`

---

## 需要帮助？

遇到问题随时告诉我！
