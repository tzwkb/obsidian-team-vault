# obsidian-team-vault

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)

English | [中文](README_ZH.md)

## Overview

 HTTPS API and management tool for a shared team Obsidian Vault, with registration, approval, permissions, and token authentication.

## Key Capabilities

- Uses a Mac Mini as the team Vault server.
- Provides registration, approval, and three-level permission control.
- Manages team knowledge-base access through a REST API.

## Usage

 Follow the deployment and API configuration notes below to start the service and configure users/permissions.

## Notes

 Public README content should not contain real tokens or private Vault content.

## Command and Configuration Reference

The following code blocks keep commands, paths, filenames, and configuration keys literal; explanatory comments are translated for the English README.

```
Client ──HTTPS──→ Cloudflare Tunnel ──→ Auth Proxy (:8000) ──→ Obsidian REST API (:27124)
                                            │
                                        users.db (SQLite)
```

```
# Window 1 - proxy service
cd ~/macobisidian && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000

# Window 2 - public tunnel
cloudflared tunnel --url http://localhost:8000
```
