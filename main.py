from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
import httpx
import sqlite3
import secrets
import os
from pydantic import BaseModel
from enum import Enum

load_dotenv()

OBSIDIAN_URL = os.getenv("OBSIDIAN_URL", "https://127.0.0.1:27124")
OBSIDIAN_API_KEY = os.getenv("OBSIDIAN_API_KEY", "")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
DB_PATH = os.getenv("DB_PATH", "users.db")

if not ADMIN_TOKEN:
    ADMIN_TOKEN = secrets.token_urlsafe(32)
    print(f"[WARN] ADMIN_TOKEN not set in .env, generated: {ADMIN_TOKEN}")

ROLE_METHODS = {
    "reader": {"GET"},
    "editor": {"GET", "PUT", "POST", "PATCH", "DELETE"},
    "admin":  {"GET", "PUT", "POST", "PATCH", "DELETE"},
}

app = FastAPI(title="Obsidian Proxy")
security = HTTPBearer()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            purpose       TEXT NOT NULL,
            requested_role TEXT NOT NULL,
            role          TEXT,
            token         TEXT UNIQUE,
            status        TEXT DEFAULT 'pending',
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()


class Role(str, Enum):
    reader = "reader"
    editor = "editor"
    admin  = "admin"


class RegisterRequest(BaseModel):
    name:           str
    requested_role: Role
    purpose:        str


class ApproveRequest(BaseModel):
    role: Role


def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != ADMIN_TOKEN:
        raise HTTPException(403, "Not admin")


def get_user_by_token(token: str):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE token = ? AND status = 'approved'", (token,)
    ).fetchone()
    conn.close()
    return user


@app.post("/register", status_code=201)
def register(req: RegisterRequest):
    conn = get_db()
    conn.execute(
        "INSERT INTO users (name, purpose, requested_role) VALUES (?, ?, ?)",
        (req.name, req.purpose, req.requested_role)
    )
    conn.commit()
    conn.close()
    return {"message": "申请已提交，等待管理员审批"}


@app.get("/admin/pending")
def list_pending(_=Depends(verify_admin)):
    conn = get_db()
    rows = conn.execute(
        "SELECT id, name, purpose, requested_role, created_at FROM users WHERE status = 'pending'"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/admin/users")
def list_users(_=Depends(verify_admin)):
    conn = get_db()
    rows = conn.execute(
        "SELECT id, name, purpose, requested_role, role, status, created_at FROM users"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/admin/approve/{user_id}")
def approve(user_id: int, req: ApproveRequest, _=Depends(verify_admin)):
    new_token = secrets.token_urlsafe(32)
    conn = get_db()
    result = conn.execute(
        "UPDATE users SET status='approved', role=?, token=? WHERE id=? AND status='pending'",
        (req.role, new_token, user_id)
    )
    conn.commit()
    conn.close()
    if result.rowcount == 0:
        raise HTTPException(404, "用户不存在或已处理")
    return {"token": new_token, "role": req.role}


@app.post("/admin/reject/{user_id}")
def reject(user_id: int, _=Depends(verify_admin)):
    conn = get_db()
    result = conn.execute(
        "UPDATE users SET status='rejected' WHERE id=? AND status='pending'", (user_id,)
    )
    conn.commit()
    conn.close()
    if result.rowcount == 0:
        raise HTTPException(404, "用户不存在或已处理")
    return {"message": "已拒绝"}


@app.delete("/admin/revoke/{user_id}")
def revoke(user_id: int, _=Depends(verify_admin)):
    conn = get_db()
    conn.execute(
        "UPDATE users SET status='revoked', token=NULL WHERE id=?", (user_id,)
    )
    conn.commit()
    conn.close()
    return {"message": "已撤销"}


@app.api_route("/{path:path}", methods=["GET", "PUT", "POST", "PATCH", "DELETE"])
async def proxy(path: str, request: Request,
                credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials == ADMIN_TOKEN:
        user = {"role": "admin"}
    else:
        user = get_user_by_token(credentials.credentials)
        if not user:
            raise HTTPException(401, "无效 Token")

    allowed = ROLE_METHODS.get(user["role"], set())
    if request.method not in allowed:
        # MCP protocol uses POST for all calls; allow POST to /mcp/* even for GET-only roles
        if request.method == "POST" and (path == "mcp" or path.startswith("mcp/")):
            pass
        else:
            raise HTTPException(403, f"{user['role']} 不允许 {request.method}")

    body = await request.body()
    headers = {k: v for k, v in request.headers.items()
               if k.lower() not in ("host", "authorization")}
    headers["Authorization"] = f"Bearer {OBSIDIAN_API_KEY}"

    async with httpx.AsyncClient(verify=False) as client:
        resp = await client.request(
            method=request.method,
            url=f"{OBSIDIAN_URL}/{path}",
            headers=headers,
            content=body,
            params=dict(request.query_params),
        )

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type"),
    )
