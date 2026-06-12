# 1001D_R1 Intent Clarification Card Fixture Report

## Result

`XIAOJIAO_INTENT_CLARIFICATION_CARD_FIXTURE_PASS`

Marker:

`ALL_1001D_R1_INTENT_CLARIFICATION_CARD_FIXTURE_CHECKS_OK`

## What This Proves

This fixture proves that semantic confirmation cards can sit between Intent Parser and Action Gate.

The covered flow is:

```text
teacher utterance
-> initial low or ambiguous intent
-> clarification card
-> teacher selection event
-> confirmed_intent
-> action gate handoff
```

All cases keep `token_cost=0` and `model_call_executed=false`.

## Covered Cases

- `先帮我看一下这个` -> choose prepare lesson
- `学习单那个先弄一下` -> choose generate simple classroom-practice handout
- `这节课处理一下` -> choose confirm lesson draft
- `第二环节改一下` -> choose shorten duration while keeping the activity
- `按刚才那个风格来` -> choose preference candidate only

## Important Boundary

This is not a real UI implementation.

It only defines the semantic payload that a future UI may render as:

- inline chips
- small cards
- parameter drawers

It does not modify frontend files, connect runtime routes, call provider/model APIs, write database records, write memory, write Feishu, create formal exports, or enter 1000F.

## Product Meaning

Xiaojiao should not force teachers to type precise instructions.

When language is vague, the system should put likely actions in front of the teacher and let one click produce clean structured intent data.

This keeps the structure stable while teacher semantics remain iterative.

## Next

`1001D_R1_REVIEW_PENDING_BEFORE_1000F`
