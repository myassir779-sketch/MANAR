#!/usr/bin/env python3
"""MANAR minimal shared API (stdlib only; place behind HTTPS reverse proxy)."""
from __future__ import annotations
import base64, hashlib, hmac, json, os, secrets, sqlite3, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get('MANAR_DB_PATH', str(ROOT / 'data' / 'manar.sqlite3')))
HOST = os.environ.get('MANAR_HOST', '127.0.0.1')
PORT = int(os.environ.get('MANAR_API_PORT', '4174'))
TOKEN_SECRET = os.environ.get('MANAR_TOKEN_SECRET', '')
BOOTSTRAP_ADMIN_KEY = os.environ.get('MANAR_ADMIN_SETUP_KEY', '')
MAX_BODY = 100_000


def db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    con.execute('PRAGMA journal_mode=WAL')
    con.executescript('''
      CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, name TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('admin','client','translator')), password_hash TEXT NOT NULL, created_at INTEGER NOT NULL);
      CREATE TABLE IF NOT EXISTS jobs(id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL REFERENCES users(id), title TEXT NOT NULL, source_language TEXT NOT NULL, target_language TEXT NOT NULL, description TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'submitted' CHECK(status IN ('submitted','reviewing','assigned','in_progress','qa','completed','cancelled')), assigned_translator_id INTEGER REFERENCES users(id), created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL);
      CREATE TABLE IF NOT EXISTS translator_profiles(user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE, native_language TEXT NOT NULL, languages TEXT NOT NULL, specialties TEXT NOT NULL DEFAULT '', bio TEXT NOT NULL DEFAULT '', availability TEXT NOT NULL DEFAULT 'available');
      CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY, actor_id INTEGER, action TEXT NOT NULL, entity TEXT NOT NULL, entity_id INTEGER, created_at INTEGER NOT NULL);
    ''')
    return con


def pw_hash(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 310_000)
    return base64.urlsafe_b64encode(salt).decode().rstrip('=') + '$' + base64.urlsafe_b64encode(digest).decode().rstrip('=')


def pw_verify(password: str, stored: str) -> bool:
    try:
        salt_s, digest_s = stored.split('$', 1)
        salt = base64.urlsafe_b64decode(salt_s + '=' * (-len(salt_s) % 4))
        expected = base64.urlsafe_b64decode(digest_s + '=' * (-len(digest_s) % 4))
        actual = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 310_000)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def token_for(user_id: int, role: str) -> str:
    if len(TOKEN_SECRET) < 32:
        raise RuntimeError('MANAR_TOKEN_SECRET must be at least 32 characters')
    payload = base64.urlsafe_b64encode(json.dumps({'uid': user_id, 'role': role, 'exp': int(time.time()) + 86400}, separators=(',', ':')).encode()).decode().rstrip('=')
    sig = hmac.new(TOKEN_SECRET.encode(), payload.encode(), hashlib.sha256).digest()
    return payload + '.' + base64.urlsafe_b64encode(sig).decode().rstrip('=')


def decode_token(token: str):
    try:
        payload, signature = token.split('.', 1)
        expected = hmac.new(TOKEN_SECRET.encode(), payload.encode(), hashlib.sha256).digest()
        supplied = base64.urlsafe_b64decode(signature + '=' * (-len(signature) % 4))
        if not hmac.compare_digest(expected, supplied): return None
        data = json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4)))
        if int(data['exp']) < time.time(): return None
        return data
    except Exception:
        return None


class API(BaseHTTPRequestHandler):
    server_version = 'MANAR-API'
    def log_message(self, fmt, *args):
        print('[MANAR API]', fmt % args)
    def send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body))); self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Content-Security-Policy',"default-src 'none'; frame-ancestors 'none'")
        self.send_header('Referrer-Policy','no-referrer'); self.end_headers(); self.wfile.write(body)
    def read_json(self):
        try: n = int(self.headers.get('Content-Length','0'))
        except ValueError: n = 0
        if n <= 0 or n > MAX_BODY: raise ValueError('BODY_SIZE')
        data = json.loads(self.rfile.read(n).decode('utf-8'))
        if not isinstance(data, dict): raise ValueError('INVALID_JSON')
        return data
    def auth(self):
        header = self.headers.get('Authorization','')
        if not header.startswith('Bearer '): return None
        return decode_token(header[7:])
    def audit(self, con, actor, action, entity, entity_id):
        con.execute('INSERT INTO audit(actor_id,action,entity,entity_id,created_at) VALUES(?,?,?,?,?)',(actor,action,entity,entity_id,int(time.time())))
    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/health':
            self.send_json(200, {'ok':True,'service':'MANAR shared API','database':'sqlite','authConfigured':len(TOKEN_SECRET)>=32}); return
        user = self.auth()
        if not user: self.send_json(401, {'ok':False,'error':'AUTH_REQUIRED'}); return
        con = db()
        try:
            if path == '/api/me':
                row=con.execute('SELECT id,email,name,role,created_at FROM users WHERE id=?',(user['uid'],)).fetchone()
                self.send_json(200, {'ok':True,'user':dict(row) if row else None}); return
            if path == '/api/jobs':
                if user['role']=='admin': rows=con.execute('SELECT j.*,u.name AS owner_name FROM jobs j JOIN users u ON u.id=j.owner_id ORDER BY j.created_at DESC LIMIT 500').fetchall()
                elif user['role']=='translator': rows=con.execute("SELECT j.*,u.name AS owner_name FROM jobs j JOIN users u ON u.id=j.owner_id WHERE j.status='submitted' OR j.assigned_translator_id=? ORDER BY j.created_at DESC LIMIT 200",(user['uid'],)).fetchall()
                else: rows=con.execute('SELECT * FROM jobs WHERE owner_id=? ORDER BY created_at DESC LIMIT 200',(user['uid'],)).fetchall()
                self.send_json(200, {'ok':True,'jobs':[dict(r) for r in rows]}); return
            if path == '/api/translators':
                rows=con.execute("SELECT u.id,u.name,u.email,p.native_language,p.languages,p.specialties,p.bio,p.availability FROM users u JOIN translator_profiles p ON p.user_id=u.id ORDER BY u.created_at DESC LIMIT 500").fetchall()
                self.send_json(200, {'ok':True,'translators':[dict(r) for r in rows]}); return
            self.send_json(404, {'ok':False,'error':'NOT_FOUND'})
        finally: con.close()
    def do_POST(self):
        path=urlparse(self.path).path
        try: data=self.read_json()
        except Exception: self.send_json(400,{'ok':False,'error':'INVALID_BODY','message':'Tuma JSON halali isiyozidi 100 KB.'}); return
        con=db()
        try:
            if path == '/api/register':
                email=str(data.get('email','')).strip().lower(); name=str(data.get('name','')).strip(); password=data.get('password'); role=data.get('role','client')
                if not email or '@' not in email or len(email)>254 or not name or len(name)>120 or not isinstance(password,str) or len(password)<12 or len(password)>200 or role not in ('client','translator'):
                    self.send_json(400,{'ok':False,'error':'VALIDATION','message':'Weka jina, barua pepe halali, nenosiri la angalau herufi 12 na role client/translator.'}); return
                try:
                    cur=con.execute('INSERT INTO users(email,name,role,password_hash,created_at) VALUES(?,?,?,?,?)',(email,name,role,pw_hash(password),int(time.time())))
                    uid=cur.lastrowid
                    if role=='translator':
                        native=str(data.get('nativeLanguage','')).strip(); langs=data.get('languages',[])
                        if not native or not isinstance(langs,list): con.rollback(); self.send_json(400,{'ok':False,'error':'TRANSLATOR_PROFILE_REQUIRED'}); return
                        con.execute('INSERT INTO translator_profiles(user_id,native_language,languages,specialties,bio) VALUES(?,?,?,?,?)',(uid,native,json.dumps(langs),str(data.get('specialties',''))[:500],str(data.get('bio',''))[:2000]))
                    self.audit(con,uid,'register','user',uid); con.commit()
                    self.send_json(201,{'ok':True,'token':token_for(uid,role),'user':{'id':uid,'email':email,'name':name,'role':role}})
                except sqlite3.IntegrityError: self.send_json(409,{'ok':False,'error':'EMAIL_EXISTS'})
                return
            if path == '/api/login':
                email=str(data.get('email','')).strip().lower(); password=data.get('password','')
                row=con.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
                if not row or not isinstance(password,str) or not pw_verify(password,row['password_hash']): self.send_json(401,{'ok':False,'error':'INVALID_CREDENTIALS'}); return
                self.send_json(200,{'ok':True,'token':token_for(row['id'],row['role']),'user':{'id':row['id'],'email':row['email'],'name':row['name'],'role':row['role']}}); return
            if path == '/api/admin/bootstrap':
                if not BOOTSTRAP_ADMIN_KEY or not hmac.compare_digest(str(data.get('setupKey','')),BOOTSTRAP_ADMIN_KEY): self.send_json(403,{'ok':False,'error':'SETUP_DENIED'}); return
                if con.execute("SELECT 1 FROM users WHERE role='admin' LIMIT 1").fetchone(): self.send_json(409,{'ok':False,'error':'ADMIN_ALREADY_EXISTS'}); return
                email=str(data.get('email','')).strip().lower(); name=str(data.get('name','Admin')).strip(); password=data.get('password')
                if not email or '@' not in email or not isinstance(password,str) or len(password)<16: self.send_json(400,{'ok':False,'error':'ADMIN_PASSWORD_MIN_16'}); return
                cur=con.execute("INSERT INTO users(email,name,role,password_hash,created_at) VALUES(?,?,'admin',?,?)",(email,name,pw_hash(password),int(time.time())))
                self.audit(con,cur.lastrowid,'bootstrap','user',cur.lastrowid); con.commit(); self.send_json(201,{'ok':True,'message':'Admin created. Remove setup key from environment now.'}); return
            user=self.auth()
            if not user: self.send_json(401,{'ok':False,'error':'AUTH_REQUIRED'}); return
            if path == '/api/jobs':
                title=str(data.get('title','')).strip(); source=str(data.get('sourceLanguage','')).strip(); target=str(data.get('targetLanguage','')).strip(); description=str(data.get('description','')).strip()
                if user['role'] not in ('admin','client') or not title or len(title)>200 or not source or not target or source==target or len(description)>10000: self.send_json(400,{'ok':False,'error':'JOB_VALIDATION'}); return
                now=int(time.time()); cur=con.execute("INSERT INTO jobs(owner_id,title,source_language,target_language,description,status,created_at,updated_at) VALUES(?,?,?,?,?,'submitted',?,?)",(user['uid'],title,source,target,description,now,now)); self.audit(con,user['uid'],'create','job',cur.lastrowid); con.commit(); self.send_json(201,{'ok':True,'jobId':cur.lastrowid,'status':'submitted'}); return
            if path.startswith('/api/jobs/') and path.endswith('/status'):
                if user['role']!='admin': self.send_json(403,{'ok':False,'error':'ADMIN_REQUIRED'}); return
                try: job_id=int(path.split('/')[-2])
                except ValueError: self.send_json(400,{'ok':False,'error':'INVALID_JOB_ID'}); return
                status=str(data.get('status',''))
                if status not in ('submitted','reviewing','assigned','in_progress','qa','completed','cancelled'): self.send_json(400,{'ok':False,'error':'INVALID_STATUS'}); return
                cur=con.execute('UPDATE jobs SET status=?,updated_at=? WHERE id=?',(status,int(time.time()),job_id))
                if not cur.rowcount: self.send_json(404,{'ok':False,'error':'JOB_NOT_FOUND'}); return
                self.audit(con,user['uid'],'status_change','job',job_id); con.commit(); self.send_json(200,{'ok':True,'jobId':job_id,'status':status}); return
            self.send_json(404,{'ok':False,'error':'NOT_FOUND'})
        except Exception:
            con.rollback(); self.send_json(500,{'ok':False,'error':'INTERNAL_ERROR','message':'Ombi limefeli; hakuna maelezo binafsi yaliyorejeshwa.'})
        finally: con.close()

if __name__=='__main__':
    if len(TOKEN_SECRET)<32: raise SystemExit('Set MANAR_TOKEN_SECRET to a random secret of at least 32 characters before starting.')
    print(f'MANAR API listening on http://{HOST}:{PORT} (development only; use HTTPS reverse proxy in production)')
    ThreadingHTTPServer((HOST,PORT),API).serve_forever()
