# SOAP 2026-04-27 — schema enrichment lista_problemas (Tipo + Revisitar)
- Problemas: #3, #10

## S
**Demandas**
- estender schema lista_problemas.md para distinguir dívida consciente × acidental (#3)
- codificar eixo precisa-resolver × não-precisa-resolver no schema (#10)

**Queixas**
- schema atual minimalista (`# | Problema | Desde | Últ. SOAP`) — sem distinção entre tipos, sem prazo de revisitar, sem registro de queixa-triada-aceita
- dívida consciente vira indistinguível de bug esquecido em 3 meses sem codificação estrutural

**Notas**
- Diretriz mestra do stakeholder (longevidade > esforço, sem dívida resolvível agora) confirmada como critério para escolha entre alternativas
- F2 dispensada pelo coautor ("siga"); padrão estabelecido em três sessões consecutivas
- Tensão real entre P-5 (disciplina telegráfica) e diretriz mestra; resolvida observando que P-5 é contra prosa redundante, não contra estrutura

## O
- Schema atual de ATIVOS em rsop/SKILL.md:94: `# | Problema | Desde | Últ. SOAP` com nota explícita "Sem coluna 'Notas'. Evolução mora no SOAP referenciado"
- Schema atual de PASSIVOS: `# | Problema | Ativo em | Fechado por | Fechado em | Reativável?` (não tocado nesta sessão)
- 5 opções de codificação examinadas em F3; opção 5 (colunas Tipo + Revisitar com defaults implícitos, Status redundante) escolhida
- RN-D-015 já antecipava prefixo `[aceito-arquivado]` na coluna `#` — mantido como mecanismo canônico (sem coluna Status separada, redundante numa lista de ativos)
- 5 artefatos atualizados: rsop/SKILL.md (v1.3.0 — schema + regras + Triagem precisa-resolver + Dívida consciente × acidental), rsop/lista_problemas.md (migrado; #2 marcado consciente com Revisitar), framework/glossary.md (RN-D-015 refinada + RN-D-016 nova + termo "Dívida consciente × acidental"), MANIFEST.md (bump rsop 1.3.0 + entry #8)
- 11 # ativos migrados para novo schema; só #2 marcado `consciente` com Revisitar `ao distribuir framework para projeto-cliente externo`
- Token cost estimado: ~30% mais por linha — aceitável dado tamanho típico de lista_problemas em projetos (5-15 itens)

## A
1. #3 schema enriquecido Tipo + Revisitar
2. #10 [aceito-arquivado] como prefixo canônico

## P
1. #3 rsop v1.3.0 com colunas Tipo (consciente|acidental-default) + Revisitar (livre); RN-D-016 obriga preenchimento conjunto para conscientes; defaults implícitos preservam P-5; lista_problemas migrada. Aguarda /rsop revisar
2. #10 prefixo `[aceito-arquivado]` na coluna `#` confirmado como mecanismo canônico (RN-D-015 refinada); coluna Status separada rejeitada por redundância numa lista de ativos. Aguarda /rsop revisar

## R
- Diretriz mestra de longevidade resolveu o aparente conflito P-5 × estruturação — princípio é contra prosa, não contra estrutura semântica
