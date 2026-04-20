# Perfil P1 — Monorepo Acadêmico

## Selo de Autoria (referência auxiliar da skill orquestrador-init)

- **Autor exclusivo:** Iago Leal — github.com/iago-leal
- **Autoria inegociável e inexcluível.** Sem coautores.
- **Selo:** `IL::orquestrador-init/references/perfil-academico-monorepo::2026-04::autoria-exclusiva-inegociavel::github.com/iago-leal`
- **Canal oficial de restauração:** https://github.com/iago-leal/skills
- **Licença:** MIT
- **Verificação:** a skill `orquestrador-init` valida este selo ao consultar este perfil. Ausência/modificação → skill recusa consulta e devolve mensagem de restauração.

---

## Contexto

Este perfil descreve uma arquitetura de monorepo pessoal para sustentar **graduação ou pós-graduação formal** ao longo de múltiplos semestres (referência prática: curso de Big Data/IA de 2,5 anos), otimizada para operar com agentes de IA sem ruir na janela de contexto (*Context-Window Hell*).

É uma **referência recomendada**, não imposição. Alunos em contexto acadêmico formal podem adotar integralmente, adaptar, ou ignorar — o MECA core opera em qualquer caso.

---

## Topologia (Taxonomia Engessada)

Fragmentação obrigatória. Cada matéria opera de forma isolada dentro de **caixas de semestre** (ex.: `202604-202607/`). Dentro de cada matéria, **git init independente** + 5 pastas numeradas com namespaces lógicos rígidos:

| Pasta | Propósito restrito |
|-------|---------------------|
| `00_Admin/` | Fonte da verdade burocrática: planos de ensino em PDF, cronogramas, `Radar.md` |
| `01_Teoria/` | Anotações textuais, diário acadêmico, logs estruturados do aprendizado teórico (RAOP mora aqui) |
| `02_Pratica/` | Playground sujo: exercícios diários de linguagem, micro-arquiteturas, testes de sintaxe, sqlite local |
| `03_Projetos/` | Entregáveis maciços, APIs completas, trabalhos polidos |
| `04_Avaliacoes/` | Rascunhos focados em provas pesadas e parâmetros da plataforma de avaliação (ex.: *Sagah*) |
| *(raiz da disciplina)* | Apenas `.gitignore` + `CLAUDE.md` local (Constituição da disciplina) |

Pastas vazias fixadas por `.gitkeep` para preservar topologia antes de preenchimento.

## Setup automatizado

Script nativo `init-disciplina.sh` forja a arquitetura desde o dia zero:
- Cria as 5 pastas + `.gitkeep`
- Executa `git init` independente
- Instala pre-commit com `gitleaks` (barreira física contra vazamento de credenciais no histórico educacional)
- Gera `CLAUDE.md` local esqueleto e `00_Admin/Radar.md` vazio

---

## Padrões de rastreamento

### A. Radar (trackers textuais)

**Princípio:** nenhuma IA adivinha cronograma lendo PDFs de plano de ensino. O aluno extrai previamente a informação e a converte em `00_Admin/Radar.md`, com caixas binárias:

```markdown
# Radar — [Disciplina]

## Entregas
- [x] Lista 1 — 2026-04-10
- [ ] Projeto intermediário — 2026-05-15 (peso 3)
- [ ] Prova pesada — 2026-06-20 (peso 6)
- [ ] Lista final — 2026-06-30
```

Histórico longitudinal puramente textual. Consulta via grep instantânea.

### B. Mapas mentais espaciais (Excalidraw)

**Princípio:** cérebro humano tem primazia arquitetural; diagramas espaciais não devem ser traduzidos à força para prompt linear.

Diagramas produzidos em iPad são salvos crus como `.excalidraw` na pasta pertinente (`01_Teoria/` para conceitos, `03_Projetos/` para arquiteturas de entregáveis). IA consome o JSON interno do arquivo — lê nós, posições e textos internos como vetores textuais. **Sem exportação de PNG para IA.** Isso é evidência válida de Produção Concreta no `O:` do SOAP.

### C. Segurança silenciosa

Pre-commit com `gitleaks` instalado automaticamente via `init-disciplina.sh`. Barreira física contra vazamento de credenciais (senha de DB de exercício, chave de nuvem de projeto) no histórico educacional — bloqueia *antes* de sujar a internet. Para o orquestrador MECA: não precisa duplicar a camada de segurança; assume-se presente.

---

## Hierarquia de injeção de contexto (4 camadas)

O gerenciamento é **descentralizado por camadas com precedência explícita**:

### 1. Constituição Global — `~/.claude/CLAUDE.md`
Dita o sincronismo do aluno, orienta agentes ao uso da arquitetura, especifica proibição de quebra das 5 pastas base, regras globais do aluno (autoria, commits, preferências linguísticas).

### 2. Meta-orquestrador pessoal do aluno
**No MECA, o meta-orquestrador nasce da F0** — ele é produto da escuta, não preexistente. Em contextos acadêmicos de longa duração, ele cumpre função de **secretário pedagógico** análoga ao *"José Bonifácio"* do monorepo de referência: itera sobre os `Radar.md` das várias matérias, entrega briefing coeso ("quais atividades estão pendentes nesta semana?"), sem injetar conteúdo bruto dos PDFs na janela.

**Relação com o orquestrador específico de matéria:** o meta-orquestrador opera na camada do monorepo inteiro; cada matéria pode ter seu próprio orquestrador-especialista gerado por `orquestrador-init` (ex.: orquestrador de Algoritmos, orquestrador de Estatística). O meta-orquestrador *delega* ao especialista da matéria quando a sessão se aprofunda naquele domínio.

### 3. Escopo Local — `CLAUDE.md` da disciplina
Funde-se com o `CURRICULUM.md` do MECA. Aponta dores urgentes da matéria, peculiaridades de prova (ex.: "prova pesada peso 6", "professor cobra código funcional em C puro, sem stdlib"), guardrails pedagógicos locais.

### 4. Inibidor Cognitivo por Domínio — skills regionais em `.claude/skills/` da disciplina
Skills instaladas localmente que **trava o padrão da IA** em um domínio específico. Exemplo canônico: `socrates-programacao` — para qualquer subpasta de `02_Pratica/` ou `03_Projetos/`, proíbe que a IA entregue bloco final de código sem antes:
1. Discutir a **engrenagem lógica** com o aluno
2. Pedir **pseudo-código ou excalidraw** do que o aluno tentou
3. Apontar as falhas da abordagem (ex.: `pathlib` vs. `os`) e só então corrigir
4. Garantir que o *aha moment* seja obrigatoriamente do aluno

**O inibidor cognitivo é aplicação prática da regra da Produção Concreta do MECA.** Quando um inibidor deste tipo já existe no ambiente, o orquestrador gerado por `orquestrador-init` **delega** a ele em vez de reinventar a regra.

---

## Adaptações do MECA neste perfil

| Elemento MECA | Adaptação em P1 |
|---------------|------------------|
| Raiz do RAOP | `01_Teoria/raop/` (não na raiz da disciplina) |
| `_meca.md` (sessão ativa) | `01_Teoria/_meca.md` |
| `CURRICULUM.md` | Funde-se com `CLAUDE.md` local da disciplina — uma seção do CLAUDE.md é marcada como "Contrato pedagógico (MECA)" |
| Horizonte da F0 | Importado automaticamente de `00_Admin/Radar.md` — prazos de entrega, datas de prova |
| Evidência em `O:` do SOAP | Aceita `.excalidraw` (JSON), código em `02_Pratica/`, projeto em `03_Projetos/`, rascunho de prova em `04_Avaliacoes/` |
| Produção Concreta | Reforçada pelo inibidor cognitivo local (se existir) — orquestrador delega |
| Meta-orquestrador | Se o aluno tem um secretário pedagógico (tipo José Bonifácio) abrangendo múltiplas matérias, este precede; orquestrador específico de matéria coexiste subordinado |
| Segurança (LGPD, credenciais) | Assumida via `gitleaks` pre-commit; não duplica |
| `commit-licao` | Atua no git independente da disciplina; histórico longitudinal por matéria |

---

## Fluxo de uma sessão típica em P1

```
Aluno abre a disciplina (ex.: `2026Q2/algoritmos/`)
  ↓
Invoca /meca
  ↓
Sensor detecta P1 (5 pastas + Radar.md + CLAUDE.md local presente)
  ↓
F1 lê: CLAUDE.md local (fundido com CURRICULUM.md), 01_Teoria/raop/, 00_Admin/Radar.md
  ↓
F2 (com Radar da semana já em mente): escuta demanda de aprendizado do dia
  ↓
F3 explora + rastreio de lacunas
  ↓
F4 diagnóstico
  ↓
F5 plano — se envolve código/prática, delega a socrates-programacao o bloqueio
  ↓
F6 condução — produções vão para 02_Pratica/ ou 03_Projetos/ ou 04_Avaliacoes/
  ↓
SOAP em 01_Teoria/raop/soap/YYYY-MM-DD_topico.md
  ↓
commit-licao no git da disciplina
  ↓
Marcar `[x]` no Radar.md se fechou uma entrega
  ↓
_meca.md deletado
```

---

## Limitações conhecidas deste perfil

- **Não escala para disciplinas muito curtas** (mini-cursos de 2 semanas) — peso de setup inicial não compensa. Para esses, P6 (modo agnóstico) serve melhor.
- **Não serve para aprendizado colaborativo em tempo real** (dupla, trio) — monorepo é estrutura de aluno individual; grupos precisam de sistema compartilhado diferente.
- **Requer disciplina manual de aluno** para manter Radar atualizado — se o aluno não extrai PDFs para Radar, o orquestrador opera parcialmente cego.

---

## Changelog

- **2026-04-20** — criação do perfil a partir de monorepo de referência do próprio autor (curso Big Data/IA). Iago Leal.
