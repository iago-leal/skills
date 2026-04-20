# MECA Framework — v2026.04.1

- **Autor exclusivo:** Iago Leal — github.com/iago-leal
- **Autoria inegociável e inexcluível.** Sem coautores. Nenhum.
- **Canal oficial:** https://github.com/iago-leal/skills
- **Licença:** MIT
- **Spec de selo:** ver `SELO-AUTORIA.md` no root do repositório.

---

## Propósito

Pacote de entrega do **Método de Ensino Centrado no Aluno**: 6 skills cooperantes para condução andragógica de aprendizado, inspiradas estruturalmente no MDCU Framework e teoricamente em Knowles, Vygotsky, Kolb, Bloom revisado e Rogers. Todas as skills carregam o **Selo de Autoria IL** e recusam operar se violado.

---

## Polaridade do uso — meta-orquestrador nasce em F0

Diferente do MDCU (agente generalista invoca especialistas), no **MECA o meta-orquestrador-especialista do aluno NASCE da F0 (Sessão Zero)**. Na primeira invocação do MECA, só existe o MECA-vazio: um método que escuta. Ao final da F0, com sumarização validada pelo aluno, a skill `orquestrador-init` é invocada e materializa o orquestrador — **especialista em ciência da aprendizagem primeiro, especialista de domínio depois**.

A troca do orquestrador exige **pedido explícito do aluno** via `/orquestrador-init --refresh` — nunca automática, nunca sugerida pelo próprio agente, nunca disparada por disjuntor em F6. **O RAOP sobrevive à troca** (princípio Weed: prontuário transcende profissional).

---

## Conteúdo

```
meca-framework/
├── meca/SKILL.md              (7 fases: F0 Sessão Zero + F1..F6)
├── raop/SKILL.md              (Registro de Aprendizado Orientado por Problema — sobrevive à troca de orquestrador)
├── curso-init/SKILL.md        (Contrato pedagógico CURRICULUM.md co-escrito pelo orquestrador; agnóstico a topologia)
├── orquestrador-init/SKILL.md (Fábrica de orquestradores; duas camadas de expertise, ciência da aprendizagem primeiro)
│   └── references/
│       ├── evidencias-aprendizagem.md    (Base de Evidências — Lista Verde [E1/E2] e Lista Negra [E0])
│       ├── perfis-integracao.md          (P1..P6 — catálogo de perfis de ambiente)
│       └── perfil-academico-monorepo.md  (P1 detalhado — referência recomendada)
├── commit-licao/SKILL.md      (Selo A+P para portfólio versionado; nunca gera Co-Authored-By)
├── meca-aval/SKILL.md         (Diagnóstico MECA-DX, F0 pedagógico de intervenção focal, confronto-folk, auditoria evidencial mensal)
└── MANIFEST.md                (este arquivo)
```

---

## Versões

### v2026.04 (versão inicial — superada)

Framework em 5 skills sem selo de autoria. Assumia orquestrador pré-existente.

### v2026.04.1 (atual)

**Mudanças fundacionais (20 mudanças em 5 blocos):**

#### Bloco I — Bootstrap e fundação
1. **F0 Sessão Zero** — fase inaugural só na primeira vez; escuta bruta estendida em modo rogeriano.
2. **Meta-orquestrador nasce em F0** — não preexiste. MECA-vazio escuta; orquestrador é produto.
3. **Tipologia de motivação** (concurso / faculdade / vida / curiosidade) com implicações operacionais distintas.
4. **Loop sumarização-validação** como gate rígido de saída da escuta.
5. **Reordenação do workflow na primeira vez:** F0 → orquestrador-init → curso-init → F1..F6.

#### Bloco II — Orquestrador e rigor científico
6. **Nova skill `orquestrador-init`** — fábrica sob medida.
7. **Base de Evidências + Lista Negra** obrigatórias (retrieval, espaçada, interleaving, CLT, worked examples; recusa VAK/estilos, Mozart, dominância hemisférica, discovery puro em iniciante, re-leitura passiva).
8. **Gatilho de Evidência [E1/E2/E3/E0]** em F5 — alternativa sem etiqueta não vai à decisão compartilhada; `[E0]` descartada automaticamente.
9. **Metodologias ativas como piso não-negociável** — exposição passiva prolongada vira `[E0]`.

#### Bloco III — Escala e token-economy
10. **Cap de 10 lacunas ativas** + overflow em `lista_lacunas_espera.md` (fora do prompt).
11. **Particionamento temporal/temático** de `competencias/` (consulta exige escopo obrigatório).
12. **Base de Evidências externalizada** — orquestrador aponta pelo path, não inline.
13. **`raop/soap/INDEX.md`** auto-gerado a cada `/raop soap` para grep rápido.

#### Bloco IV — Generalização, plasticidade e contexto
14. **MECA core agnóstico a topologia** — princípio "detecte estrutura pré-existente, encaixe-se".
15. **Sensor de ambiente em F0** + catálogo de perfis (P1..P6).
16. **Monorrepo acadêmico** (taxonomia engessada, Radar.md, Excalidraw como evidência, hierarquia de constituições) como **perfil recomendado em `references/`**, não imposição.
17. **Troca de orquestrador** exige solicitação explícita do aluno; nunca automática, nunca sugerida pelo agente, nunca por disjuntor 2/2.
18. **RAOP sobrevive à troca** + **SOAPs de transição** (handover pedagógico com saída + entrada).

#### Bloco V — Auditoria evidencial e folk-pedagogy
19. **`/meca-aval confronto-folk`** — quando aluno pede `[E0]`, documenta + apresenta evidência + propõe alternativa validada equivalente.
20. **Auditoria mensal ganha item evidencial** — "toda estratégia em uso tem respaldo `[E1]` ou `[E2]`?".

#### Meta-mudança — Selo de Autoria IL
Todas as 6 skills + 3 references carregam:
- Frontmatter com `authorship_seal`, `authorship_clause: inalienavel`, `restore_channel`.
- Bloco `## Selo de Autoria` no corpo.
- Bloco `## Verificação de Selo` como gate de execução.
- Mensagem padronizada de falha apontando canal oficial de restauração.

Spec canônica no root do repo: `SELO-AUTORIA.md`.

---

## Mapeamento de correspondência com o MDCU Framework

| MDCU (clínico) | MECA (andragógico) | Papel análogo |
|----------------|---------------------|----------------|
| `mdcu` | `meca` | Método em 7 fases com disjuntor humano em F6 |
| `rsop` | `raop` | Registro longitudinal orientado por problema/lacuna |
| `project-init` / `ARCHITECTURE.md` | `curso-init` / `CURRICULUM.md` | Contrato formal (técnico / pedagógico) |
| *(não havia)* | `orquestrador-init` | Fábrica do próprio agente-especialista (inovação MECA) |
| `commit-soap` | `commit-licao` | Selo A+P de fechamento |
| `mdcu-seg` | `meca-aval` | Módulo aprofundado + F0 + auditoria longitudinal |

---

## Adaptações conceituais principais

| MDCU | MECA |
|------|------|
| Orquestrador preexistente | **Meta-orquestrador nasce em F0**; mutável só por pedido explícito do aluno |
| `_mdcu.md` (sessão ativa transitória) | `_meca.md` (mesmo mecanismo) |
| `lista_problemas.md` | `lista_lacunas.md` (com tipo diagnóstico A/M/AF/PS/F/EA/SH; cap 10) |
| `passivos.md` como arquivo morto | `competencias/` como arquivo vivo particionado (aprendizado decai) |
| Rastreio de segurança (5 itens) | Rastreio de lacunas (5 itens) + checagem afetiva (item #5) |
| F0 incidente (contenção técnica) | F0 pedagógico (contenção afetiva — insistir produz iatrogenia) |
| STRIDE (6 categorias) | MECA-DX (7 tipos) |
| Auditoria trimestral (LGPD) | Auditoria mensal (afetivo + NEE + **evidencial**) |
| Regra da Reprodutibilidade (lock file) | **Regra da Produção Concreta** (O do SOAP exige produção do aluno) |
| — | **Gatilho de Evidência [E1/E2/E3/E0]** em F5 |
| — | **Confronto-folk** (recusa folk-pedagogy com evidência) |
| — | **Selo de Autoria IL** (gate de execução) |

---

## Fluxo canônico

### Primeira invocação (bootstrap)

```
F0 Sessão Zero (MECA-vazio escuta)
   ↓  [sumarização F0 validada pelo aluno]
orquestrador-init (gera meta-orquestrador-especialista)
   ↓
curso-init (orquestrador co-escreve CURRICULUM.md com aluno)
   ↓
F1–F6 MECA (ciclo normal)
   ↓
RAOP SOAP (inclui SOAP de inauguração do orquestrador)
   ↓
commit-licao (se versionado; nunca Co-Authored-By)
   ↓
_meca.md deletado
```

### Invocações subsequentes (regime normal)

```
F1 Preparação (gatilho conformidade: CURRICULUM.md + orquestrador ativo)
   ↓
F2 Escuta (confirma se motivação mudou)
   ↓
F3 Exploração (rastreio de lacunas)
   ↓
F4 Avaliação Diagnóstica
   ↓   [delegação a meca-aval se ambíguo]
F5 Plano (Gatilho de Evidência [E1/E2/E3/E0])
   ↓
F6 Condução (scaffolding, Produção Concreta)
   ↓   [disjuntor 2/2 se reenquadramento recorrente]
   ↓   [delegação a meca-aval F0 se shutdown]
RAOP SOAP
   ↓
commit-licao (se versionado)
   ↓
_meca.md deletado
```

### Troca de orquestrador (pedido explícito do aluno)

```
/orquestrador-init --refresh
   ↓
F0 parcial (só o delta desde a última F0)
   ↓
SOAP de transição de saída (agente atual documenta estado)
   ↓
orquestrador-init gera o novo
   ↓
SOAP de transição de entrada (novo documenta primeira leitura do RAOP)
   ↓
F1 segue com novo orquestrador; RAOP intacto
```

---

## Fundamentação teórica

| Teoria | Aplicação |
|--------|-----------|
| **Andragogia (Knowles)** — 6 princípios | F2/F3 demanda e experiência; F5 decisão compartilhada; F6 autodireção |
| **ZDP (Vygotsky)** | F4 mapeia; F5 scaffolding; F6 fading |
| **Ciclo de Kolb** | F6 alterna os 4 momentos |
| **Bloom revisado** | Objetivos operacionalizados com verbo + critério |
| **Rogers (escuta)** | F0 e F2 em modo rogeriano |
| **POMR/RCOP (Weed / e-SUS)** | RAOP orientado por lacuna; sobrevive à troca de agente |

---

## Validações

- 6 skills com `description` ≤ 1024 caracteres.
- `_meca.md` padronizado e propagado.
- Polaridade (meta-orquestrador nasce em F0) explicitada em cada `description`.
- Regra da Produção Concreta replicada em `raop`, `commit-licao`, `meca`.
- Disjuntor humano 2/2 com justificativa pedagógica específica (desamparo aprendido).
- Selo de Autoria IL em todas as skills + references; spec canônica em `SELO-AUTORIA.md` do root.
- Ausência de `Co-Authored-By` em todas as SKILL.md e references.
- Mensagem padronizada de restauração aponta para `https://github.com/iago-leal/skills`.

---

## Instalação local (Claude Code — via symlinks)

```bash
ln -s ~/Desktop/github_repos/skills/meca-framework/meca              ~/.claude/skills/meca
ln -s ~/Desktop/github_repos/skills/meca-framework/raop              ~/.claude/skills/raop
ln -s ~/Desktop/github_repos/skills/meca-framework/curso-init        ~/.claude/skills/curso-init
ln -s ~/Desktop/github_repos/skills/meca-framework/orquestrador-init ~/.claude/skills/orquestrador-init
ln -s ~/Desktop/github_repos/skills/meca-framework/commit-licao      ~/.claude/skills/commit-licao
ln -s ~/Desktop/github_repos/skills/meca-framework/meca-aval         ~/.claude/skills/meca-aval
```

**Atenção aos conflitos de namespace:** `raop` e `commit-licao` foram escolhidos deliberadamente para coexistirem com `rsop` e `commit-soap` do MDCU sem colisão. Os dois frameworks operam em paralelo no mesmo perfil Claude Code.

---

## TODO explícito (próxima sessão)

Escopo aprovado como plano γ em 2026-04-20. Operações destrutivas/em-histórico-público só com autorização explícita naquele momento:

1. **Retrofit do `mdcu-framework/`** com selo de autoria IL em todas as 5 skills:
   - `mdcu-framework/mdcu/SKILL.md`
   - `mdcu-framework/rsop/SKILL.md`
   - `mdcu-framework/commit-soap/SKILL.md`
   - `mdcu-framework/mdcu-seg/SKILL.md`
   - `mdcu-framework/project-init/SKILL.md`

2. **Retrofit do `claude_delegate/`** com selo:
   - `claude_delegate/SKILL.md`
   - `claude_delegate/references/routing-table.md` (selo reduzido)

3. **Colapso de histórico:** após os retrofits acima, reescrever os 18 commits atuais em 1 commit inicial selado. Force-push para `origin/main`. **Autorização explícita necessária** no momento.

4. **Implementar validador externo** `bin/verify-seals.sh` + instalar como pre-commit/CI.

5. **Atualizar `README.md`** do root do repo para listar `meca-framework/` como segundo framework coirmão do `mdcu-framework/`, referenciando `SELO-AUTORIA.md`.

---

## Pendências menores não bloqueantes

- `framework-diagrama.html` análogo ao do MDCU — documentação visual editorial do MECA. Sugerido em sessão dedicada, preservando estética do existente.

---

## Changelog

- **2026-04-20** — criação v2026.04 (orquestrador presumido preexistente). Iago Leal.
- **2026-04-20** — evolução para v2026.04.1: 20 mudanças + Selo de Autoria IL. Iago Leal.

---

**Autoria:** Iago Leal — [github.com/iago-leal](https://github.com/iago-leal). Exclusiva, inegociável, inexcluível. Sem coautores.
**Relação com o MDCU Framework:** coirmão estrutural (pai arquitetural: POMR/Weed); aplicação inversa da polaridade método↔especialista (no MECA, o especialista nasce do método).
