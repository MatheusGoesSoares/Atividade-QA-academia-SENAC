# Sistema QA — Academia Fitness

Projeto de **Garantia da Qualidade de Software (QA)** desenvolvido em Python com automação de testes de interface web utilizando **Playwright**. O sistema simula uma academia de ginástica e seus testes verificam as regras de negócio diretamente na interface do navegador.

**Equipe:** Lucas Mendes · Matheus Goes · Wendell Barboza  
**Disciplina:** Qualidade de Software — Prof. Icaro Ferreira · SENAC

---

## Índice

- [Sobre o Sistema](#sobre-o-sistema)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação e Configuração](#instalação-e-configuração)
- [Como Executar](#como-executar)
- [Funcionalidades e Regras de Negócio](#funcionalidades-e-regras-de-negócio)
- [Casos de Teste](#casos-de-teste)
- [Critérios de Decisão de QA](#critérios-de-decisão-de-qa)
- [Bug Proposital](#bug-proposital)
- [Relatório Automático](#relatório-automático)

---

## Sobre o Sistema

O sistema gerencia membros de uma academia fitness com quatro funcionalidades principais: **cadastro de membros**, **check-in**, **cancelamento de matrícula** e **renovação de plano**. Cada funcionalidade possui regras de negócio que são validadas tanto no servidor (Flask) quanto testadas via automação de browser (Playwright).

A automação abre o **Microsoft Edge** de forma controlada, navega pelas abas da interface, preenche formulários, clica em botões e lê os resultados exibidos na tela — exatamente como um usuário faria. Após cada teste, um **popup colorido** aparece no canto da tela indicando se o cenário passou ou falhou.

---

## Tecnologias Utilizadas

| Tecnologia | Função |
|---|---|
| Python 3 | Linguagem principal |
| Flask | Servidor web / API REST |
| Playwright | Automação de browser (Microsoft Edge) |
| HTML / CSS / JavaScript | Interface web do sistema |

---

## Estrutura do Projeto

```
ATV-QA/
│
├── sistema_academia.py     # Regras de negócio (RF01–RF04)
├── app.py                  # API Flask com rotas da aplicação
├── testes_playwright.py    # 12 casos de teste com automação de browser
├── relatorio.py            # Gerador do relatório HTML de QA
├── run_qa.py               # Ponto de entrada — orquestra tudo
├── requirements.txt        # Dependências Python
│
├── templates/
│   └── index.html          # Interface web do sistema (5 abas)
│
└── relatorios/
    └── relatorio_qa.html   # Relatório gerado automaticamente
```

---

## Instalação e Configuração

### Pré-requisitos

- Python 3.8 ou superior
- Microsoft Edge instalado (padrão no Windows 10/11)

### Instalação das dependências

```bash
pip install flask playwright
playwright install msedge
```

> Caso o `pip` não seja reconhecido, utilize `python -m pip install flask playwright`

---

## Como Executar

### Execução padrão — browser visível

```bash
python run_qa.py
```

Abre o Microsoft Edge de forma automatizada. Para cada teste é exibido um **popup** no canto inferior direito do browser indicando o resultado (verde = PASS, vermelho = FAIL). Ao final, o relatório HTML é aberto automaticamente.

### Execução sem abrir o browser (modo rápido)

```bash
python run_qa.py --headless
```

Executa os mesmos testes em segundo plano, sem abrir o browser. Útil quando o foco é apenas o resultado no terminal.

### Execução com o bug proposital ativado

```bash
python run_qa.py --bug
```

Ativa intencionalmente um defeito no sistema para demonstrar que a automação é capaz de detectar falhas. O TC008 falhará com severidade **CRÍTICA**, alterando a decisão de QA para **NÃO LIBERAR**.

### Combinações possíveis

```bash
python run_qa.py               # browser visível, sem bug
python run_qa.py --bug         # browser visível, com bug
python run_qa.py --headless    # sem browser, sem bug
python run_qa.py --bug --headless  # sem browser, com bug
```

---

## Funcionalidades e Regras de Negócio

### RF01 — Cadastro de Membros

Dá permissão para registrar um novo membro informando nome, CPF, idade e plano.

| Regra | Descrição |
|---|---|
| RN01 | CPF deve ser único no sistema |
| RN02 | Idade mínima para cadastro é 16 anos |
| RN03 | Plano deve ser um dos válidos: mensal, trimestral ou anual |

**Planos disponíveis:**

| Plano | Duração | Valor |
|---|---|---|
| Mensal | 30 dias | R$ 99,90 |
| Trimestral | 90 dias | R$ 269,90 |
| Anual | 365 dias | R$ 899,90 |

---

### RF02 — Check-in

Registra a entrada de um membro na academia.

| Regra | Descrição |
|---|---|
| RN04 | Apenas membros cadastrados podem fazer check-in |
| RN05 | Membros com matrícula cancelada não podem fazer check-in |
| RN06 | Membros com matrícula vencida não podem fazer check-in |

---

### RF03 — Cancelamento de Matrícula

Cancela a matrícula de um membro, impedindo futuros check-ins.

| Regra | Descrição |
|---|---|
| RN07 | O CPF informado deve pertencer a um membro cadastrado |

---

### RF04 — Renovação de Plano

Reativa a matrícula de um membro e define um novo plano.

| Regra | Descrição |
|---|---|
| RN08 | O CPF informado deve pertencer a um membro cadastrado |
| RN09 | O novo plano deve ser um dos válidos |
| RN10 | A renovação reativa automaticamente uma matrícula cancelada |

---

## Casos de Teste

São 12 casos de teste organizados por funcionalidade. Todos utilizam automação real de browser: o Playwright abre o Edge, navega pelas abas, preenche os campos e lê a resposta exibida na tela.

| ID | Funcionalidade | Descrição | Tipo | Severidade |
|---|---|---|---|---|
| TC001 | Interface Web | Página carrega com título e 5 abas | Normal | BAIXA |
| TC002 | RF01 - Cadastro | Cadastrar membro com dados válidos | Normal | ALTA |
| TC003 | RF01 - Cadastro | Rejeitar CPF já cadastrado | Erro | ALTA |
| TC004 | RF01 - Cadastro | Rejeitar membro com menos de 16 anos | Erro | ALTA |
| TC005 | RF01 - Cadastro | Rejeitar plano inválido injetado via JS | Erro | MÉDIA |
| TC006 | RF02 - Check-in | Check-in com matrícula ativa | Normal | CRÍTICA |
| TC007 | RF03 - Cancelamento | Cancelar matrícula existente | Normal | ALTA |
| TC008 | RF02 - Check-in | **Rejeitar check-in com matrícula cancelada** | Erro | **CRÍTICA** |
| TC009 | RF02 - Check-in | Rejeitar check-in de CPF inexistente | Erro | ALTA |
| TC010 | RF03 - Cancelamento | Rejeitar cancelamento de CPF inexistente | Erro | MÉDIA |
| TC011 | RF04 - Renovação | Renovar plano de membro cancelado | Normal | ALTA |
| TC012 | RF04 - Renovação | Rejeitar renovação de CPF inexistente | Erro | MÉDIA |

> **TC005** injeta uma opção inválida diretamente no `<select>` do HTML via JavaScript para simular uma tentativa de manipulação de formulário. Isso demonstra que a validação acontece no servidor, não apenas no frontend.

> **TC008** é o teste do bug proposital. Quando o bug está ativo, o sistema permite o check-in de uma matrícula cancelada — o que é detectado pela automação.

---

## Critérios de Decisão de QA

Após a execução de todos os testes, o sistema calcula automaticamente as métricas e emite uma **decisão final de QA**:

| Decisão | Condição |
|---|---|
| ✅ **LIBERADO** | Nenhuma falha encontrada (0 FAILs) |
| ⚠️ **LIBERADO COM RESSALVAS** | Falhas presentes, porém nenhuma crítica |
| ❌ **NÃO LIBERAR** | Pelo menos uma falha com severidade CRÍTICA |

### Métricas geradas

- Total de testes executados
- Quantidade de testes aprovados (PASS)
- Quantidade de testes reprovados (FAIL)
- Quantidade de falhas críticas
- Taxa de aprovação (%)
- Decisão final de QA

---

## Bug Proposital

O projeto inclui um defeito intencional para demonstrar que a automação é capaz de identificar falhas no sistema.

### Qual é o bug?

Quando ativado, o sistema **ignora a verificação de matrícula cancelada** durante o check-in. Ou seja, um membro com matrícula cancelada consegue fazer check-in normalmente, o que não deveria ser permitido.

### Onde está o bug?

Arquivo: `sistema_academia.py`, método `fazer_checkin()`.

```python
# BUG: quando BUG_ATIVO eh True, ignora verificação de matrícula cancelada
if not BUG_ATIVO:
    if not membro.ativo:
        raise ValueError("Matrícula cancelada. Renove para realizar check-in")
```

### Como o bug afeta os resultados?

| | Sem bug | Com bug (`--bug`) |
|---|---|---|
| TC008 | PASS | **FAIL** |
| Falhas críticas | 0 | **1** |
| Taxa de aprovação | 100% | **91,7%** |
| Decisão de QA | LIBERADO | **NÃO LIBERAR** |

### Como ativar para demonstração?

```bash
python run_qa.py --bug
```

O flag `--bug` ativa o defeito automaticamente antes dos testes e o desativa ao final, sem necessidade de editar o código manualmente.

---

## Relatório Automático

Ao final de cada execução, o programa gera automaticamente o arquivo `relatorios/relatorio_qa.html` e o abre no navegador padrão.

O relatório contém:

- **Cards de métricas** — total, aprovados, reprovados, falhas críticas e taxa de aprovação
- **Decisão final de QA** — destaque visual com cor correspondente (verde / amarelo / vermelho)
- **Tabela de casos de teste** — ID, funcionalidade, descrição, resultado esperado, resultado obtido, status, severidade e horário de execução
- **Legenda de severidade** — explicação dos níveis e critérios de decisão

O relatório é legível por qualquer pessoa, mesmo sem conhecimento técnico do sistema, permitindo identificar quais funcionalidades foram testadas, quais passaram, quais falharam e qual foi a decisão sobre a qualidade da versão testada.
