# obsidian-team-vault

[中文](README.md) | English

## Overview

 HTTPS API and management tool for a shared team Obsidian Vault, with registration, approval, permissions, and token authentication.

## Key Capabilities

- Uses a Mac Mini as the team Vault server.
- Provides registration, approval, and three-level permission control.
- Manages team knowledge-base access through a REST API.

## Usage

 Follow the deployment and API configuration notes below to start the service and configure users/permissions.

## Status

 This repository is maintained or used according to the current README notes.

## Notes

 Public README content should not contain real tokens or private Vault content.

## Command and Configuration Reference

The following code blocks are preserved from the primary README. Commands, paths, and configuration keys are not translated; adjust them for the actual environment.

```
客户端 ──HTTPS──→ Cloudflare Tunnel ──→ Auth Proxy (:8000) ──→ Obsidian REST API (:27124)
                                            │
                                        users.db (SQLite)
```

```
# 窗口1 — 代理服务
cd ~/macobisidian && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000

# 窗口2 — 公网隧道
cloudflared tunnel --url http://localhost:8000
```

## Detailed Technical Notes

The primary README keeps the original technical details, history notes, full commands, and file layout. This file maintains the English version of the core documentation; consult the primary README code blocks and paths when exact commands are needed.
