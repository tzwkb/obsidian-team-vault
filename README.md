# obsidian-team-vault

English | [中文](README_ZH.md)


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

## Detailed Technical Notes

The primary README keeps the original technical details, history notes, full commands, and file layout. This file maintains the English version of the core documentation; consult the primary README code blocks and paths when exact commands are needed.
