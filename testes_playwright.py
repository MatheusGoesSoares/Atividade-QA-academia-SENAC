"""
Casos de Teste - Sistema Academia Fitness
Automação de interface web com Playwright (browser real)
"""
import json as _json
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5000"
_H = {"Content-Type": "application/json"}


def _resultado(id, funcionalidade, descricao, esperado, obtido, passou, severidade="MEDIA", modo="UI"):
    return {
        "id": id,
        "funcionalidade": funcionalidade,
        "descricao": descricao,
        "esperado": esperado,
        "obtido": obtido,
        "status": "PASS" if passou else "FAIL",
        "severidade": severidade if not passou else "-",
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "modo": modo,
    }


def executar_testes(headless=False, verbose=True):
    resultados = []

    def log(tc, status, msg=""):
        if verbose:
            simbolo = "  [PASS]" if status == "PASS" else "  [FAIL]"
            print(f"{simbolo} {tc} — {msg}")

    # slow_mo desacelera cada ação individual; pausa_resultado dá tempo para ver o resultado
    slow_mo        = 0    if headless else 700
    pausa_resultado = 0   if headless else 2200   # ms visível na tela após cada resultado

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=headless, slow_mo=slow_mo)
        ctx = browser.new_context()
        page = ctx.new_page()
        api = ctx.request

        # ── Helpers de API (setup/teardown sem passar pela UI) ────────────────

        def jpost(rota, corpo=None):
            return api.post(
                f"{BASE_URL}{rota}",
                data=_json.dumps(corpo) if corpo is not None else "",
                headers=_H,
            )

        # ── Helpers de browser ────────────────────────────────────────────────

        _ABAS = {
            "cadastro": "Cadastrar Membro",
            "checkin":  "Check-in",
            "cancelar": "Cancelar Matrícula",
            "renovar":  "Renovar Plano",
            "membros":  "Ver Membros",
        }

        def ir_para_aba(nome):
            """Clica no botão de aba correspondente."""
            page.locator(f'button.tab-btn:has-text("{_ABAS[nome]}")').click()

        def limpar_resultado(res_id):
            """Oculta o div de resultado para detectar a próxima resposta."""
            page.evaluate(f"document.getElementById('{res_id}').style.display = 'none'")

        def obter_resultado(res_id, timeout=6000):
            """Aguarda o resultado aparecer e retorna o texto (sem pausar ainda)."""
            page.wait_for_selector(f"#{res_id}", state="visible", timeout=timeout)
            return page.inner_text(f"#{res_id}").strip()

        def eh_sucesso(res_id):
            """True se a classe CSS do resultado indicar verde (sucesso)."""
            return "sucesso" in (page.get_attribute(f"#{res_id}", "class") or "")

        def exibir_popup(tc_id, passou, severidade, descricao, resultado_obtido):
            """Injeta um popup flutuante no browser com o resultado do teste."""
            if not pausa_resultado:
                return
            cor_fundo  = "#1e7e34" if passou else "#c82333"
            cor_borda  = "#28a745" if passou else "#dc3545"
            status_txt = "PASS ✓" if passou else "FAIL ✗"
            sev_txt    = "" if passou else f'<div style="margin-top:6px;font-size:13px;opacity:.9">Severidade: <strong>{severidade}</strong></div>'
            page.evaluate(f"""
                (() => {{
                    const old = document.getElementById('__qa_popup__');
                    if (old) old.remove();
                    const el = document.createElement('div');
                    el.id = '__qa_popup__';
                    el.innerHTML = `
                        <div style="font-size:11px;opacity:.8;letter-spacing:1px">RESULTADO DO TESTE</div>
                        <div style="font-size:22px;font-weight:bold;margin:6px 0">{tc_id} — {status_txt}</div>
                        <div style="font-size:13px;opacity:.9">{descricao}</div>
                        {sev_txt}
                        <div style="margin-top:8px;font-size:12px;opacity:.75;border-top:1px solid rgba(255,255,255,.3);padding-top:6px">{resultado_obtido}</div>
                    `;
                    Object.assign(el.style, {{
                        position: 'fixed', top: '50%', left: '50%',
                        transform: 'translate(-50%, -50%)',
                        background: '{cor_fundo}', border: '3px solid {cor_borda}',
                        color: '#fff', padding: '28px 36px', borderRadius: '12px',
                        boxShadow: '0 12px 40px rgba(0,0,0,.5)', zIndex: '99999',
                        minWidth: '380px', textAlign: 'center',
                        fontFamily: 'Arial, sans-serif', animation: 'none'
                    }});
                    document.body.appendChild(el);
                }})()
            """)
            page.wait_for_timeout(pausa_resultado)
            page.evaluate("const el = document.getElementById('__qa_popup__'); if(el) el.remove();")

        # ── Inicialização ─────────────────────────────────────────────────────
        jpost("/reset")
        page.goto(BASE_URL)
        page.wait_for_selector("h1")

        # ══════════════════════════════════════════════════════════════════════
        # TC001 — Página carrega com título e 5 abas de navegação  [UI]
        # ══════════════════════════════════════════════════════════════════════
        try:
            titulo = page.inner_text("h1")
            n_abas = page.locator("button.tab-btn").count()
            passou = len(titulo) > 0 and n_abas == 5
            msg = f'Título: "{titulo}" | Abas: {n_abas}'
            resultados.append(_resultado(
                "TC001", "Interface Web",
                "Verificar se a página carrega com título e as 5 abas de navegação",
                "Título visível e 5 abas exibidas corretamente",
                msg, passou, "BAIXA",
            ))
            log("TC001", resultados[-1]["status"], msg)
            exibir_popup("TC001", passou, "BAIXA", "Página carrega título e 5 abas", msg)
        except Exception as e:
            resultados.append(_resultado("TC001", "Interface Web", "Página carrega corretamente", "Título + 5 abas", f"Erro: {e}", False, "ALTA"))
            log("TC001", "FAIL", str(e))
            exibir_popup("TC001", False, "ALTA", "Página carrega corretamente", str(e))

        # ══════════════════════════════════════════════════════════════════════
        # TC002 — Cadastrar membro válido preenchendo o formulário  [UI]
        # ══════════════════════════════════════════════════════════════════════
        try:
            ir_para_aba("cadastro")
            page.fill("#cad-nome", "Ana Lima")
            page.fill("#cad-cpf", "100.200.300-01")
            page.fill("#cad-idade", "25")
            page.select_option("#cad-plano", "mensal")
            limpar_resultado("res-cadastro")
            page.locator("#tab-cadastro button.btn").click()
            texto = obter_resultado("res-cadastro")
            passou = eh_sucesso("res-cadastro") and "sucesso" in texto.lower()
            resultados.append(_resultado(
                "TC002", "RF01 - Cadastro de Membros",
                "Preencher formulário de cadastro com dados válidos e submeter",
                "Formulário aceito e mensagem de sucesso exibida na tela",
                texto, passou, "ALTA",
            ))
            log("TC002", resultados[-1]["status"], texto)
            exibir_popup("TC002", passou, "ALTA", "Cadastro com dados válidos", texto)
        except Exception as e:
            resultados.append(_resultado("TC002", "RF01 - Cadastro de Membros", "Cadastrar via formulário", "Sucesso na tela", f"Erro: {e}", False, "ALTA"))
            log("TC002", "FAIL", str(e))
            exibir_popup("TC002", False, "ALTA", "Cadastro com dados válidos", str(e))

        # ══════════════════════════════════════════════════════════════════════
        # TC003 — Formulário rejeita CPF já cadastrado  [UI]
        # ══════════════════════════════════════════════════════════════════════
        try:
            ir_para_aba("cadastro")
            page.fill("#cad-nome", "Clone Silva")
            page.fill("#cad-cpf", "100.200.300-01")
            page.fill("#cad-idade", "30")
            page.select_option("#cad-plano", "anual")
            limpar_resultado("res-cadastro")
            page.locator("#tab-cadastro button.btn").click()
            texto = obter_resultado("res-cadastro")
            passou = not eh_sucesso("res-cadastro") and "cpf" in texto.lower()
            resultados.append(_resultado(
                "TC003", "RF01 - Cadastro de Membros",
                "Submeter formulário com CPF já cadastrado",
                "Mensagem de erro de CPF duplicado exibida na tela",
                texto, passou, "ALTA",
            ))
            log("TC003", resultados[-1]["status"], texto)
            exibir_popup("TC003", passou, "ALTA", "Rejeitar CPF duplicado", texto)
        except Exception as e:
            resultados.append(_resultado("TC003", "RF01 - Cadastro de Membros", "Rejeitar CPF duplicado via UI", "Erro na tela", f"Erro: {e}", False, "ALTA"))
            log("TC003", "FAIL", str(e))
            exibir_popup("TC003", False, "ALTA", "Rejeitar CPF duplicado", str(e))

        # ══════════════════════════════════════════════════════════════════════
        # TC004 — Formulário rejeita idade menor que 16 anos  [UI]
        # ══════════════════════════════════════════════════════════════════════
        try:
            ir_para_aba("cadastro")
            page.fill("#cad-nome", "Junior Silva")
            page.fill("#cad-cpf", "999.888.777-00")
            page.fill("#cad-idade", "14")
            page.select_option("#cad-plano", "mensal")
            limpar_resultado("res-cadastro")
            page.locator("#tab-cadastro button.btn").click()
            texto = obter_resultado("res-cadastro")
            passou = not eh_sucesso("res-cadastro") and "16" in texto
            resultados.append(_resultado(
                "TC004", "RF01 - Cadastro de Membros",
                "Submeter formulário com campo idade preenchido como 14",
                "Mensagem de erro com idade mínima (16 anos) exibida na tela",
                texto, passou, "ALTA",
            ))
            log("TC004", resultados[-1]["status"], texto)
            exibir_popup("TC004", passou, "ALTA", "Rejeitar menor de 16 anos", texto)
        except Exception as e:
            resultados.append(_resultado("TC004", "RF01 - Cadastro de Membros", "Rejeitar menor de 16 via UI", "Erro na tela", f"Erro: {e}", False, "ALTA"))
            log("TC004", "FAIL", str(e))
            exibir_popup("TC004", False, "ALTA", "Rejeitar menor de 16 anos", str(e))

        # ══════════════════════════════════════════════════════════════════════
        # TC005 — Servidor rejeita plano inválido (injeção de opção via JS)  [UI]
        # ══════════════════════════════════════════════════════════════════════
        try:
            ir_para_aba("cadastro")
            page.fill("#cad-nome", "Hacker Plano")
            page.fill("#cad-cpf", "555.444.333-00")
            page.fill("#cad-idade", "22")
            page.evaluate("""
                const sel = document.getElementById('cad-plano');
                const opt = document.createElement('option');
                opt.value = 'diario'; opt.text = 'Diário (inválido)';
                sel.add(opt); sel.value = 'diario';
            """)
            limpar_resultado("res-cadastro")
            page.locator("#tab-cadastro button.btn").click()
            texto = obter_resultado("res-cadastro")
            passou = not eh_sucesso("res-cadastro") and "plano" in texto.lower()
            resultados.append(_resultado(
                "TC005", "RF01 - Cadastro de Membros",
                'Injetar opção de plano inválido "diario" no select via JS e submeter',
                "Servidor rejeita o plano inválido mesmo com manipulação de HTML",
                texto, passou, "MEDIA",
            ))
            log("TC005", resultados[-1]["status"], texto)
            exibir_popup("TC005", passou, "MEDIA", "Rejeitar plano inválido (injeção JS)", texto)
        except Exception as e:
            resultados.append(_resultado("TC005", "RF01 - Cadastro de Membros", "Rejeitar plano inválido (injeção JS)", "Erro na tela", f"Erro: {e}", False, "MEDIA"))
            log("TC005", "FAIL", str(e))
            exibir_popup("TC005", False, "MEDIA", "Rejeitar plano inválido (injeção JS)", str(e))

        # ══════════════════════════════════════════════════════════════════════
        # TC006 — Check-in de membro ativo pelo formulário  [UI]
        # ══════════════════════════════════════════════════════════════════════
        try:
            ir_para_aba("checkin")
            page.fill("#ci-cpf", "100.200.300-01")
            limpar_resultado("res-checkin")
            page.locator("#tab-checkin button.btn").click()
            texto = obter_resultado("res-checkin")
            passou = eh_sucesso("res-checkin") and "sucesso" in texto.lower()
            resultados.append(_resultado(
                "TC006", "RF02 - Check-in",
                "Preencher CPF de membro ativo na aba Check-in e submeter",
                "Check-in realizado e mensagem de sucesso exibida na tela",
                texto, passou, "CRITICA",
            ))
            log("TC006", resultados[-1]["status"], texto)
            exibir_popup("TC006", passou, "CRITICA", "Check-in com matrícula ativa", texto)
        except Exception as e:
            resultados.append(_resultado("TC006", "RF02 - Check-in", "Check-in ativo via UI", "Sucesso na tela", f"Erro: {e}", False, "CRITICA"))
            log("TC006", "FAIL", str(e))
            exibir_popup("TC006", False, "CRITICA", "Check-in com matrícula ativa", str(e))

        # ══════════════════════════════════════════════════════════════════════
        # TC007 — Cancelar matrícula pelo formulário  [UI]
        # ══════════════════════════════════════════════════════════════════════
        try:
            ir_para_aba("cancelar")
            page.fill("#can-cpf", "100.200.300-01")
            limpar_resultado("res-cancelar")
            page.locator("#tab-cancelar button.btn").click()
            texto = obter_resultado("res-cancelar")
            passou = eh_sucesso("res-cancelar") and "cancelada" in texto.lower()
            resultados.append(_resultado(
                "TC007", "RF03 - Cancelamento",
                "Preencher CPF na aba de Cancelamento e submeter",
                "Matrícula cancelada e mensagem de sucesso exibida na tela",
                texto, passou, "ALTA",
            ))
            log("TC007", resultados[-1]["status"], texto)
            exibir_popup("TC007", passou, "ALTA", "Cancelar matrícula existente", texto)
        except Exception as e:
            resultados.append(_resultado("TC007", "RF03 - Cancelamento", "Cancelar matrícula via UI", "Sucesso na tela", f"Erro: {e}", False, "ALTA"))
            log("TC007", "FAIL", str(e))
            exibir_popup("TC007", False, "ALTA", "Cancelar matrícula existente", str(e))

        # ══════════════════════════════════════════════════════════════════════
        # TC008 — Check-in com matrícula cancelada (BUG proposital)  [UI]
        # ══════════════════════════════════════════════════════════════════════
        try:
            ir_para_aba("checkin")
            page.fill("#ci-cpf", "100.200.300-01")
            limpar_resultado("res-checkin")
            page.locator("#tab-checkin button.btn").click()
            texto = obter_resultado("res-checkin")
            passou = not eh_sucesso("res-checkin") and "cancelada" in texto.lower()
            resultados.append(_resultado(
                "TC008", "RF02 - Check-in",
                "Tentar check-in na interface com CPF de matrícula cancelada",
                "Interface exibe mensagem de erro: matrícula cancelada",
                texto, passou, "CRITICA",
            ))
            log("TC008", resultados[-1]["status"], texto)
            exibir_popup("TC008", passou, "CRITICA", "Check-in com matrícula cancelada", texto)
        except Exception as e:
            resultados.append(_resultado("TC008", "RF02 - Check-in", "Rejeitar check-in cancelado via UI", "Erro na tela", f"Erro: {e}", False, "CRITICA"))
            log("TC008", "FAIL", str(e))
            exibir_popup("TC008", False, "CRITICA", "Check-in com matrícula cancelada", str(e))

        # ══════════════════════════════════════════════════════════════════════
        # TC009 — Check-in de CPF inexistente pelo formulário  [UI]
        # ══════════════════════════════════════════════════════════════════════
        try:
            ir_para_aba("checkin")
            page.fill("#ci-cpf", "000.000.000-00")
            limpar_resultado("res-checkin")
            page.locator("#tab-checkin button.btn").click()
            texto = obter_resultado("res-checkin")
            passou = not eh_sucesso("res-checkin") and "encontrado" in texto.lower()
            resultados.append(_resultado(
                "TC009", "RF02 - Check-in",
                "Preencher CPF não cadastrado na aba Check-in e submeter",
                "Interface exibe mensagem de erro: membro não encontrado",
                texto, passou, "ALTA",
            ))
            log("TC009", resultados[-1]["status"], texto)
            exibir_popup("TC009", passou, "ALTA", "Check-in com CPF inexistente", texto)
        except Exception as e:
            resultados.append(_resultado("TC009", "RF02 - Check-in", "Check-in inexistente via UI", "Erro na tela", f"Erro: {e}", False, "ALTA"))
            log("TC009", "FAIL", str(e))
            exibir_popup("TC009", False, "ALTA", "Check-in com CPF inexistente", str(e))

        # ══════════════════════════════════════════════════════════════════════
        # TC010 — Cancelar CPF inexistente pelo formulário  [UI]
        # ══════════════════════════════════════════════════════════════════════
        try:
            ir_para_aba("cancelar")
            page.fill("#can-cpf", "777.666.555-00")
            limpar_resultado("res-cancelar")
            page.locator("#tab-cancelar button.btn").click()
            texto = obter_resultado("res-cancelar")
            passou = not eh_sucesso("res-cancelar") and "encontrado" in texto.lower()
            resultados.append(_resultado(
                "TC010", "RF03 - Cancelamento",
                "Preencher CPF não cadastrado na aba Cancelamento e submeter",
                "Interface exibe mensagem de erro: membro não encontrado",
                texto, passou, "MEDIA",
            ))
            log("TC010", resultados[-1]["status"], texto)
            exibir_popup("TC010", passou, "MEDIA", "Cancelar CPF inexistente", texto)
        except Exception as e:
            resultados.append(_resultado("TC010", "RF03 - Cancelamento", "Cancelar inexistente via UI", "Erro na tela", f"Erro: {e}", False, "MEDIA"))
            log("TC010", "FAIL", str(e))
            exibir_popup("TC010", False, "MEDIA", "Cancelar CPF inexistente", str(e))

        # ══════════════════════════════════════════════════════════════════════
        # TC011 — Renovar plano com dados válidos pelo formulário  [UI]
        # ══════════════════════════════════════════════════════════════════════
        try:
            ir_para_aba("renovar")
            page.fill("#ren-cpf", "100.200.300-01")
            page.select_option("#ren-plano", "anual")
            limpar_resultado("res-renovar")
            page.locator("#tab-renovar button.btn").click()
            texto = obter_resultado("res-renovar")
            passou = eh_sucesso("res-renovar") and "sucesso" in texto.lower()
            resultados.append(_resultado(
                "TC011", "RF04 - Renovação de Plano",
                "Preencher CPF e selecionar plano anual na aba Renovação e submeter",
                "Plano renovado e mensagem de sucesso exibida na tela",
                texto, passou, "ALTA",
            ))
            log("TC011", resultados[-1]["status"], texto)
            exibir_popup("TC011", passou, "ALTA", "Renovar plano válido", texto)
        except Exception as e:
            resultados.append(_resultado("TC011", "RF04 - Renovação de Plano", "Renovar plano via UI", "Sucesso na tela", f"Erro: {e}", False, "ALTA"))
            log("TC011", "FAIL", str(e))
            exibir_popup("TC011", False, "ALTA", "Renovar plano válido", str(e))

        # ══════════════════════════════════════════════════════════════════════
        # TC012 — Renovar plano de CPF inexistente pelo formulário  [UI]
        # ══════════════════════════════════════════════════════════════════════
        try:
            ir_para_aba("renovar")
            page.fill("#ren-cpf", "999.000.111-99")
            page.select_option("#ren-plano", "mensal")
            limpar_resultado("res-renovar")
            page.locator("#tab-renovar button.btn").click()
            texto = obter_resultado("res-renovar")
            passou = not eh_sucesso("res-renovar") and "encontrado" in texto.lower()
            resultados.append(_resultado(
                "TC012", "RF04 - Renovação de Plano",
                "Preencher CPF não cadastrado na aba Renovação e submeter",
                "Interface exibe mensagem de erro: membro não encontrado",
                texto, passou, "MEDIA",
            ))
            log("TC012", resultados[-1]["status"], texto)
            exibir_popup("TC012", passou, "MEDIA", "Renovar CPF inexistente", texto)
        except Exception as e:
            resultados.append(_resultado("TC012", "RF04 - Renovação de Plano", "Renovar inexistente via UI", "Erro na tela", f"Erro: {e}", False, "MEDIA"))
            log("TC012", "FAIL", str(e))
            exibir_popup("TC012", False, "MEDIA", "Renovar CPF inexistente", str(e))

        browser.close()

    return resultados
