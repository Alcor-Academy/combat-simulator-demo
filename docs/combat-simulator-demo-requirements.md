# Combat Simulator Demo - Software Crafters Event

## 🎯 Obiettivo della Demo

Dimostrare come Claude Code + framework disciplinato (TDD Outside-In, ATDD, Clean Architecture) produce codice production-ready, non "spaghetti generato da AI".

**Messaggio chiave:** L'AI amplifica le tue pratiche. Se hai disciplina, ottieni codice eccellente. Se no, ottieni spazzatura velocemente.

---

## 📋 Requisiti Funzionali

### Epic: Combat Simulator CLI

Due personaggi si affrontano in combattimento a turni stile D&D semplificato.

---

### Feature 1: Character Creation (15 min)

**User Story:**
> Come giocatore, voglio creare un personaggio con statistiche base, per poter partecipare a un combattimento.

**Acceptance Criteria:**
```gherkin
Given nessun personaggio esiste
When creo un personaggio "Thorin" con 20 HP e 5 Attack
Then il personaggio ha nome "Thorin"
And il personaggio ha 20 HP
And il personaggio ha 5 Attack Power

Given un personaggio con HP
When verifico se è vivo
Then ritorna true se HP > 0
And ritorna false se HP <= 0
```

**Outcome atteso:**
- `Character` value object immutabile
- Factory method o Builder per creazione
- Nessun setter, stato illegale non rappresentabile
- 3-4 test unitari

**Wow moment:** Mostrare come Claude propone un costruttore con validazione, tu guidi verso Value Object immutabile.

---

### Feature 2: Dice Rolling System (10 min)

**User Story:**
> Come sistema di combattimento, ho bisogno di generare numeri casuali per simulare i dadi, mantenendo il sistema testabile.

**Acceptance Criteria:**
```gherkin
Given un dado a 6 facce
When viene lanciato
Then ritorna un valore tra 1 e 6

Given un DiceRoller deterministico (test double)
When è configurato per ritornare 4
Then ritorna sempre 4
```

**Outcome atteso:**
- `DiceRoller` come Port (interfaccia)
- `RandomDiceRoller` adapter per produzione
- `FixedDiceRoller` test double
- Dependency Injection pronta

**Wow moment:** Hexagonal Architecture emerge naturalmente. Il pubblico vede il Port/Adapter pattern applicato a qualcosa di semplice.

---

### Feature 3: Attack Resolution (15 min)

**User Story:**
> Come giocatore, voglio attaccare un nemico e vedere il danno calcolato in base al dado e al mio potere d'attacco.

**Acceptance Criteria:**
```gherkin
Given attaccante con Attack Power 5
And un dado che ritorna 3
When attacco viene risolto
Then il danno totale è 8 (5 + 3)

Given difensore con 20 HP
And danno inflitto di 8
When il danno viene applicato
Then il difensore ha 12 HP rimanenti
```

**Outcome atteso:**
- `AttackResult` value object
- `CombatService` o `AttackResolver` domain service  
- Character ritorna nuova istanza con HP aggiornati (immutabilità)
- 4-5 test unitari

**Wow moment:** Character.receiveDamage() ritorna nuovo Character, non muta. Pubblico vede immutabilità in pratica.

---

### Feature 4: Combat Round (15 min)

**User Story:**
> Come giocatore, voglio eseguire un round di combattimento dove entrambi i personaggi si attaccano, per vedere chi vince.

**Acceptance Criteria:**
```gherkin
Given "Thorin" con 20 HP e 5 Attack
And "Goblin" con 10 HP e 3 Attack
And dadi configurati per [4, 2] (primo attacco, secondo attacco)
When eseguo un combat round
Then Thorin infligge 9 danni (5+4) al Goblin
And Goblin infligge 5 danni (3+2) a Thorin
And Goblin ha 1 HP
And Thorin ha 15 HP

Given un combattente con 0 HP
When è il suo turno di attaccare
Then non può attaccare (è morto)
```

**Outcome atteso:**
- `CombatRound` orchestrator
- Output strutturato del round (non print!)
- `CombatLog` o `RoundResult` per i risultati
- Walking skeleton CLI funzionante

**Wow moment:** Il gioco funziona E2E! La platea vede qualcosa di giocabile nato da TDD rigoroso.

---

### Feature 5: Victory Condition (5 min - buffer/bonus)

**User Story:**
> Come giocatore, voglio sapere quando il combattimento è finito e chi ha vinto.

**Acceptance Criteria:**
```gherkin
Given combattimento in corso
When un personaggio raggiunge 0 HP
Then il combattimento termina
And l'altro personaggio è dichiarato vincitore
```

**Outcome atteso:**
- `CombatResult` con winner
- Game loop completo

---

## ⏱️ Timeline Dettagliata

| Fase | Tempo | Attività | Note per Presenter |
|------|-------|----------|-------------------|
| **Setup** | 0:00-0:03 | Mostra CLAUDE.md, spiega il framework | "Ecco le regole che Claude deve seguire" |
| **Walking Skeleton** | 0:03-0:08 | E2E test che fallisce, struttura base | Primo wow: Claude capisce outside-in |
| **Feature 1** | 0:08-0:23 | Character con TDD | Mostra ciclo red-green-refactor |
| **Feature 2** | 0:23-0:33 | DiceRoller + Port/Adapter | Wow: Hexagonal emerge |
| **Feature 3** | 0:33-0:48 | Attack con immutabilità | Wow: niente mutazioni |
| **Feature 4** | 0:48-0:58 | Combat Round E2E | Grande finale: funziona! |
| **Q&A/Buffer** | 0:58-1:00 | Domande, Victory se c'è tempo | |

---

## 🏗️ Architettura Attesa

```
src/
├── domain/
│   ├── Character.ts          # Value Object
│   ├── AttackResult.ts       # Value Object  
│   ├── CombatRound.ts        # Domain Service
│   └── ports/
│       └── DiceRoller.ts     # Port (interface)
├── infrastructure/
│   └── RandomDiceRoller.ts   # Adapter
├── application/
│   └── CombatSimulator.ts    # Use Case
└── cli/
    └── main.ts               # Entry point

test/
├── domain/
│   ├── Character.test.ts
│   ├── AttackResult.test.ts
│   └── CombatRound.test.ts
├── doubles/
│   └── FixedDiceRoller.ts    # Test Double
└── e2e/
    └── CombatSimulator.test.ts
```

---

## 🎪 Wow Moments da Non Perdere

1. **CLAUDE.md in azione** (0:03)
   - "Guardate, gli dico di fare TDD outside-in e lui parte dal test E2E"

2. **Test Double emerge naturalmente** (0:25)
   - "Non posso testare con dadi random. Claude, come risolviamo?"
   - Claude propone Port/Adapter

3. **Immutabilità forzata** (0:40)
   - "Questo setter non mi piace. Come lo rendiamo immutabile?"
   - Character.receiveDamage() → new Character

4. **Il gioco funziona** (0:55)
   - Run della CLI, combattimento live
   - "50 minuti, TDD rigoroso, e abbiamo un gioco funzionante"

5. **Code coverage e design** (closing)
   - "100% coverage, zero mocking di implementazione, architettura pulita"

---

## 🚨 Rischi e Mitigazioni

| Rischio | Probabilità | Mitigazione |
|---------|-------------|-------------|
| Claude va fuori binari | Media | CLAUDE.md robusto + interrupt manuale |
| Tempo sfora | Media | Feature 5 è buffer sacrificabile |
| Bug inaspettato live | Alta | Abbraccialo! Mostra debugging con AI |
| Pubblico scettico | Media | Enfatizza il processo, non il prodotto |
| WSL crasha | 😅 | Backup locale pronto |

---

## 📝 CLAUDE.md Suggerito per la Demo

```markdown
# Combat Simulator - Demo Rules

## Development Methodology
- ALWAYS use TDD with Outside-In approach
- Write ONE failing test, then minimal code to pass
- Refactor only when tests are green
- No code without a failing test first

## Architecture  
- Hexagonal Architecture: Ports and Adapters
- Domain objects are immutable Value Objects
- No setters, use factory methods or builders
- Make illegal states unrepresentable via types

## Testing
- Test behavior through public API only
- Use test doubles for external dependencies (randomness)
- No mocking of internal implementation
- E2E test as walking skeleton first

## Code Style
- Favor immutability
- Small functions, single responsibility
- No comments that explain "what", only "why" if needed
- Types over runtime checks
```

---

## ✅ Checklist Pre-Demo

- [ ] CLAUDE.md configurato e testato
- [ ] Repository vuoto pronto
- [ ] Claude Code autenticato e funzionante
- [ ] Font size terminale ingrandito per proiezione
- [ ] WSL stabile (🤞)
- [ ] Timer visibile
- [ ] Backup: video pre-registrato delle parti critiche

---

## 🎤 Opening Line Suggerita

> "Oggi non vi mostro quanto è bravo Claude a generare codice. Vi mostro quanto è bravo a seguire le regole. Le MIE regole. Le NOSTRE regole di software crafter."
