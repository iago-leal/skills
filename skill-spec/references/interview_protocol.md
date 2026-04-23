# Protocolo de Entrevista — Modo CRIAR

Adaptação do fluxo de entrevista do `sdd-spec` (6 perguntas) para o contexto específico de skills (7 perguntas). Uma pergunta por turno. Nunca agrupe. Nunca assuma. Se o usuário já respondeu algo no contexto anterior, confirme antes de pular.

---

## Regras do protocolo

1. **Uma pergunta por mensagem.** Espere resposta antes de avançar.
2. **Nunca assuma a resposta.** Se o usuário foi vago, reformule.
3. **Reflita de volta.** Antes de ir para a próxima, resuma em 1 frase o que entendeu e peça confirmação.
4. **Sinalize saltos.** Se o contexto anterior cobriu uma pergunta, diga: "Você já mencionou X — confirma?".
5. **Sem pergunta embutida em proposta.** Não diga "quer que eu faça Y?" antes de ter a resposta da pergunta atual.

---

## As 7 perguntas

### P1 — Propósito (1 frase)

> "Qual é o propósito da skill em uma frase? O que ela faz que hoje é feito de jeito frágil ou manual?"

**O que extrair:**
- Verbo de ação principal (indexar / gerar / extrair / avaliar / anonimizar / ...)
- Objeto da ação (PDFs médicos, specs de feature, commits, ...)
- Valor entregue (reprodutibilidade, velocidade, privacidade, padronização)

**Red flag:** Resposta genérica tipo "automatizar X". Pergunte: "quem é o usuário e qual problema dele essa skill resolve?"

---

### P2 — Triggers (quando ATIVAR e quando NÃO)

> "Quando essa skill deve ser ativada automaticamente? Dê 3 exemplos de mensagens do usuário que devem disparar, e 2 exemplos que NÃO devem disparar (mesmo sendo próximos)."

**O que extrair:**
- Palavras-chave explícitas
- Contextos de ativação
- Delimitação vs skills vizinhas (ex: vs `pdf`, vs `sdd-spec`)
- Comandos `/slash` se aplicável

**Red flag:** Todos os exemplos positivos são paráfrases do nome da skill. Pergunte: "e se o usuário falar do problema sem usar a palavra X?"

---

### P3 — Domínio e público

> "Qual é o domínio (medicina, devops, escrita, ...) e quem é o usuário típico (nível técnico, contexto de uso)?"

**O que extrair:**
- Domínio principal
- Jargão permitido na skill (ex: pode usar "OCR" sem explicar? pode usar "BM25"?)
- Nível de autonomia esperado (interativo vs programático via `--json`)

---

### P4 — Scripts necessários

> "A skill precisa de scripts executáveis? Se sim, liste 1 por script: nome, o que faz em 1 frase, e exemplo de CLI. Se for conversacional (só SKILL.md + referências), diga 'N/A'."

**O que extrair:**
- Lista de scripts (`setup.py`, `ingest.py`, ...)
- CLI proposta de cada um
- Se tem output JSON determinístico
- Se precisa de self-bootstrap (venv próprio)

**Red flag:** "Acho que preciso de um script que..." sem saber exatamente o que. Pergunte: "qual é o comando mais simples que um usuário rodaria? me mostre o argparse."

---

### P5 — Dependências

> "Quais dependências de sistema (ex: tesseract, ollama) e de Python (ex: pymupdf, chromadb) a skill precisa? Versões específicas importam?"

**O que extrair:**
- Lista de pacotes Python com versões (`==X.Y.Z` ou `latest` justificado)
- Binários de sistema + comando de instalação
- Se o usuário quer ser conservador (pinar tudo) ou permissivo

**Red flag:** "Qualquer versão serve." Explique: determinismo exige pinagem. Ofereça pinar na versão corrente como default.

---

### P6 — Privacidade e ambiente de execução

> "A skill deve rodar 100% local, chamar APIs externas, ou híbrido? Há dados sensíveis envolvidos?"

**O que extrair:**
- Local / cloud / híbrido
- Dados sensíveis (PII, PHI, segredos)
- Ambiente-alvo (macOS / Linux / Windows / todos)
- Restrições de rede

**Red flag:** Dados sensíveis mencionados mas sem plano de anonimização. Cite a skill `data-anonymizer` como delegação.

---

### P7 — O que a skill NÃO faz

> "Cite 3 coisas que essa skill NÃO faz, especialmente tarefas próximas que pertencem a outras skills ou que estão fora de escopo. Ex: 'NÃO gera respostas com LLM — apenas recupera'."

**O que extrair:**
- Delimitação vs skills vizinhas (com nome da skill a delegar)
- Funcionalidades explicitamente adiadas
- Responsabilidades que parecem caber mas não cabem

**Red flag:** Genéricos como "NÃO faz mágica". Recuse. Peça 3 itens específicos e acionáveis.

---

## Saída da entrevista

Ao final das 7 perguntas, produza um **resumo estruturado** (sem ainda preencher o template) e confirme com o usuário:

```
Entrevista concluída. Resumo:

1. Propósito: <1 frase>
2. Triggers (+): <3 exemplos>
   Triggers (−): <2 exemplos>
3. Domínio: <domínio> — usuário: <perfil>
4. Scripts: <lista ou N/A>
5. Deps: <python + sistema>
6. Privacidade: <local/cloud/híbrido>
7. NÃO faz: <3 itens>

Confirma antes de eu preencher a SPEC? (s/n)
```

Só depois do `s` explícito, avance para preencher `spec_template.md`.

---

## Quando pular a entrevista

Se o usuário disser "tenho SPEC em draft, só completa os buracos" ou "já escrevi as respostas, processa":

- Leia o que ele forneceu
- Identifique quais das 7 perguntas ficaram em aberto
- Entreviste **só as abertas**, uma de cada vez

Nunca preencha buracos sozinho com inferências silenciosas.
