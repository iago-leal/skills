# SOAP 2026-04-27 — F6 reformulada
- Problemas: #8

## S
**Demandas**
- reformular F6 do mdcu/SKILL.md para parar de violar P-8/F-1 (resolver #8)

**Queixas**
- F6 atual contém execução técnica direta (micro-commits, lock file, "incrementos pequenos") — confunde escopo MDCU com escopo de engine downstream (queixa herdada do SOAP anterior)

**Notas**
- F2 dispensada pelo coautor — *"sem perguntas abertas agora. vamos reformular. já discutimos bastante"* — S: herdado do SOAP anterior + descrição do #8 (exceção justificada à Regra 1; RN-D-001 + autoridade do coautor)
- Decisão informada (i) modo monolítico = exceção declarada com critério de saída — interpretada da inclinação F5 a partir de "sim" do coautor; vigiar se foi a leitura certa
- Reabertura espontânea de tese central NÃO ocorreu nesta sessão (gatilho conhecido do stakeholder, vigiado em F1)

## O
- F6 atual decomposta em 10 componentes; **3 violam P-8** (execução com skills/MCPs, "incrementos pequenos", micro-commits, lock file rule) — outros 7 são metaprotocolo de observação ou handoff longitudinal (não violam)
- Disjuntor 2/2 + reenquadramento + releitura de _mdcu.md = **metaprotocolo canônico** (P-3 gates não-negociáveis); preservado na reformulação
- Tradução de retorno + handoff para /rsop soap + /commit-soap + delete _mdcu.md = interface humana + camada longitudinal (P-9); preservado
- Lock file rule migrou conceitualmente para #9 (project-init refatorado); F6.a apenas verifica que engine respeitou a regra
- Modo monolítico (orquestrador-instância como engine ad-hoc) nomeado explicitamente em F6.a com critérios de aceitação + critérios de saída
- 5 artefatos atualizados: mdcu/SKILL.md (F6 reescrita; F5 nota refinada), framework/architecture-diagram.md (#8 marcado como resolvido), rsop/lista_problemas.md (#8 evolução)

## A
1. #8 F6 reformulada três sub-blocos

## P
1. #8 F6.a delegação + monolítico declarado, F6.b acompanhamento com Disjuntor 2/2, F6.c tradução + fechamento; lock file rule migrou para #9; aguarda /rsop revisar para ir a passivos

## R
- decisão (i) modo monolítico inferida do "sim" sem confirmação explícita — coautor pode corrigir antes do commit; F2 dispensada por autoridade do coautor (caso particular legítimo, não anti-padrão)
