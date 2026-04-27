# SOAP 2026-04-27 — tese formalizada, RSOP inaugurado
- Problemas: #1, #2, #3, #4, #5, #6, #7, #8, #9, #10, #11

## S
**Demandas**
- adicionar 6ª skill mdcu-hooks ao framework (pré-decidida em §8 do PLANEJAMENTO)
- promover mdcu para 3.0.0 com Gate F6 (pré-decidida em §8)
- definir schema canônico do distillate + projeções para frameworks downstream
- inaugurar RSOP do mdcu-framework
- promover glossário canônico fora de saída do Reversa

**Queixas**
- spec-kit privilegia spec processada sobre voz crua do stakeholder
- frameworks de spec são trends; MDCU é técnica de comunicação — fricção de envelhecimento se acoplado
- slug livre quebra determinismo de cunhagem entre orquestradores
- problema #1 antigo da lista_problemas era nota livre — sem campo estruturado para dívida consciente
- hooks programáticos viviam em ~/.claude/, não no repo (D-004)
- Reversa é análise + revisão, não suite executável que rode em CI

**Notas**
- Padrão de demanda aparente: exploratória (com elementos de shopping em D1/D2 já decididas)
- Demanda oculta DO1 confirmada+refinada: MDCU é transposição direta MCCP→SE como cobertura de lacuna humana sobre engines técnicos validados — não substituto, complemento
- Demanda oculta DO2 refutada: não há tensão entre uso-cliente vs. dogfooding; coexistência é projetada
- Demanda oculta DO3 recontextualizada: vocabulário público (slug, glossário, schema) não é prematuro — é interface obrigatória para conversar com engines
- SIFE: stakeholder confiante-cauteloso; valoriza fidelidade clínica > conveniência de engenharia
- Calibração in-session: "perfeitamente" do stakeholder referia patobiografia (F3), não hipótese F4 — corrigido antes de avançar para F5
- Tese reframada em F3 turno 2: orquestrador é arquiteto SE sênior + comunicador MCCP + tradutor-artista; humildade técnica é do AUTOR, não do orquestrador
- Tese reframada em F3 turno 3: framework tem 3 dimensões (técnica/intervenção, documentação, humana); parte humana só vivia como evento ou fragmento, não como artefato canônico longitudinal
- Stakeholder compartilhou diagrama em 2 versões; v2 corrigiu seta MCCP→MDCU — virou artefato canônico não previsto inicialmente

## O
- `_reversa_sdd/architecture.md` §5 já negava execução do MDCU mas sem princípio nomeado (P-8/P-9 ausentes antes desta sessão)
- `_reversa_sdd/domain.md` 13 RN-D existentes; 0 codificavam dever de alerta ou triagem precisa-resolver
- `_reversa_sdd/domain.md` 13 termos canônicos MCCP existentes; 0 incluíam satisfação clínica, decisão informada, composição do orquestrador, anamnese
- `mdcu/SKILL.md` Persona genérica ("engenheiro que trata problema técnico como problema humano"); F5 menciona ADR; F6 contém micro-commits, lock file, "incrementos pequenos" — execução técnica direta
- `mdcu/SKILL.md` Princípio central não nomeava satisfação clínica nem dever de alerta
- `project-init/SKILL.md` executa npm/poetry/cargo/git diretamente (tensão estrutural com P-8)
- `commit-soap/SKILL.md` executa git commit; acoplado a sessão MDCU (não cobre marcos longitudinais fora do MDCU — tensão com P-9)
- `rsop/SKILL.md` schema lista_problemas: # | Problema | Desde | Últ. SOAP — sem coluna para precisa-resolver/aceito-arquivado
- Framework não tem `ARCHITECTURE.md` próprio; equivalentes funcionais aceitos por exceção (`_reversa_sdd/architecture.md` + `MANIFEST.md`)
- Framework não tinha RSOP próprio antes desta sessão — primeiro `dados_base.md` + `lista_problemas.md` criados aqui

## A
1. #1 tese formalizada em principles.md
2. #2 ARCHITECTURE.md ausente — exceção justificada
3. #3 schema sem dívida consciente
4. #4 glossário promovido — domain.md ampliado
5. #5 dogfooding estático — falta CI
6. #6 protocolo sign-out indefinido
7. #7 rubrica scorer com teto declarado
8. #8 F6 contém execução técnica
9. #9 project-init executa diretamente
10. #10 eixo precisa-resolver só prosa
11. #11 commit-soap acoplado MDCU

## P
1. principles.md F-1 a F-5 + architecture-diagram.md canônico — resolvido
2. aceitar como dívida consciente; revisitar ao distribuir framework para projeto-cliente externo
3. estender schema lista_problemas com Tipo (consciente/acidental) + Revisitar-quando — sessão futura
4. promover principles.md para fora de _reversa_sdd quando refactorar saída do Reversa — sessão futura
5. desenhar suite executável CI ao planejar release-train v2026.06+
6. documentar protocolo sign-out como seção de RSOP ou skill própria
7. implementar scorer com 5 dimensões + teto art-craft declarado em F-4
8. reformular F6 — substituir execução por delegação a engines + tradução de retorno
9. transformar project-init em orquestrador de setup-engine externo
10. enriquecer schema lista_problemas com coluna Status [aceito-arquivado]
11. desacoplar commit-soap do MDCU — passa a selo de qualquer marco longitudinal

## R
- atalho cognitivo cometido em F4: aprovação ampla onde era específica; corrigido in-session — reforço operacional de RN-D-001
