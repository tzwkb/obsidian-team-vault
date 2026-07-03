# obsidian-team-vault

<!-- bilingual-readme:start -->

## 双语说明 / Bilingual Documentation

> 本节提供整篇 README 的中英双语维护说明；下方保留原始详细说明、命令、路径和配置示例。
> This section provides bilingual maintenance notes for the full README; the original detailed notes, commands, paths, and configuration examples are preserved below.

### 中文

**概览**：团队共享 Obsidian Vault 的 HTTPS API 和管理工具，支持注册、审批、权限和 Token 鉴权。

**主要能力**：
- 将 Mac Mini 作为团队 Vault 服务端。
- 提供注册、审批和三级权限控制。
- 通过 REST API 管理团队知识库访问。

**使用方式**：按下方部署和 API 配置说明启动服务、配置用户和权限。

**状态**：该仓库仍按当前 README 的说明维护或使用。

**注意事项**：公开 README 不应包含真实 token 或私有 Vault 内容。

### English

**Overview**: HTTPS API and management tool for a shared team Obsidian Vault, with registration, approval, permissions, and token authentication.

**Key capabilities**:
- Uses a Mac Mini as the team Vault server.
- Provides registration, approval, and three-level permission control.
- Manages team knowledge-base access through a REST API.

**Usage**: Follow the deployment and API configuration notes below to start the service and configure users/permissions.

**Status**: This repository is maintained or used according to the current README notes.

**Notes**: Public README content should not contain real tokens or private Vault content.

<!-- bilingual-readme:end -->

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