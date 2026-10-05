"""Gerador de relatório HTML de QA."""
import os
from datetime import datetime


_COR_SEV = {
    "CRITICA": "#dc3545",
    "ALTA":    "#fd7e14",
    "MEDIA":   "#ffc107",
    "BAIXA":   "#28a745",
    "-":       "#6c757d",
}


def gerar_relatorio(resultados, arquivo="relatorios/relatorio_qa.html"):
    os.makedirs(os.path.dirname(arquivo), exist_ok=True)

    total     = len(resultados)
    aprovados = sum(1 for r in resultados if r["status"] == "PASS")
    reprovados = total - aprovados
    taxa       = (aprovados / total * 100) if total else 0
    criticos   = sum(1 for r in resultados if r["status"] == "FAIL" and r["severidade"] == "CRITICA")

    if reprovados == 0:
        decisao, cor_dec, icone = "LIBERADO", "#28a745", "&#10003;"
        texto_dec = "Sistema aprovado em todos os testes. Pode ser liberado para produção."
    elif criticos > 0:
        decisao, cor_dec, icone = "NÃO LIBERAR", "#dc3545", "&#10007;"
        texto_dec = "Falhas críticas detectadas. O sistema não deve ser liberado para produção."
    else:
        decisao, cor_dec, icone = "LIBERADO COM RESSALVAS", "#ffc107", "&#9888;"
        texto_dec = "Falhas não-críticas encontradas. Liberação condicionada à correção dos defeitos."

    cor_taxa = "#28a745" if taxa >= 80 else "#ffc107" if taxa >= 50 else "#dc3545"
    agora    = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")

    linhas = ""
    for r in resultados:
        cor_st  = "#28a745" if r["status"] == "PASS" else "#dc3545"
        cor_sv  = _COR_SEV.get(r["severidade"], "#6c757d")
        modo    = r.get("modo", "UI")
        cor_modo = "#0d6efd" if modo == "UI" else "#6c757d"
        linhas += f"""
        <tr>
          <td><strong>{r['id']}</strong></td>
          <td>{r['funcionalidade']}</td>
          <td>{r['descricao']}</td>
          <td>{r['esperado']}</td>
          <td>{r['obtido']}</td>
          <td style="color:{cor_st};font-weight:bold;text-align:center">{r['status']}</td>
          <td style="color:{cor_sv};font-weight:bold;text-align:center">{r['severidade']}</td>
          <td style="color:{cor_modo};font-weight:bold;text-align:center">{modo}</td>
          <td style="text-align:center">{r['timestamp']}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Relatório QA — Academia Fitness</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:Arial,sans-serif;background:#f0f2f5;color:#333}}
    header{{background:linear-gradient(135deg,#1a1a2e,#16213e);color:#fff;padding:30px;text-align:center}}
    header h1{{font-size:2.1em}} header p{{opacity:.8;margin-top:6px}}
    .wrap{{max-width:1200px;margin:28px auto;padding:0 20px}}
    .cards{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:22px}}
    .card{{background:#fff;padding:20px;border-radius:10px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.1)}}
    .card .val{{font-size:2.4em;font-weight:bold}}
    .card .lbl{{color:#666;font-size:.85em;margin-top:4px}}
    .prog{{background:#e9ecef;border-radius:8px;height:8px;margin-top:8px}}
    .prog-bar{{height:100%;border-radius:8px;background:{cor_taxa};width:{taxa:.1f}%}}
    .box{{background:#fff;padding:24px;border-radius:10px;margin-bottom:22px;box-shadow:0 2px 8px rgba(0,0,0,.1)}}
    .box h2{{color:#1a1a2e;margin-bottom:16px;padding-bottom:10px;border-bottom:2px solid #e8e8e8}}
    .decisao-wrap{{text-align:center}}
    .badge-dec{{display:inline-block;padding:14px 36px;border-radius:8px;font-size:1.7em;font-weight:bold;color:#fff;background:{cor_dec}}}
    .badge-dec-txt{{margin-top:12px;color:#555}}
    table{{width:100%;border-collapse:collapse;font-size:.88em}}
    th{{background:#1a1a2e;color:#fff;padding:11px 9px;text-align:left}}
    td{{padding:9px;border-bottom:1px solid #eee;vertical-align:top}}
    tr:nth-child(even){{background:#f9f9f9}} tr:hover{{background:#eef2ff}}
    .leg{{display:flex;gap:18px;flex-wrap:wrap;margin-top:10px}}
    .leg-i{{display:flex;align-items:center;gap:7px;font-size:.85em}}
    .dot{{width:11px;height:11px;border-radius:50%}}
    footer{{text-align:center;padding:18px;color:#888;font-size:.82em}}
  </style>
</head>
<body>
  <header>
    <h1>Relatório de Qualidade de Software</h1>
    <p>Academia Fitness &mdash; Gerado em {agora}</p>
  </header>

  <div class="wrap">
    <!-- Métricas -->
    <div class="cards">
      <div class="card"><div class="val" style="color:#1a1a2e">{total}</div><div class="lbl">Total de Testes</div></div>
      <div class="card"><div class="val" style="color:#28a745">{aprovados}</div><div class="lbl">Aprovados (PASS)</div></div>
      <div class="card"><div class="val" style="color:#dc3545">{reprovados}</div><div class="lbl">Reprovados (FAIL)</div></div>
      <div class="card"><div class="val" style="color:#dc3545">{criticos}</div><div class="lbl">Falhas Críticas</div></div>
      <div class="card">
        <div class="val" style="color:{cor_taxa}">{taxa:.1f}%</div>
        <div class="lbl">Taxa de Aprovação</div>
        <div class="prog"><div class="prog-bar"></div></div>
      </div>
    </div>

    <!-- Decisão QA -->
    <div class="box">
      <h2>Decisão Final de QA</h2>
      <div class="decisao-wrap">
        <div class="badge-dec">{icone} {decisao}</div>
        <p class="badge-dec-txt">{texto_dec}</p>
      </div>
    </div>

    <!-- Tabela de casos de teste -->
    <div class="box">
      <h2>Casos de Teste Executados</h2>
      <table>
        <tr>
          <th>ID</th><th>Funcionalidade</th><th>Descrição</th>
          <th>Resultado Esperado</th><th>Resultado Obtido</th>
          <th style="text-align:center">Status</th>
          <th style="text-align:center">Severidade</th>
          <th style="text-align:center">Modo</th>
          <th style="text-align:center">Horário</th>
        </tr>
        {linhas}
      </table>
    </div>

    <!-- Legenda -->
    <div class="box">
      <h2>Legenda de Severidade e Critérios de Decisão</h2>
      <div class="leg">
        <div class="leg-i"><div class="dot" style="background:#dc3545"></div><span><strong>CRÍTICA</strong> — Falha compromete segurança ou integridade dos dados</span></div>
        <div class="leg-i"><div class="dot" style="background:#fd7e14"></div><span><strong>ALTA</strong> — Falha compromete funcionalidade principal</span></div>
        <div class="leg-i"><div class="dot" style="background:#ffc107"></div><span><strong>MÉDIA</strong> — Inconveniência, não bloqueia o sistema</span></div>
        <div class="leg-i"><div class="dot" style="background:#28a745"></div><span><strong>BAIXA</strong> — Impacto mínimo, sem risco operacional</span></div>
      </div>
      <ul style="margin-top:16px;margin-left:18px;color:#555;line-height:1.9">
        <li><strong>LIBERADO</strong> — 0 falhas</li>
        <li><strong>LIBERADO COM RESSALVAS</strong> — Apenas falhas não-críticas</li>
        <li><strong>NÃO LIBERAR</strong> — Pelo menos 1 falha CRÍTICA</li>
      </ul>
    </div>
  </div>

  <footer>Relatório gerado automaticamente pelo sistema de QA &mdash; Academia Fitness</footer>
</body>
</html>"""

    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(html)

    return arquivo
