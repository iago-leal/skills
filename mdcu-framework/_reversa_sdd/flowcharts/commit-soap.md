# Fluxograma — `commit-soap`

## Fluxo de execução

```mermaid
flowchart TD
  Start([/commit-soap]) --> Find[Localizar SOAP mais recente<br/>em rsop/soap/]
  Find --> Exists{SOAP existe?}
  Exists -- Não --> Abort[Mensagem fixa:<br/>'Registre /rsop soap antes —<br/>ou use git commit padrão se WIP'<br/>ABORTA — não inventa mensagem]
  Exists -- Sim --> Extract[Extrair seções A e P]
  Extract --> Multi{SOAP toca<br/>múltiplos #?}
  Multi -- Sim --> FormatMulti[Formato:<br/>A: #N — síntese<br/>A: #M — síntese<br/>P: #N — síntese<br/>P: #M — síntese]
  Multi -- Não --> FormatSingle[Formato:<br/>A: síntese — máx 72 chars 1ª linha<br/>P: síntese]
  FormatMulti --> Refs[Adiciona<br/>Refs: rsop/soap/YYYY-MM-DD_*.md]
  FormatSingle --> Refs
  Refs --> Show[Exibe ao usuário<br/>para revisão]
  Show --> Mode{Modo}
  Mode -- '' --> Confirm{Confirma?}
  Mode -- '--dry-run' --> StopDry[Mostra mas não comita]
  Mode -- '--amend' --> Amend[git commit --amend<br/>com nova mensagem]
  Confirm -- Sim --> Commit[git commit -m mensagem]
  Confirm -- Não --> Cancel[Aborta sem comitar]
```

## Política de uso (gates)

```mermaid
flowchart TD
  Type{Que tipo de<br/>commit?}
  Type -- Fechamento de<br/>sessão MDCU --> CSoap[/commit-soap<br/>SELO LONGITUDINAL]
  Type -- Merge de<br/>feature final --> CSoap
  Type -- WIP / checkpoint --> Std[git commit padrão]
  Type -- Formatação / typo --> Std
  Type -- Bump dependência<br/>rotineiro --> Std
  Type -- Merge intermediário<br/>sem SOAP --> Std

  CSoap --> Search[Visível em<br/>git log --grep='A:']
  Std --> Filter[Visível em<br/>git log --invert-grep --grep='A:']
```

## Comandos de auditoria habilitados

```
git log --grep="A:"             # marcos cognitivos do projeto
git log --grep="P:"             # planos
git log --grep="#3"             # história longitudinal do problema #3
git log --grep="Refs: rsop"     # commits com SOAP atrelado
git log --invert-grep --grep="A:"  # ruído operacional (micro-commits)
```
