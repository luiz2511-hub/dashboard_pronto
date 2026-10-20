# Dashboard Analítico — Brasileirão 2026

Versão preparada para hospedar o site e o backend Python juntos no Render. Mantém a interface, a tabela, os gráficos, as estatísticas, a consulta à football-data.org e o cache de até 24 horas.

## Deploy no Render
1. Envie esta pasta para um repositório GitHub novo/atualizado, sem incluir o arquivo `.env`.
2. No Render, crie um **New Web Service** e conecte o repositório.
3. Runtime: **Python 3**.
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn app:app`
6. Em **Environment**, crie `FOOTBALL_DATA_TOKEN` com sua chave nova da football-data.org. Não use a chave que já apareceu publicamente.
7. Clique em **Deploy**. Abra a URL gerada pelo Render. O site e `/api/standings` estarão no mesmo domínio.

## Rodar localmente
```powershell
python -m pip install -r requirements.txt
```
Crie `.env` a partir de `.env.example` e coloque sua chave válida. Depois:
```powershell
python app.py
```
Abra `http://127.0.0.1:8000`.

## Observações
- Não publique `.env`; o `.gitignore` já o ignora.
- A API consultada é `football-data.org`, competição BSA, temporada 2026. A disponibilidade depende da chave e do plano dessa API.
- O cache de dados permanece em até 24 horas, como no projeto original.
