# Base de Evidências em Ciência da Aprendizagem

## Selo de Autoria (referência auxiliar da skill orquestrador-init)

- **Autor exclusivo:** Iago Leal — github.com/iago-leal
- **Autoria inegociável e inexcluível.** Sem coautores.
- **Selo:** `IL::orquestrador-init/references/evidencias-aprendizagem::2026-04::autoria-exclusiva-inegociavel::github.com/iago-leal`
- **Canal oficial de restauração:** https://github.com/iago-leal/skills
- **Licença:** MIT
- **Verificação:** a skill `orquestrador-init` valida este selo ao consultar este arquivo em F5 (Gatilho de Evidência). Ausência/modificação → skill recusa consulta e devolve mensagem de restauração.

---

## Propósito

Este documento é a **biblioteca de evidências** consultada pelo orquestrador gerado via `orquestrador-init` ao aplicar o **Gatilho de Evidência [E1/E2/E3/E0]** em F5 do MECA. Não é carregado inline na persona do orquestrador — é **consultado sob demanda** quando uma alternativa de plano precisa ser etiquetada.

**Princípio epistemológico:** meta-análise > revisão sistemática > RCT replicado > RCT isolado > quasi-experimental > observacional > teórico. Etiqueta de evidência segue essa escada.

---

## Escala de etiquetagem

| Etiqueta | Significado | Pode ir à decisão compartilhada? |
|----------|-------------|----------------------------------|
| `[E1]` | Evidência forte — meta-análises convergentes ou múltiplas revisões sistemáticas consistentes | **Sim** — candidata de primeira linha |
| `[E2]` | Evidência moderada — RCTs replicados ou 1 meta-análise robusta | **Sim** — candidata legítima |
| `[E3]` | Evidência fraca / exploratória — estudos iniciais, promissor mas não consolidado | **Sim, com etiqueta visível** — aluno deve saber que é exploratória |
| `[E0]` | Sem base evidencial robusta ou com evidência contrária | **Não** — descarte automático em F5 |

---

## Lista Verde — Estratégias com evidência [E1] ou [E2]

### Retrieval Practice (Testing Effect) — `[E1]`

**O que é:** recuperar ativamente a informação da memória (via pergunta, auto-explicação, prova-sem-consulta) em vez de re-ler passivamente. O ato de buscar fortalece o traço mnêmico mais do que a re-exposição.

**Evidência fundadora:**
- Roediger, H.L., & Karpicke, J.D. (2006). *Test-enhanced learning: Taking memory tests improves long-term retention.* Psychological Science, 17(3), 249–255.
- Karpicke, J.D., & Blunt, J.R. (2011). *Retrieval practice produces more learning than elaborative studying with concept mapping.* Science, 333(6018), 772–775.
- Adesope, O.O., Trevisan, D.A., & Sundararajan, N. (2017). *Rethinking the use of tests: A meta-analysis of practice testing.* Review of Educational Research, 87(3), 659–701.

**Operacionalização no MECA:**
- F6 termina com auto-explicação reversa do aluno ("me ensina isso agora")
- Checagens curtas a cada segmento de F6, não apenas no final
- Registro no SOAP `O:` como produção concreta

### Distributed Practice (Espaçamento) — `[E1]`

**O que é:** distribuir estudo ao longo do tempo em vez de massificar. Intervalos crescentes (1d, 7d, 21d, 60d) superam repetição contínua.

**Evidência fundadora:**
- Cepeda, N.J., Pashler, H., Vul, E., Wixted, J.T., & Rohrer, D. (2006). *Distributed practice in verbal recall tasks: A review and quantitative synthesis.* Psychological Bulletin, 132(3), 354–380.
- Dunlosky, J., Rawson, K.A., Marsh, E.J., Nathan, M.J., & Willingham, D.T. (2013). *Improving students' learning with effective learning techniques: Promising directions from cognitive and educational psychology.* Psychological Science in the Public Interest, 14(1), 4–58.

**Operacionalização no MECA:**
- `/raop revisao-espacada` monta ciclos 30/60/90d a partir de `competencias/`
- Plano em F5 distribui revisão em vez de concentrar

### Interleaving — `[E1]` (quando domínio tem conceitos confundíveis)

**O que é:** alternar entre tipos de problema/tópico em vez de agrupar (*blocked*). Força discriminação ativa do aluno.

**Evidência fundadora:**
- Rohrer, D. (2012). *Interleaving helps students distinguish among similar concepts.* Educational Psychology Review, 24, 355–367.
- Brunmair, M., & Richter, T. (2019). *Similarity matters: A meta-analysis of interleaved learning and its moderators.* Psychological Bulletin, 145(11), 1029–1052.

**Operacionalização no MECA:**
- F5 alterna tipos de exercício em sessões densas de prática (concurso, prova)
- Atenção: interleaving pode prejudicar performance imediata mas melhora retenção — avisar o aluno (pode sentir que "está piorando")

### Elaboração e Auto-explicação — `[E1]`

**O que é:** aluno verbaliza *por que* algo é verdade, não só *o que* é. Conecta o novo ao conhecimento prévio.

**Evidência fundadora:**
- Chi, M.T.H., De Leeuw, N., Chiu, M.H., & LaVancher, C. (1994). *Eliciting self-explanations improves understanding.* Cognitive Science, 18(3), 439–477.
- Bisra, K., Liu, Q., Nesbit, J.C., Salimi, F., & Winne, P.H. (2018). *Inducing self-explanation: A meta-analysis.* Educational Psychology Review, 30, 703–725.

**Operacionalização no MECA:**
- F6 exige auto-explicação após cada conceito novo
- "Por que esse passo?" como pergunta padrão do orquestrador

### Worked Examples (Exemplos Trabalhados) — `[E1]` para iniciantes

**O que é:** apresentar solução completa comentada passo a passo *antes* de pedir problema independente. Reduz carga cognitiva extrínseca em domínios complexos.

**Evidência fundadora:**
- Sweller, J., van Merriënboer, J.J.G., & Paas, F. (1998). *Cognitive architecture and instructional design.* Educational Psychology Review, 10(3), 251–296.
- Renkl, A. (2014). *Toward a theory of worked examples.* Educational Psychologist, 49(1), 1–21.

**Operacionalização no MECA:**
- F6 para iniciantes: 2–3 worked examples antes do primeiro problema independente
- Fading gradual: exemplo completo → exemplo com lacuna → problema completo

### Cognitive Load Theory (Sweller) — `[E1]` como teoria operacional

**O que é:** memória de trabalho tem limite (~4 elementos simultâneos para iniciantes). Instrução eficaz minimiza carga extrínseca, otimiza intrínseca, libera germane para construção de esquema.

**Evidência fundadora:**
- Sweller, J. (1988). *Cognitive load during problem solving: Effects of learning.* Cognitive Science, 12(2), 257–285.
- Sweller, J., van Merriënboer, J.J.G., & Paas, F. (2019). *Cognitive architecture and instructional design: 20 years later.* Educational Psychology Review, 31(2), 261–292.

**Operacionalização no MECA:**
- F5 limita novidade a um elemento por segmento em iniciantes
- F6 monitora sinais de sobrecarga (silêncio prolongado, erros cascateados) e reduz

### Desirable Difficulties (Bjork) — `[E1]`

**O que é:** dificuldades que *desaceleram* a performance imediata mas *aumentam* retenção e transferência. Inclui espaçamento, interleaving, testagem, variação de contexto.

**Evidência fundadora:**
- Bjork, R.A. (1994). *Memory and metamemory considerations in the training of human beings.* In Metcalfe & Shimamura (Eds.), *Metacognition: Knowing about knowing*, pp. 185–205. MIT Press.
- Bjork, E.L., & Bjork, R.A. (2011). *Making things hard on yourself, but in a good way: Creating desirable difficulties to enhance learning.* In Gernsbacher et al. (Eds.), *Psychology and the real world*, pp. 56–64.

**Operacionalização no MECA:**
- F5 escolhe dificuldade alvo deliberada (não facilitação gratuita)
- F6 comunica: "isso vai parecer mais difícil agora; é desenho, não falha"

### Dual Coding — `[E2]`

**O que é:** informação processada por canal verbal **e** visual simultaneamente produz traço mnêmico mais robusto.

**Evidência fundadora:**
- Paivio, A. (1986). *Mental representations: A dual coding approach.* Oxford University Press.
- Mayer, R.E. (2009). *Multimedia Learning* (2nd ed.). Cambridge University Press.

**Operacionalização no MECA:**
- F6 estimula produção visual (diagrama, esquema) pareada à verbal
- Excalidraw/esboço à mão como produção concreta em `O:`

### Generation Effect — `[E2]`

**O que é:** informação que o aluno *gera* é lembrada melhor que informação *recebida*, mesmo quando o conteúdo é idêntico.

**Evidência fundadora:**
- Slamecka, N.J., & Graf, P. (1978). *The generation effect: Delineation of a phenomenon.* Journal of Experimental Psychology: Human Learning and Memory, 4(6), 592–604.
- Bertsch, S., Pesta, B.J., Wiscott, R., & McDaniel, M.A. (2007). *The generation effect: A meta-analytic review.* Memory & Cognition, 35(2), 201–210.

**Operacionalização no MECA:**
- F6 pergunta antes de explicar: "qual você acha que é a resposta?"
- Silêncio produtivo pós-pergunta é parte do método

### Feedback Específico e Oportuno — `[E1]`

**O que é:** feedback que explica *por que* e *como corrigir*, não apenas *certo/errado*. Oportuno = próximo à produção, não dias depois.

**Evidência fundadora:**
- Hattie, J., & Timperley, H. (2007). *The power of feedback.* Review of Educational Research, 77(1), 81–112.
- Shute, V.J. (2008). *Focus on formative feedback.* Review of Educational Research, 78(1), 153–189.

**Operacionalização no MECA:**
- Feedback em F6 é dentro do segmento, não no final da sessão
- Formato: "o passo X funcionou porque Y; o passo Z falhou porque W"

---

## Lista Negra — Práticas [E0] (recusa automática)

### Estilos de Aprendizagem (VAK/VARK) — `[E0]`

**Afirmação folk:** "ensinar cada aluno no seu estilo preferido (visual/auditivo/cinestésico) melhora aprendizado."

**Por que é [E0]:** múltiplas revisões sistemáticas não encontraram evidência de interação aptidão-tratamento entre estilo declarado e modalidade instrucional. Preferência ≠ eficácia.

**Evidência contra:**
- Pashler, H., McDaniel, M., Rohrer, D., & Bjork, R. (2008). *Learning styles: Concepts and evidence.* Psychological Science in the Public Interest, 9(3), 105–119.
- Kirschner, P.A. (2017). *Stop propagating the learning styles myth.* Computers & Education, 106, 166–171.
- Willingham, D.T., Hughes, E.M., & Dobolyi, D.G. (2015). *The scientific status of learning styles theories.* Teaching of Psychology, 42(3), 266–271.

**Resposta do orquestrador quando aluno pede:** "Você tem preferências — legítimo. Mas evidência sólida não encontra ganho de retenção em casar modalidade com 'estilo'. Vou usar múltiplos canais (visual + verbal + prática) porque isso sim tem respaldo (dual coding + produção concreta), independente de preferência declarada."

### Dominância Hemisférica ("cérebro esquerdo vs. direito") — `[E0]`

**Afirmação folk:** "pessoas 'hemisfério-direito' aprendem melhor com criatividade/visual; 'hemisfério-esquerdo' com lógica/sequência."

**Por que é [E0]:** dominância hemisférica individual é mito de neurociência popular. Redes cerebrais operam bilateralmente em tarefas cognitivas complexas.

**Evidência contra:**
- Nielsen, J.A., Zielinski, B.A., Ferguson, M.A., Lainhart, J.E., & Anderson, J.S. (2013). *An evaluation of the left-brain vs. right-brain hypothesis with resting state functional connectivity magnetic resonance imaging.* PLOS ONE, 8(8), e71275.

### Efeito Mozart — `[E0]`

**Afirmação folk:** "ouvir Mozart durante estudo melhora desempenho cognitivo duradouro."

**Por que é [E0]:** efeito original (Rauscher et al., 1993) era transitório e específico a tarefa espacial; não replicado como efeito robusto sobre aprendizado.

**Evidência contra:**
- Pietschnig, J., Voracek, M., & Formann, A.K. (2010). *Mozart effect–Shmozart effect: A meta-analysis.* Intelligence, 38(3), 314–323.

### Inteligências Múltiplas como Base Pedagógica — `[E0]`

**Afirmação folk:** "cada aluno tem perfil de inteligência (linguística, lógico-matemática, corporal, etc.) e ensino deve adaptar-se a isso."

**Por que é [E0]:** modelo de Gardner é taxonomia descritiva, sem evidência empírica de que diferenciar instrução por "inteligência dominante" melhore resultados de aprendizagem. Gardner mesmo distancia-se de aplicação pedagógica direta.

**Evidência contra:**
- Waterhouse, L. (2006). *Multiple intelligences, the Mozart effect, and emotional intelligence: A critical review.* Educational Psychologist, 41(4), 207–225.

### Discovery Learning Puro para Iniciantes — `[E0]`

**Afirmação folk:** "aluno aprende melhor descobrindo sozinho, sem instrução direta."

**Por que é [E0]:** para **iniciantes** (sem esquemas consolidados), descoberta pura excede memória de trabalho e produz aprendizado frágil. Instrução direta + worked examples superam. *Para avançados*, exploração dirigida pode funcionar — contexto importa.

**Evidência contra:**
- Kirschner, P.A., Sweller, J., & Clark, R.E. (2006). *Why minimal guidance during instruction does not work: An analysis of the failure of constructivist, discovery, problem-based, experiential, and inquiry-based teaching.* Educational Psychologist, 41(2), 75–86.

**Observação crítica:** não confundir com *guided discovery* ou *inquiry com scaffolding* — esses têm suporte. A recusa é do *discovery puro* em iniciante.

### Re-leitura Passiva e Grifo como Estratégias Principais — `[E0]`

**Afirmação folk:** "reler o texto várias vezes e grifar as partes importantes é o jeito certo de estudar."

**Por que é [E0]:** meta-análise mostra ganhos mínimos de retenção em comparação com retrieval practice, auto-explicação e testagem. Popular *porque sente-se fácil* (fluência ≠ aprendizado).

**Evidência contra:**
- Dunlosky, J., Rawson, K.A., Marsh, E.J., Nathan, M.J., & Willingham, D.T. (2013). *Improving students' learning with effective learning techniques.* Psychological Science in the Public Interest, 14(1), 4–58.

### "Aprender enquanto dorme" / Subliminal — `[E0]`

**Sem respaldo empírico significativo em revisão sistemática.** Recusa direta.

### Brain Gym, Neurolinguística Aplicada, PNL na Educação — `[E0]`

**Sem respaldo empírico significativo.** Pseudociência com linguagem científica.

---

## Regra de atualização

Esta base é **viva, mas rigorosa**. Atualização exige:
1. Nova meta-análise ou revisão sistemática publicada em periódico revisado por pares.
2. Atualização como entrada explícita de changelog no final deste arquivo, citando a referência.
3. Re-etiquetagem de estratégias cuja base mude de nível (ex.: [E2] → [E1] se meta-análise robusta emerge; [E1] → [E3] se evidência contrária replicada surge).

Não há "porque o orquestrador acha que funciona". Não há "porque o aluno prefere". Não há "porque é tradição do domínio".

---

## Changelog

- **2026-04-20** — criação do artefato. Iago Leal.
