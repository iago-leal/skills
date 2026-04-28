# SOAP 2026-04-27 — checklist de qualidade do SOAP (rsop v1.4.0)
- Problemas: #7

## S
**Demandas**
- definir rubrica/scorer análogo ao skill-spec para o distillate canônico do MDCU (resolver #7)

**Queixas**
- sem critério de qualidade verificável, orquestradores diferentes produzem outputs de qualidade diferente sem feedback estrutural

**Notas**
- Padrão aparente: n/a — sessão técnica sobre o próprio framework, não escuta de novo problema do stakeholder
- F-4 declarado é constraint forte: scorer mede o necessário, não o suficiente
- Diretriz mestra do stakeholder em vigor (longevidade > esforço)
- Fadiga após 5 sessões consecutivas vigiada como viés (item d em F1)

## O
- Distillate canônico hoje = SOAP (PLANEJAMENTO.md §4.2 distillate paralelo nunca foi materializado; SOAP carrega tudo que distillate precisava carregar)
- Skill-spec usa scorer 0-100 em 5 dimensões com red flags porque skills são comparáveis e reprodutíveis em CI; SOAP não tem essa natureza (per-problem, telegráfico, não-comparativo)
- Análise dos critérios candidatos: 9 de 10 itens são binariamente verificáveis a partir de regras já canônicas (rsop/SKILL.md regras-de-operação + RN-D-002/006/007/015/016 em framework/glossary.md)
- Item subjetivo (10 — anamnese update se padrão novo emergiu) marcado como semi-binário ("presença ou ausência de update" é binário; "padrão novo" é julgamento)
- F-4 expressa naturalmente em checklist binário ("necessário, não suficiente"); scorer numérico induz prosa de justificativa de score (viola P-5)
- 3 artefatos atualizados nesta sessão: rsop/SKILL.md (v1.4.0 — seção "Checklist de qualidade do SOAP" com 10 itens), MANIFEST.md (bump rsop 1.4.0 + entry 9), rsop/lista_problemas.md (#7 evolução)

## A
1. #7 checklist binário 10 itens

## P
1. #7 rsop v1.4.0 com seção "Checklist de qualidade do SOAP"; cap F-4 declarado; auto-aplicado em F6.c do MDCU; não-bloqueante; itens 1-9 são pré-condições objetivas que se falham exigem correção do SOAP antes de selar; item 10 é nota mental subjetiva. Aguarda /rsop revisar

## R
- F-4 + P-5 dissolveram a formulação original ("scorer numérico análogo ao skill-spec") — checklist binário foi a forma certa pra natureza do SOAP

## Auto-aplicação do checklist (este SOAP testa a si mesmo)

- 1. S separa D/Q? **sim**
- 2. Padrão aparente classificado quando aplicável? **n/a** (sessão técnica sobre o próprio framework)
- 3. A ≤5 palavras? **sim** ("checklist binário 10 itens" = 4 palavras)
- 4. P 1:1 com A? **sim** (A1 ↔ P1)
- 5. A referencia # válido? **sim** (#7)
- 6. R 1 linha ou omitido? **sim** (1 linha)
- 7. S e O lidos do _mdcu.md? **sim**
- 8. Dívida consciente introduzida? **n/a** (nenhuma)
- 9. Aceito-arquivado introduzido? **n/a** (nenhuma)
- 10. Anamnese update? **não** — sessão não revelou padrão novo do stakeholder; diretriz mestra já está registrada na anamnese desde sessão anterior
