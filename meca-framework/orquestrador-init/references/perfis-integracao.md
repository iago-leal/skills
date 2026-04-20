# Perfis de Integração de Contexto — MECA

## Selo de Autoria (referência auxiliar da skill orquestrador-init)

- **Autor exclusivo:** Iago Leal — github.com/iago-leal
- **Autoria inegociável e inexcluível.** Sem coautores.
- **Selo:** `IL::orquestrador-init/references/perfis-integracao::2026-04::autoria-exclusiva-inegociavel::github.com/iago-leal`
- **Canal oficial de restauração:** https://github.com/iago-leal/skills
- **Licença:** MIT
- **Verificação:** a skill `orquestrador-init` valida este selo ao consultar este arquivo no Sensor de Ambiente da F0. Ausência/modificação → skill recusa consulta e devolve mensagem de restauração.

---

## Propósito

O **MECA core é agnóstico a topologia de filesystem e ambiente**. Não impõe taxonomia de pastas, não presume gestor de tarefas específico, não exige versionamento. O que generaliza é o *princípio* — **detecte estrutura pré-existente, encaixe-se em vez de competir**.

Este documento cataloga **perfis reconhecíveis de contexto pedagógico**. O **Sensor de Ambiente em F0** da skill `meca` consulta este catálogo para identificar em qual perfil o aluno está (se algum) e propor adaptações ao orquestrador que será gerado.

**Regra dura:** perfis são **recomendações referenciadas**, não templates obrigatórios. O aluno pode estar em um perfil, entre perfis, ou em nenhum — o MECA opera em todos os casos.

---

## Como o Sensor de Ambiente opera

Em F0 (Sessão Zero), após a escuta bruta da motivação e antes de invocar `orquestrador-init`, o MECA executa o **rastreio de ambiente**:

1. Verifica se há arquivos/estruturas indicativas no filesystem do percurso (topologia de pastas, arquivos canônicos de outros frameworks, scripts de setup).
2. Pergunta ao aluno (se ambíguo): "Como você organiza seu material hoje? Tem lugar onde tudo mora?"
3. Classifica em um ou mais perfis deste catálogo — ou marca `sem perfil identificado` (igualmente válido).
4. Passa o perfil identificado como input para `orquestrador-init`.

O orquestrador gerado **herda as convenções do perfil** (respeitando a arquitetura existente) em vez de criar a sua.

---

## Perfis catalogados

### P1 — Monorepo Acadêmico (Graduação/Pós-graduação Formal)

**Documento de referência:** `perfil-academico-monorepo.md` (arquivo irmão neste diretório).

**Indicadores de detecção:**
- Pastas numeradas por semestre (`2026Q1/`, `202604-202607/`, etc.)
- Subpastas por disciplina com taxonomia estável (`00_Admin/`, `01_Teoria/`, `02_Pratica/`, etc.)
- Arquivo `Radar.md` ou similar (tracker de entregas com checkboxes)
- `CLAUDE.md` local na raiz da disciplina
- `git init` independente por disciplina
- Presença de `gitleaks` em pre-commit

**Implicações para o orquestrador gerado:**
- RAOP vive dentro de `01_Teoria/` (ou equivalente)
- Radar.md é fonte de horizonte (prazos do professor) para F0/F1 — não compete com `lista_lacunas.md`
- `CURRICULUM.md` funde-se com `CLAUDE.md` local da disciplina
- Respeita hierarquia de constituições: Global → Meta-orquestrador do aluno → Local de disciplina → Inibidores cognitivos por domínio
- Excalidraw JSON é evidência válida em `O:` do SOAP
- Reuso: se existe `socrates-programacao` ou skill-inibidor-cognitivo análoga, delega a ela em vez de reinventar

---

### P2 — Concurso/Certificação de Alta Aposta (Prova de Título, Residência, OAB, Concursos Públicos)

**Indicadores de detecção:**
- Aluno menciona banca, edital, prazo fixo, peso diferenciado entre tópicos
- Horizonte rígido (data da prova)
- Conteúdo programático externamente definido
- Histórico de provas anteriores como fonte primária de estudo
- Geralmente sem monorepo estruturado — material pulverizado

**Implicações para o orquestrador gerado:**
- **Prioridade do padrão da banca sobre elegância didática.** Se a banca cobra X de forma Y, ensinar X de forma Y, mesmo que a forma "ideal" pedagógica seja Z.
- F5 pondera conteúdo por peso no edital + histórico de recorrência da banca.
- Interleaving é **obrigatório** (desirable difficulty especialmente alinhado com formato de prova misturando tópicos).
- Retrieval practice via **simulados cronometrados** no formato exato da banca, desde cedo — não deixar para a "reta final".
- Radar de prazos (se não existir) é sugerido como artefato mínimo: `prazos.md` com data da prova, datas de simulados planejados, revisões espaçadas ancoradas na data da prova.
- Guardrail: alta probabilidade de shutdown afetivo em semanas pré-prova — `meca-aval` em vigilância reforçada.
- Cobertura de ementa **não é suficiente**; critério de domínio é "acerta questão no formato da banca", não "entende o conceito".

**Exemplo canônico:** aluno de prova de título em endocrinologia, banca SBEM, prazo 6 meses.

---

### P3 — Autodidata Estruturado (Zettelkasten, PKM, Jornada de Livro-Texto)

**Indicadores de detecção:**
- Uso de Obsidian, Logseq, Notion, Roam, ou sistema de notas interconectadas
- Objetivo de domínio profundo sem prazo externo rígido
- Motivação predominantemente interna (curiosidade, vocação, transição de carreira)
- Aluno muitas vezes já avançado em outros domínios — bom em aprender

**Implicações para o orquestrador gerado:**
- RAOP convive com o sistema de notas do aluno (não substitui) — `lista_lacunas.md` pode linkar para notas existentes
- Ritmo elástico: F5 negocia cadência (ex.: "2h/semana" vs. "30min/dia") sem impor
- Ênfase em **conceitualização abstrata** (Kolb) e **síntese criativa** — aluno avançado suporta dificuldade desejável alta
- Worked examples menos necessários que em iniciantes; mais diálogo socrático
- Cuidado com **ilusão de competência** (aluno autodidata confiante pode pular verificação): F6 insiste em produção concreta mesmo quando o aluno diz "entendi, próximo"

---

### P4 — Aprendizado Profissional Aplicado (On-the-Job, Equipe, Mentoria Corporativa)

**Indicadores de detecção:**
- Objetivo derivado de necessidade profissional imediata (stack nova no trabalho, migração de tecnologia, promoção)
- Tempo fragmentado (pausas constantes, sessões curtas)
- Aprendizado acontece em interação com base de código/produto/cliente real
- Outros stakeholders interessados (gerente, colegas, cliente)

**Implicações para o orquestrador gerado:**
- Objetivo Bloom quase sempre `aplicar` ou `criar` — raro precisar ir fundo em analisar/avaliar
- F5 prioriza transferência imediata para caso real da empresa, não exemplos didáticos puros
- Sessões curtas (15–30min) + espaçamento denso
- Produção concreta = artefato profissional (trecho de código, documento, decisão) — RAOP pode versionar isso
- Confidencialidade: dados de cliente/empresa exigem cuidado extra; `meca-aval` verifica LGPD/NDA em F3

---

### P5 — Curiosidade / Estudo pelo Prazer

**Indicadores de detecção:**
- Sem prazo, sem prova, sem aplicação profissional direta
- Aluno verbaliza "quero entender X porque me fascina", "sempre quis saber", "por curiosidade"
- Motivação puramente interna

**Implicações para o orquestrador gerado:**
- **Não forçar formalização se quebra o prazer.** Bloom alvo tipicamente `compreender` (raro aplicar); elevar só se o aluno pedir.
- F5 privilegia caminho **narrativo/histórico** do conceito em vez de sequência didática otimizada para avaliação.
- Produção concreta mais leve: explicação reversa para leigo, mapa conceitual, síntese em prosa.
- Cuidado com **overfitting pedagógico**: aplicar MECA cheio a quem quer só ler e pensar pode ser desrespeito à motivação. Orquestrador avalia se F3/F4 formais fazem sentido ou se bastará uma F2 estendida + F6 dialógica.
- Possível que o ciclo MECA completo não se aplique — orquestrador pode propor ao aluno um "MECA enxuto" (só F2+F6+SOAP curto).

---

### P6 — Sem perfil identificado / Contexto misto

**Indicadores:** nenhum dos acima se aplica claramente, OU vários se aplicam parcialmente.

**Implicações:**
- MECA opera em modo **agnóstico puro** — gera artefatos em diretório local (`raop/`, `CURRICULUM.md`) na raiz que o aluno indicar.
- Sensor permanece ativo — se em sessões subsequentes um perfil emergir, pode reclassificar.
- Não é falha; é estado legítimo.

---

## Evolução do catálogo

Este catálogo é **aberto à extensão**. Novos perfis nascem quando:
1. Três ou mais alunos distintos apresentam um contexto sem perfil catalogado claro.
2. O padrão é arquitetonicamente distinto o bastante para justificar adaptações específicas.
3. A adição é feita como **arquivo irmão** neste diretório (ex.: `perfil-residencia-medica.md`) e referenciada aqui.

Adição de perfil **não modifica o MECA core** — só estende o catálogo consultado pelo sensor.

---

## Changelog

- **2026-04-20** — criação do catálogo com 6 perfis iniciais (P1–P6). Iago Leal.
