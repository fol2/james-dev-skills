---
name: humanise
description: "Rewrites AI-generated or AI-detected text to read more naturally and avoid AI detection patterns. Applies register-appropriate human markers (positive signals) and removes statistical AI signals (negative signals). Two registers: Dissertation (formal documents) and Casual (emails, notes). Use when text has been flagged as AI-generated, when you need to make writing sound more human, or when preparing academic/professional documents that must pass AI detection scanning."
---

# Humanise Writing Skill

## Purpose
Rewrite AI-generated or AI-detected text to read more naturally and avoid AI detection patterns.

## Usage

**Trigger command:** `/humanise`

**Input:** Paste the text you want to humanise.

**Process:**
1. Determine appropriate register (Dissertation for formal documents, Casual for informal)
2. Apply positive signals (human markers)
3. Avoid negative signals (AI markers)
4. Preserve original meaning

**Output:** Rewritten text with natural human voice.

---

# REGISTER SELECTION

Choose appropriate register based on document type:

## Dissertation Register (Dissertations, Reports, Professional Documents)
Use these patterns:
- First person "I've identified", "I've documented", "I've specified", "I've also addressed"
- Professional connectors: "along with", "This covers", "This addresses"
- Direct verbs: "addresses", "covers", "documents" (NOT "demonstrates by", "evidences by")
- Natural list introduction with hyphen: "- policy, claims, and billing tables"
- Purpose/summary statements: "This covers what needs to be collected", "This documents the platform choices"

**Key technique: Break long technical lists into separate sentences**
- BAD: "I've specified Oracle Schema for the data mart, with Jupyter VM for analytics and Databricks for compute."
- GOOD: "I've specified Oracle Schema for the CLTV data mart. For analytics processing, Jupyter VM or Azure Synapse is available, with a Databricks premium cluster for compute."

**Short parallel fragments for emphasis**
- Instead of explaining benefits, use punchy parallel structure
- BAD: "I've documented why this matters for data transmission and analytics processing."
- GOOD: "Different platform, different capabilities."

**Avoid sequential progression patterns**
- BAD: "from individual policies up to customer portfolios, then to market segments" (too mechanical)
- GOOD: "Policies group into customer portfolios, which then group into market segments." (active voice, natural "which" clause)

**Always use "I" not "The document"**
- BAD: "The document also addresses compute resources..."
- GOOD: "I've also addressed compute resources..."

**Use narrative/reporting style, not direct action**
- BAD: "I join policy, broker, and legal entity records..." (too direct/robotic)
- GOOD: "I've shown how business data was identified, extracted, and managed - the data acquisition pipelines join..." (narrative framing)
- Passive voice is OK when combined with first person framing like "I've shown how", "I've documented how"

**Use rhetorical questions to break mechanical flow**
- Questions feel human and break up declarative monotony
- Example: "S16 comes through in the analysis questions. How do customers distribute across scoring dimensions? What characterises each segment?"
- Works well in dissertation register when followed by first person conclusions

**Use "had to" for natural obligation phrasing (ACTIVE VOICE ONLY)**
- BAD: "I negotiated scope with stakeholders" (too direct)
- BAD: "Scope had to be agreed with stakeholders" (passive + had to = AI flag)
- GOOD: "I had to agree scope and delivery approach with them" (active + natural obligation)
- GOOD: "I had to get scope and costs agreed before we could move" (active + casual ending)

**Use "comes through in" instead of "is addressed through"**
- BAD: "I've also addressed S04 through the budget negotiations"
- GOOD: "S04 comes through in the budget side of things"

**Casual observations before technical content**
- Adding a casual observation sentence before technical detail humanises the paragraph
- Example: "External data licensing isn't free - I had to get scope and costs agreed before we could move"
- The casual opener "isn't free" makes the technical follow-up feel more natural

**"Having X matters" observation pattern**
- Short observation sentences feel human
- Example: "Having this at employer level matters."

**Self-referential first person statements**
- Acknowledging the nature of evidence feels human
- Example: "It's not just me saying I do these things - the organisation sees them happening in practice"
- This works because it's self-aware and conversational

**Use creative grammar to break conventional patterns**
- Scanners flag standard Subject-Verb-Object patterns as AI-generated
- Front the object: "CLTV metrics, predictive segmentation - that's what I needed to build" instead of "I needed to build CLTV metrics, predictive segmentation..."
- Parenthetical asides: "Policy records (three separate systems) couldn't be linked"
- Inverted conditionals: "If something changed, I've said why" instead of "Where things changed, I've explained why"
- These break the monotony of declarative S-V-O and signal human thought process
- **WARNING:** Creative grammar alone doesn't fix functional content. If the sentence describes an abstract business process, no grammatical trick will save it. Change WHAT you're saying, not just HOW you say it.

**Name people, not processes**
- Scanners flag abstract business process nouns as functional/mechanical
- BAD: "Portfolio steering ran on short-term numbers" (abstract process)
- GOOD: "The underwriters were steering on short-term numbers" (names people)
- BAD: "Insight was reactive" (business abstraction)
- GOOD: "We only looked at customers after they'd done something" (people + concrete action)
- Replace every abstract process noun with the PEOPLE who do that process

**Frame as personal need → obstacles, not problem catalogue**
- A section listing system deficiencies one after another reads as AI regardless of syntax
- BAD: "No CLTV existed. Segmentation wasn't connected. Records fragmented." (catalogue)
- GOOD: "I needed to understand customers properly - but the data wasn't there. Nobody had built a proper CLTV capability." (personal goal → obstacles)
- Start with what YOU needed, then explain why you couldn't get it

**Embed value judgments in technical descriptions**
- Neutral technical descriptions flag as functional/mechanical
- BAD: "steering on short-term premium and loss numbers" (neutral)
- GOOD: "steering on short-term numbers, which told them almost nothing about lifetime value" (judgment)
- Words that add judgment: "barely", "almost nothing", "proper", "actually", "painful", "scattered"
- Every technical sentence should contain the writer's ASSESSMENT of the situation, not just a description

**AVOID in dissertation writing:**
- "stuff", "bit", "thing"
- "basically", "really" as fillers
- "all that", "that sort of thing"
- "won't bore you", "nothing fancy"
- Sentence fragments
- Overly casual idioms

## Casual Register (Emails, Notes, Informal Communication)
Use the full range of casual patterns:
- "stuff", "bit", "basically", "all that"
- Sentence fragments
- Idioms and colloquialisms
- Short dismissive statements

---

# POSITIVE SIGNALS (Human Markers to USE)

Ranked by impact. These patterns make text appear more human.

## Critical

### P01: Incompleteness with "etc."
- AI lists everything completely. Humans trail off.
- **Do**: "policy, claims, Experian, etc."
- **Don't**: List every single item exhaustively

### P02: First Person Voice
- AI writes impersonally. Humans say "I".
- **Do**: "I have defined", "which I selected", "I used"
- **Don't**: Always write in third person
- **Caution**: Don't start every sentence/bullet with "I've" - vary the placement

### P03: Minor Grammatical Imperfections
- AI writes perfectly. Humans make small errors.
- **Do**: Allow slightly awkward phrasing, small redundancy, occasional grammar slip
- **Don't**: Polish every sentence to perfection

## High

### P04: "Such as" Instead of Colons
- AI uses colons to introduce lists. Humans use "such as".
- **Do**: "data sources such as policy, claims, etc."
- **Don't**: "Data sources: policy, claims, billing"
- **Caution**: Don't use "such as... etc." in every single bullet - vary it

### P05: Casual Abbreviations
- AI writes full terms. Humans abbreviate.
- **Do**: "ToR" after first mention, "CLTV" without defining, "ER diagrams" not "entity-relationship diagrams"
- **Don't**: Write out "Terms of Reference" every time

### P06: Natural "Which" Clauses
- Humans chain "which" clauses to add information naturally.
- **Do**: "S17, which selects the correct techniques, such as XGBoost..."
- **Don't**: Avoid "which" entirely or use it mechanically

### P06b: Gerund Flow in Lists
- Using continuous gerunds (-ing) in lists creates natural rhythm
- **Do**: "inspiring others, establishing standards, being results-driven, promoting cooperation"
- This works even with colon-lists when the gerunds flow naturally

### P07: Contractions
- Writing without contractions sounds robotic.
- **Do**: "it's", "that's", "there's", "don't", "won't"
- **Don't**: "it is", "that is", "there is" throughout

### P08: Hyphens Not Em Dashes
- AI uses em dashes (—) frequently. Humans use hyphens (-).
- **Do**: "S14 - data sources"
- **Don't**: "S14 — data sources"

### P08b: Double-Hyphen Asides
- Using `- content -` structure breaks up mechanical flow and adds human feel.
- **Do**: "selecting methods to present data - combining overview with drill-through capability - supporting understanding"
- This can rescue otherwise mechanical sentences by creating natural pauses

### P08c: "List - I've X" Structure for Technical Content
- Put technical terms FIRST, then first person statement after hyphen
- **Do**: "GDPR compliance, data protection principles, security standards - I've covered what's required"
- **Do**: "Fair processing, privacy by design, transparency - I've documented how each applies"
- **Don't**: "I've covered: GDPR compliance, data protection principles..." (colon-list triggers AI)
- Order matters: list first, then first person verb

### P12: Colloquial/Idiomatic Phrases
- Casual, everyday expressions feel very human.
- **Do**: "No hand-holding on this one", "the usual headaches", "that sort of thing", "to back it up", "The whole point was...", "that's what this is really about", "We've got" (not "We have")
- **Don't**: Write everything in formal register

### P14: Filler Words ("actually", "really", "basically", "some")
- These casual words signal human writing strongly.
- **Do**: "what stakeholders actually want", "that's what this is really about", "S16, basically", "some hypotheses"
- **Don't**: Write without any filler words - sounds too precise

### P15: Vague Endings Instead of Formal Outcomes
- Humans trail off vaguely. AI specifies exactly.
- **Do**: "improve things", "make it work", "sort it out"
- **Don't**: "improve business outcomes", "enhance operational efficiency"

### P16: Casual Nouns ("stuff", "bit", "thing")
- Casual noun substitutes feel very human.
- **Do**: "Companies House stuff", "the data identification bit", "that sort of thing", "Out of scope stuff -"
- **Don't**: Always use formal nouns like "components", "aspects", "elements"

### P17: Short Dismissive Statements
- Brief, casual dismissals feel very human.
- **Do**: "Not doing any of that.", "None of that here.", "That's not happening."
- **Don't**: Always explain or justify exclusions formally

### P13: Sentence Fragments as Statements
- Dropping subject occasionally feels natural.
- **Do**: "Compared how the different algorithms performed." (no "I")
- **Don't**: Every sentence must be grammatically complete

## Medium

### P09: Casual Connectors
- AI uses formal transitions. Humans are casual.
- **Do**: "also", "Lastly", "fits in as", "is also related to"
- **Don't**: "Furthermore", "Additionally", "Moreover"

### P10: Unbalanced Treatment
- Real notes aren't symmetrical.
- **Do**: Some points get one word, some get a sentence, some skipped
- **Don't**: Give every item equal length and detail

### P11: Mixed Formats
- Real documents mix prose, bullets, fragments.
- **Do**: Use bullets where natural, mix with prose
- **Don't**: Force everything into flowing paragraphs

---

# NEGATIVE SIGNALS (AI Markers to AVOID)

Ranked by impact. These patterns trigger AI detection.

## Critical

### N01: AI Vocabulary Red Flags
Specific phrases statistically more likely to be AI.
- **Flagged**: "strategic importance" (9.5x), "actionable insights" (7.8x), "addressing concerns" (7.3x), "selecting appropriate" (6.4x), "stakeholders including" (6.1x), "relied heavily" (5.1x), "systematic approach" (4.6x), "success was measured" (4.4x), "leverage", "utilize", "facilitate"
- **Fix for "strategic importance"**: "key value" (business), "big deal" (casual), "pivotal role" (creative)
- **Fix for "addressing concerns"**: "resolving issues" (academic), "dealing with worries" (simple), "sorting out worries" (casual)
- **Fix for "selecting appropriate"**: "choosing the right", "picking suitable"
- **Fix for "stakeholders including"**: "stakeholders like", "stakeholders such as", or list directly
- **Fix for "relied heavily"**: "leaned a lot" (casual), "was largely based" (business), "depended significantly" (academic)
- **Fix for "success was measured"**: vary across objectives - "success was evaluated/assessed/judged/gauged". Better yet, restructure entirely: "I evaluated success by...", "The key metric was...", "What mattered was..."
- **Fix**: "useful findings", "step-by-step", "use", "help"

### N02: Over-Completeness
AI writes like filling a form - every item gets full explanation.
- **Problem**: "Uses X for Y and Z for W" explains what each thing does
- **Fix**: Just name things. Assume reader knows context. Leave gaps.

### N03: Balanced/Systematic Treatment
Every bullet has similar length, structure, detail level.
- **Problem**: Too symmetric, obviously machine-generated
- **Fix**: Be deliberately uneven. Some detailed, some brief.

## High

### N04: Mechanical Transitions
Subordinate clauses connecting ideas too smoothly.
- **Problem**: Overly fluid, logical flow
- **Fix**: Shorter sentences. Allow abruptness. Use "and" or full stops.

### N05: Monotonous Syntax
Same sentence structure repeated. Declarative after declarative.
- **Problem**: Main clause + descriptive phrase, repeated
- **Fix**: Mix types. Questions. Fragments. Start with "And" or "But".

### N06: Checklist Structure
Text reads like ticking boxes.
- **Problem**: "X covered. Y covered. Z covered."
- **Fix**: Write like explaining to a colleague, not filing a report.

### N07: Identical Bullet Structure
Multiple bullets with identical format.
- **Problem**: "K13: Topic - list", "K14: Topic - list" pattern
- **Fix**: Vary formats. Some sentences, some fragments. Change punctuation.

### N08: Colon-List Pattern
Repeated "Label: item, item, item" structure.
- **Problem**: Too systematic
- **Fix**: Use "such as", integrate into prose, vary structure.

### N09: Passive Voice Constructions
- **Problem**: "is handled through", "is defined by", "is covered in"
- **Fix**: Active voice. "They use Power BI" not "visualisation is handled through".

### N10: "The aim is" / "The goal is"
Stating aims explicitly sounds instructional.
- **Problem**: "The aim is practical outputs"
- **Fix**: Just describe what it does. Don't state intentions.

### N11: Formal Participles
- **Problem**: "acknowledged", "identified", "specified", "defined"
- **Fix**: "notes", "lists", or just state directly

### N12: Academic Qualifiers
- **Problem**: "quantitative targets", "qualitative assessment"
- **Fix**: Just "targets" or "numbers". Drop academic words.

### N13: "For/To" Purpose Explanations
AI always explains why.
- **Problem**: "for ELV prediction", "to improve capital allocation"
- **Fix**: Just name it. "Gradient-boosted regression, clustering" - no explanation.

### N14: Mechanical Precision with Technical Terms
Stacking precise terms in perfect lists.
- **Problem**: Every technical term placed systematically
- **Fix**: Integrate naturally. Don't list all in one breath.

## Medium

### N15: Predictable Syntax with Numbered Lists
- **Problem**: "S14 - doing X; S15 - doing Y; S16 - doing Z"
- **Fix**: Vary structure. Don't use identical patterns.

### N16: Overly Formal Vocabulary
- **Problem**: "evidences", "comprehensively scoping", "formulating"
- **Fix**: "shows", "covers", "making"

### N17: Impersonal/Indirect Tone
- **Problem**: "S19 is shown by", "It evidences"
- **Fix**: Be direct. Name what's happening.

### N18: Formulaic Organisation
- **Problem**: Clear headings, consistent sections, perfect order
- **Fix**: Allow slight messiness. Unequal treatment.

### N19: Task-Oriented Linear Structure
- **Problem**: Addressing topics in logical order like a checklist
- **Fix**: Jump around. Come back to things. Natural thought flow.

### N20: Sequential Reference Listing
- **Problem**: S01, S06, S14, S15, S16... K13, K14, K15, K16 in order
- **Fix**: Group by theme. Mention codes parenthetically.
- **Exception**: Codes AFTER content in parentheses can work: "inspiring others to deliver technical solutions (B01)" - the content leads, code follows as reference

### N21: Mechanical "Which" Connectors
- **Problem**: "which addresses S06", "which speaks to K13"
- **Fix**: Use full stops. Or rephrase as separate sentence.

### N22: "Sets/Defines/Specifies" Verbs
- **Problem**: "sets targets", "defines requirements"
- **Fix**: "has targets", "includes", or state directly

### N23: Explaining Benefits
- **Problem**: "gives teams practical outputs", "something they can use"
- **Fix**: Just state what it is. Don't sell the benefit.

### N24: Sophisticated Vocabulary
- **Problem**: "enrichment layer", "centres on"
- **Fix**: "extra data from", "is about"

### N28: Short Polished Statements
Short sentences that are too "perfect" still trigger AI.
- **Problem**: "The deck format is well-structured."
- **Fix**: Make it casual: "Deck's well laid out" or integrate into another sentence

## Low

### N25: Rigid Guidance Tone
- **Problem**: Sounds like giving advice or requirements. "X need to know", "It's essential that", "This ensures"
- **Fix**: Describe what IS there, not what SHOULD be. Don't tell stakeholders what they "need"

### N26: Subordinate Clause Connectors
- **Problem**: "since", "as" creating smooth logical connections
- **Fix**: Full stops. Keep it blunt.

### N27: Over-Fragmentation
- **Problem**: Too many fragments becomes its own pattern
- **Fix**: Mix fragments with proper sentences. Use sparingly.

---

## Quick Reference

**Always DO:**
- Use "etc." to trail off
- Use first person "I" / "we"
- Use "such as" for lists
- Use contractions ("We've got", not "We have")
- Use hyphens (-) not em dashes (—)
- Allow minor imperfections
- Be unbalanced in treatment
- Use colloquial phrases ("that sort of thing", "that's what this is really about")
- Use fragments occasionally ("Compared how...")
- Use filler words ("actually", "really", "basically", "some")
- Use vague endings ("improve things" not "improve business outcomes")

**Always AVOID:**
- "actionable insights" and similar AI phrases
- Explaining everything completely
- Symmetric bullet structures
- Passive voice ("is handled through")
- Academic words ("quantitative")
- Purpose explanations ("for X", "to achieve Y")
- Perfect grammar throughout

---

## Meta Rule: Don't Overuse Any Single Pattern

Any human signal used too consistently becomes a new AI pattern:
- "I've" at start of every bullet → monotonous
- "such as... etc." in every list → predictable
- Same structure repeated → robotic

**Vary everything.** Mix techniques. Don't let any single pattern dominate.

### Variance Lists (rotate these, don't repeat):

**Casual openers (instead of always "basically"):**
- "basically" / "essentially" / "in short"
- "So this is..." / "This is really..."
- "Right, so..." / "OK so..."
- "What this is, really, is..."
- "This one's about..."
- Start with the content directly, no opener

**Filler words (rotate):**
- "actually" / "really" / "basically" / "essentially"
- "sort of" / "kind of" / "more or less"
- "pretty much" / "largely" / "mostly"

**Casual nouns (rotate):**
- "stuff" / "bits" / "things" / "parts"
- "the X side of things" / "the X bit"

**Trail-off phrases (rotate):**
- "etc." / "and so on" / "that sort of thing"
- "and the rest" / "all that" / "and all that"
- "the usual X stuff" - casual ending for lists
- "that's the kind of X here" - casual connector for evidence lists

**Idioms/Colloquial phrases (rotate):**
- "at the end of the day"
- "no hand-holding"
- "the whole point"
- "down the line"

**Sentence starters (rotate):**
- "Plus..." (to add items casually)
- "So..." / "Right, so..."
- "Basically..." / "Really..."
