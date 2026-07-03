# obsidian-team-vault

中文 | [English](README.md)


Mac Mini 作为服务器，提供团队共享 Obsidian Vault 的 HTTPS API。内置注册 / 审批 / 三级权限 / Token 鉴权。

## 架构

```
客户端 ──HTTPS──→ Cloudflare Tunnel ──→ Auth Proxy (:8000) ──→ Obsidian REST API (:27124)
                                            │
                                        users.db (SQLite)
```

## Mac Mini 部署

1. 安装依赖：`pip3 install fastapi uvicorn httpx python-dotenv pydantic`
2. 安装 cloudflared：`brew install cloudflare/cloudflare/cloudflared`
3. Obsidian 里安装插件 **Local REST API**，复制 API Key
4. 编辑 `.env`，填入 `OBSIDIAN_API_KEY` 和 `ADMIN_TOKEN`
5. 启动：

```
# 窗口1 — 代理服务
cd ~/macobisidian && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000

# 窗口2 — 公网隧道
cloudflared tunnel --url http://localhost:8000
```

窗口2 打印的 `https://xxx.trycloudflare.com` 就是公网地址。

## 权限

| 角色 | 能做什么 |
|------|---------|
| reader | 读文件、搜索 |
| editor | 读、写、删文件 |
| admin | 全部 + 管理用户 + Token 直接读写 Vault |

## 用户流程

1. 从管理员获取公网地址
2. 注册：`POST /register`（填写姓名、权限、用途）
3. 管理员审批：`POST /admin/approve/{id}`，生成 Token 发给用户
4. 用户用 Token 调用 API

## 管理员流程

1. 获取公网地址：`grep "trycloudflare.com" ~/macobisidian/tunnel.log | tail -1`
2. 查看待审：`GET /admin/pending`
3. 审批：`POST /admin/approve/{id}` 或拒绝：`POST /admin/reject/{id}`
4. 管理：`GET /admin/users` / `DELETE /admin/revoke/{id}`

完整操作手册见 `admin-manual.html`。

## 文件

| 文件 | 说明 |
|------|------|
| `main.py` | 代理服务 |
| `.env` | OBSIDIAN_URL / OBSIDIAN_API_KEY / ADMIN_TOKEN |
| `users.db` | 用户数据库，首次运行自动创建 |
| `requirements.txt` | Python 依赖 |
| `admin-manual.html` | 管理员手册 + 开发文档 |
| `obsidian-team-vault/SKILL.md` | Claude Code Skill，安装后 Agent 自动引导配置 |
