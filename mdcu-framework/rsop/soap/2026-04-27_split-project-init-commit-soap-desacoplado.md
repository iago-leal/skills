# SOAP 2026-04-27 — split project-init + commit-soap desacoplado
- Problemas: #9, #11

## S
**Demandas**
- reformular project-init para parar de violar P-8 (resolver #9)
- desacoplar commit-soap da sessão MDCU (encadeamento revelado em F5)

**Queixas**
- project-init executa npm/poetry/cargo/git diretamente — mesma patologia de F6 antes da reformulação
- commit-soap acoplado a "sessão MDCU" deixa setup inicial sem selo longitudinal coerente (viola P-9)

**Notas**
- Stakeholder explicitou critério mestre: *"escolha a que for melhor pensando na longevidade, saúde e manutenção do framework. nao quero dividas tecnicas futuras que podem ser resolvidas agora, mesmo que dê muito trabalho"*
- Sob esse critério, alternativas A (cirúrgico — sub-blocos) e C (só nota) descartadas — preservam dívida estrutural
- Alternativa B (split em duas skills) escolhida por cumprir P-7 e P-8 estruturalmente, não declarativamente
- Sub-decisão (ii) — commit inicial via commit-soap desacoplado — entail resolver #11 na mesma sessão
- F2 dispensada novamente pelo coautor ("sigamos") — padrão estabelecido nas duas sessões anteriores
- Auto mode ativo durante toda a execução

## O
- project-init decomposto em 7 fases; **só fase 7 viola P-8** (npm/poetry/cargo init, install, git init, git commit) — fases 1-6 são interface humana de extração de contrato
- Seção "Gestão Determinística de Dependências" do project-init é **prescrição canônica**, não execução — preservada integralmente como vinculante em ambos os modos (desacoplado e monolítico)
- commit-soap v1.x: "Uso EXCLUSIVO para fechamento de sessão MDCU" — bloqueia uso para selar setup inicial coerentemente
- 6 artefatos atualizados nesta sessão: project-init/SKILL.md (refatorado para interface only), project-setup/SKILL.md (novo), commit-soap/SKILL.md (v2.0.0 desacoplado), MANIFEST.md (project-setup adicionado, bumps), framework/architecture-diagram.md (#9 e #11 marcados resolvidos), mdcu/SKILL.md (workflow + dependências + gatilho de conformidade dual)
- Versionamento semver: project-init 1.0.0→2.0.0 (MAJOR — quebra contrato), commit-soap 1.x→2.0.0 (MAJOR — escopo expandido), project-setup 0.1.0 (NOVA, pré-1.0)
- Bundle marker: v2026.05 (planejada) — agora com 6 skills ao invés de 5
- Gatilho de conformidade da F1 do MDCU agora dual: ARCHITECTURE.md presente E setup materializado (verificável via /project-setup --check)

## A
1. #9 split project-init + project-setup
2. #11 commit-soap v2.0.0 desacoplado universal

## P
1. #9 project-init refatorado para interface only (1.0.0→2.0.0); project-setup nova (0.1.0) materializa contrato em modo desacoplado/monolítico declarado; gestão determinística de dependências preservada como prescrição canônica vinculante em ambos os modos
2. #11 commit-soap v2.0.0 aceita SOAP default + --from <path> + --inline; project-setup invoca --inline para selo inicial; descrição em SKILL.md documenta marcos cobertos (sessão MDCU, project-setup, refresh, release); RN-D-012 do _reversa_sdd permanece descrevendo comportamento antigo (regenerável)

## R
- Stakeholder elevou diretriz mestra (longevidade > esforço) — fez B + (ii) virar única escolha coerente; padrão a memorizar para sessões futuras com decisões estruturais
