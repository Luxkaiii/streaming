#!/usr/bin/env python3
"""
Site Status Checker — mini-webapp
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
• Vérifie l’état (OK / KO / DOWN) d’une liste de domaines.
• Mode sombre total, copy‑to‑clipboard compatible iOS/Safari, auto‑refresh.
• Dépendances : Flask & requests
"""

import concurrent.futures as cf
from typing import Dict, List, Union

import requests
from flask import Flask, render_template_string

DOMAINS = [
    "Atitop.com", "Batiav.com", "Bolgav.com", "Brimav.com", "Domgrav.com", "Dopriv.com",
    "Dovlip.com", "Faklum.com", "Gamzig.com", "Gozirav.com", "Ipdro.com", "Makriv.com",
    "Malgrim.com", "Mobnab.com", "Moovbob.com", "Rogzov.com", "Tarbob.com", "Trifak.com",
    "Valdap.com", "Vredap.com", "Wifrad.com", "Yakriv.com",
]
TIMEOUT, MAX_WORKERS, REFRESH_MS = 5, 10, 30_000
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    )
}

def check_site(domain: str) -> Dict[str, str]:
    try:
        r = requests.head(f"https://{domain}", headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        if r.status_code >= 400:
            r = requests.get(f"https://{domain}", headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        status = "OK" if 200 <= r.status_code < 400 else "KO"
    except requests.RequestException:
        status = "DOWN"
    return {"domain": domain, "status": status}

app = Flask(__name__)

TEMPLATE = """<!doctype html>
<html lang='fr'>
<head>
<meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Status Checker</title>
<link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css'>
<style>
 body{margin:0;padding:2rem;font-family:Inter, sans-serif;background:#0d1117;color:#e6edf3}
 .glass{background:#161b22;border:1px solid #21262d;border-radius:.75rem;padding:1.2rem;box-shadow:0 4px 24px rgba(0,0,0,.6)}
 table{width:100%;border-collapse:separate;border-spacing:0 .5rem}
 th,td{padding:.75rem 1rem;border:none;background:transparent}
 thead th{color:#c9d1d9}
 tbody tr:hover{background:#21262d;transition:background .25s}
 a{font-weight:600;color:#58a6ff;text-decoration:none}
 #toast{position:fixed;bottom:1rem;left:50%;transform:translateX(-50%);background:#161b22;color:#e6edf3;padding:.6rem 1.2rem;border-radius:6px;display:none;z-index:99}
 .fade{animation:fade 1.2s forwards}@keyframes fade{0%{opacity:0}10%,90%{opacity:1}100%{opacity:0}}
</style>
</head>
<body>
<div class='container'>
 <div class='columns is-centered'>
  <div class='column is-10-tablet is-7-desktop is-6-widescreen'>
   <div class='glass'>
     <h1 class='title is-4'>💡 Status Checker</h1>
     <p class='subtitle is-6'>Clique sur un nom pour le copier 📋</p>
     <table><thead><tr><th>Site</th><th class='has-text-centered'>Statut</th></tr></thead><tbody>
       {% for row in rows %}
       <tr>
        <td><a href='#' onclick="copyToClipboard('{{ row.domain }}');return false;">{{ row.domain }}</a></td>
        <td class='has-text-centered'>{% if row.status=='OK' %}🟢{% elif row.status=='KO' %}🟠{% else %}🔴{% endif %}</td>
       </tr>
       {% endfor %}
     </tbody></table>
   </div>
  </div>
 </div>
</div>
<div id='toast'>Copié !</div>
<script>
function fallbackCopy(text){
  const ta=document.createElement('textarea');ta.value=text;ta.style.position='fixed';ta.style.top='-9999px';
  document.body.appendChild(ta);ta.focus();ta.select();try{document.execCommand('copy');}catch(e){};document.body.removeChild(ta);
}
function copyToClipboard(text){
  if(navigator.clipboard && window.isSecureContext){navigator.clipboard.writeText(text).then(showToast).catch(()=>{fallbackCopy(text);showToast();});}
  else{fallbackCopy(text);showToast();}
}
function showToast(){const t=document.getElementById('toast');t.classList.add('fade');t.style.display='block';setTimeout(()=>{t.style.display='none';t.classList.remove('fade');},1200);}
setInterval(()=>{if(document.visibilityState==='visible')location.reload();},{{ REFRESH_MS }});
</script>
</body></html>"""

@app.route('/')
def index():
    with cf.ThreadPoolExecutor(max_workers=MAX_WORKERS) as exe:
        rows: List[Dict[str, str]] = list(exe.map(check_site, DOMAINS))
    rows.sort(key=lambda r: r['domain'].lower())
    return render_template_string(TEMPLATE, rows=rows, REFRESH_MS=REFRESH_MS)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
