"""
Ponto de entrada principal do sistema de QA.

Como executar:
    python run_qa.py           -> testes normais (sem bug)
    python run_qa.py --bug     -> ativa o bug proposital antes de rodar

Requisitos:
    pip install flask playwright
    playwright install chromium
"""
import subprocess
import sys
import time
import os
import urllib.request
import urllib.error
import argparse
from datetime import datetime

# ── Argumento de linha de comando para o bug proposital ───────────────────────
parser = argparse.ArgumentParser(description="QA Automático — Academia Fitness")
parser.add_argument("--bug",      action="store_true", help="Ativa o bug proposital para demonstração")
parser.add_argument("--headless", action="store_true", help="Executa sem abrir o navegador (mais rápido)")
args = parser.parse_args()

import re

# Ativa/desativa o bug editando apenas a linha de atribuição em sistema_academia.py
def _set_bug(ativo: bool):
    caminho = os.path.join(os.path.dirname(__file__), "sistema_academia.py")
    with open(caminho, "r", encoding="utf-8") as f:
        conteudo = f.read()
    conteudo = re.sub(
        r"^BUG_ATIVO = (True|False)",
        f"BUG_ATIVO = {ativo}",
        conteudo,
        flags=re.MULTILINE,
    )
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)


def _aguardar_flask(url, tentativas=12, espera=0.5):
    for _ in range(tentativas):
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except Exception:
            time.sleep(espera)
    return False


def _linha(char="─", n=62):
    print(char * n)


def main():
    _linha("═")
    print("  SISTEMA QA — ACADEMIA FITNESS")
    print(f"  Playwright | {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    _linha("═")

    # Configurar bug
    if args.bug:
        _set_bug(True)
        print("\n  *** BUG PROPOSITAL ATIVADO (BUG_ATIVO = True) ***")
    else:
        _set_bug(False)

    # ── 1. Iniciar Flask ───────────────────────────────────────────────────────
    print("\n[1/3] Iniciando servidor Flask na porta 5000...")
    flask_proc = subprocess.Popen(
        [sys.executable, os.path.join(os.path.dirname(__file__), "app.py")],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if not _aguardar_flask("http://localhost:5000"):
        print("  ERRO: Não foi possível iniciar o servidor Flask.")
        flask_proc.terminate()
        sys.exit(1)

    print("  Servidor iniciado com sucesso em http://localhost:5000")

    try:
        # ── 2. Executar testes ─────────────────────────────────────────────────
        print("\n[2/3] Executando casos de teste com Playwright...")
        _linha()

        from testes_playwright import executar_testes
        if not args.headless:
            print("  Abrindo navegador Edge para demonstração visual...")
        resultados = executar_testes(headless=args.headless, verbose=True)

        _linha()

        # ── Métricas ───────────────────────────────────────────────────────────
        total      = len(resultados)
        aprovados  = sum(1 for r in resultados if r["status"] == "PASS")
        reprovados = total - aprovados
        taxa       = (aprovados / total * 100) if total else 0
        criticos   = sum(1 for r in resultados if r["status"] == "FAIL" and r["severidade"] == "CRITICA")

        if reprovados == 0:
            decisao = "LIBERADO"
        elif criticos > 0:
            decisao = "NAO LIBERAR"
        else:
            decisao = "LIBERADO COM RESSALVAS"

        print(f"\n  Total de testes  : {total}")
        print(f"  Aprovados (PASS) : {aprovados}")
        print(f"  Reprovados (FAIL): {reprovados}")
        print(f"  Falhas críticas  : {criticos}")
        print(f"  Taxa de aprovação: {taxa:.1f}%")
        print(f"\n  DECISAO FINAL DE QA: >>> {decisao} <<<")

        if reprovados:
            print("\n  DEFEITOS ENCONTRADOS:")
            for r in resultados:
                if r["status"] == "FAIL":
                    print(f"    {r['id']} [{r['severidade']}] {r['descricao']}")
                    print(f"          Esperado : {r['esperado']}")
                    print(f"          Obtido   : {r['obtido']}")

        # ── 3. Gerar relatório ─────────────────────────────────────────────────
        print("\n[3/3] Gerando relatório HTML...")
        from relatorio import gerar_relatorio
        arquivo = gerar_relatorio(resultados)
        caminho_abs = os.path.abspath(arquivo)
        print(f"  Relatório salvo em: {caminho_abs}")

        # Abre o relatório no navegador padrão
        try:
            import webbrowser
            webbrowser.open(caminho_abs)
        except Exception:
            pass

    finally:
        flask_proc.terminate()
        flask_proc.wait()
        # Garante que o bug é desativado após a execução com --bug
        if args.bug:
            _set_bug(False)

    _linha("═")
    print(f"  CONCLUIDO — {datetime.now().strftime('%H:%M:%S')}")
    _linha("═")


if __name__ == "__main__":
    main()
