# `framework/` — artefatos canônicos do mdcu-framework

Esta pasta contém **a fonte de verdade canônica** dos princípios, vocabulário e arquitetura do `mdcu-framework`. É **versionada** e distribuída no repositório público.

## Arquivos

| Arquivo | O que contém |
|---|---|
| `principles.md` | Princípios fundacionais (F-1 a F-5) + princípios arquiteturais canônicos (P-8, P-9). **Fonte de verdade epistemológica e arquitetural.** |
| `architecture-diagram.md` | Diagrama canônico das 4 camadas do framework (interface humana, delegação técnica, acompanhamento longitudinal, fundação). |
| `glossary.md` | Termos canônicos do framework (Satisfação clínica, Decisão informada, Composição do orquestrador, Anamnese, Engine downstream desacoplável, Precisa-resolver) + regras de negócio canônicas (RN-D-014, RN-D-015). |

## Relação com `_reversa_sdd/`

`_reversa_sdd/` é **saída da skill Reversa** rodada sobre o próprio repositório do framework — análise estática que produz princípios técnicos (P-1 a P-7), glossário extraído, regras de negócio implícitas, ADRs retroativos e diagramas C4.

- `_reversa_sdd/` é **gitignored** (regenerável a cada execução do Reversa)
- `framework/` é **versionado** (canônico, distribuído)

**Em caso de tensão entre os dois:** `framework/` prevalece. Reversa é insumo de análise; canônico é decisão de design.

**Conteúdo que vive em ambos:**

| Concept | Em `_reversa_sdd/` | Em `framework/` |
|---|---|---|
| Princípios técnicos P-1 a P-7 | `architecture.md` (Reversa output) | (não duplicado — referenciados de lá) |
| Princípios arquiteturais canônicos P-8, P-9 | (referência cruzada apenas) | `principles.md` |
| Princípios fundacionais F-1 a F-5 | (referência cruzada apenas) | `principles.md` |
| Termos centrais MCCP (Demanda, Queixa, SIFE, etc.) | `domain.md` (Reversa output) | (não duplicado — referenciados de lá) |
| Termos canônicos do framework (Satisfação, etc.) | (referência cruzada apenas) | `glossary.md` |
| RN-D-001 a RN-D-013 | `domain.md` (Reversa output) | (não duplicado — referenciados de lá) |
| RN-D-014, RN-D-015 (canônicas) | (referência cruzada apenas) | `glossary.md` |
| Diagrama arquitetural | (não tem) | `architecture-diagram.md` |

## Quando consultar

- **Antes de propor mudança ao framework:** ler `principles.md` para checar critério de coerência (a proposta aumenta capacidade de extração via MCCP, qualidade da tradução, ou probabilidade de satisfação? Ou viola alguma das 5 teses fundacionais / 2 princípios arquiteturais canônicos?)
- **Ao escrever artefato novo (skill, regra, schema):** verificar se vocabulário usado já está em `glossary.md`. Termo novo? Justificar inclusão no glossary.
- **Ao revisar arquitetura visual ou documentação:** `architecture-diagram.md` é fonte canônica. `framework-diagrama.html` na raiz do repo é editorial (público), pode divergir; se houver tensão, este arquivo prevalece.
