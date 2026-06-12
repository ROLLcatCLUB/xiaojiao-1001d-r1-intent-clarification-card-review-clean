# 1001D_R1 Intent Clarification Card Fixture

## Stage

`1001D_R1_INTENT_CLARIFICATION_CARD_FIXTURE`

This stage defines the semantic confirmation layer between intent parsing and action gating.

It does not implement real UI. It defines the structure that a future UI can render as lightweight chips, a small card, or a half-screen parameter drawer.

## Core Judgment

Teacher semantics should not depend on long free-text input.

Xiaojiao should first infer likely intents, then present a small set of useful options when the intent is ambiguous or when a generation action needs structured parameters.

The teacher selection becomes structured data:

```json
{
  "intent": "generate_handout",
  "target_object": "handout_G4_A2_L003",
  "confidence": 1.0,
  "source": "clarification_card_selection"
}
```

## Scope

This fixture proves:

- ambiguous utterance to clarification card
- teacher card selection to confirmed intent
- confirmed intent to action gate handoff
- generation parameter card to context-pack hints
- revision direction card to scoped generation boundary
- card selection signals to observation metrics
- repeated choices to preference candidate only

## Card Types

- `inline_chips`: simple 1-step actions near the work object
- `small_card`: 2 to 4 choices for intent clarification
- `parameter_drawer`: compact generation parameters before model-candidate handoff

## Required Cases

- `ambiguous_this_object`
- `handout_do_that`
- `lesson_handle_this`
- `revise_second_section`
- `same_style_preference`

## Hard Boundaries

- not a real UI implementation
- not a real runtime route
- not a real Intent Parser implementation
- not a real model call
- not a database write
- not a memory write
- not a Feishu write
- not a formal export
- not a frontend modification
- not a student-side or classroom runtime connection
- not 1000F

## Acceptance

The fixture passes only if every case:

- starts from an ambiguous or parameter-needing teacher expression
- emits a card with 2 to 4 bounded options
- records a teacher selection event
- produces a confirmed intent with confidence `1.0`
- hands the result to the action gate
- keeps `token_cost=0`
- keeps `model_call_executed=false`

## Semantic Principle

Stable structure, iterative semantics.

This stage fixes the schema for cards and confirmed intents, but does not claim that teacher semantics are complete.

Future semantic updates should happen through registries:

- `intent_registry`
- `utterance_pattern_registry`
- `clarification_card_registry`
- `suggestion_template_registry`
- `context_pack_policy_registry`
- `preference_candidate_registry`
- `observation_metric_registry`

## Next

`1001D_R1_REVIEW_PENDING_BEFORE_1000F`
