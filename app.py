import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from flask import Flask, jsonify, send_from_directory

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
API_URL = "https://api.football-data.org/v4/competitions/BSA/standings?season=2026"
CACHE_SECONDS = 24 * 60 * 60
cache = {"at": 0, "data": None}

app = Flask(__name__, static_folder=None)

# Carrega .env localmente, se existir. No Render, configure a variável no painel.
def load_local_env():
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_standings():
    token = os.environ.get("FOOTBALL_DATA_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Chave não configurada. Configure FOOTBALL_DATA_TOKEN nas variáveis de ambiente do servidor.")
    req = urllib.request.Request(
        API_URL,
        headers={"X-Auth-Token": token, "User-Agent": "BrasileiraoDashboard/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise RuntimeError(f"A API recusou a chave ou o plano não permite esta consulta (HTTP {exc.code}). Confira a chave e as permissões.") from None
        if exc.code == 429:
            raise RuntimeError("Limite de consultas atingido. Tente novamente mais tarde.") from None
        raise RuntimeError(f"A API respondeu com erro HTTP {exc.code}.") from None
    except urllib.error.URLError:
        raise RuntimeError("Não foi possível conectar à API. Confira a conexão do servidor.") from None
    except json.JSONDecodeError:
        raise RuntimeError("A API respondeu em formato inesperado.") from None

    standings = data.get("standings") or []
    total = next((item for item in standings if item.get("type") == "TOTAL"), None)
    if not total or not total.get("table"):
        raise RuntimeError("A API não retornou a classificação geral do Brasileirão 2026.")
    return {
        "competition": data.get("competition", {}).get("name", "Campeonato Brasileiro Série A"),
        "season": str(data.get("season", {}).get("startDate", "2026"))[:4],
        "currentMatchday": data.get("season", {}).get("currentMatchday"),
        "table": total["table"],
    }


@app.get("/")
def index():
    return send_from_directory(STATIC, "index.html")


@app.get("/<path:filename>")
def static_files(filename):
    # Serve somente arquivos estáticos existentes na pasta static.
    return send_from_directory(STATIC, filename)


@app.get("/api/standings")
def standings():
    now = time.time()
    if cache["data"] is not None and now - cache["at"] < CACHE_SECONDS:
        return jsonify({"source": "cache", "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(cache["at"])), "data": cache["data"]})
    try:
        data = get_standings()
        cache.update(at=now, data=data)
        return jsonify({"source": "api", "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(now)), "data": data})
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502


load_local_env()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
