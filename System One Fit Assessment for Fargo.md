# System One Fit Assessment for Fargo

Oct 29, 2026 · @Sri

Fargo runs on an LLM today. We want to know how much of that work a System One model could take over, and whether it's worth it.

A System One model doesn't write anything. You give it a question and a list of answers, and it picks one and tells you how sure it is. So it can't replace the LLM, but it could handle the quick decisions inside each conversation. My guess is we end up with a mix: System One for routing and checks, the LLM for anything the customer reads.

The sections below are the things we need to check before we can say yes or no. Each one ends with what a good result looks like. The scorecard at the end pulls it together.

## 1. What it can and can't do

System One answers three kinds of questions: pick one from a list, give a score, or say yes or no. Anything that needs real writing stays with the LLM.

| Fargo task | Can System One do it? |
| --- | --- |
| Work out the customer's intent | Yes |
| Pick the right agent or tool | Yes |
| Check if a message is off-topic or a prompt attack | Yes, but don't rely on it alone |
| Work out which account or card they mean | Yes |
| Score how risky a transfer looks | Yes |
| Pull out amounts, dates or payee names | No, it's weak with numbers and dates |
| Plan multi-step tasks | No |
| Write the reply to the customer | No |

What to check:

- [ ] Go through everything the Fargo LLM does today and mark each one yes, partly or no.
- [ ] Make sure our longest lists (intents, tools) fit within its limits.
- [ ] Check it handles every language Fargo supports. It works best in English.

Good result: routing, checks and risk scoring all come out as yes.

## 2. Where it fits in a conversation

A single Fargo turn makes several small decisions before the customer sees an answer. Those are the places System One could step in:

- Is this a banking question at all?
- Is someone trying to trick the assistant?
- What does the customer want, and which agent should handle it?
- Which tool should the agent call?
- Which account or card do they mean?
- Is this transfer risky enough to ask for confirmation?
- Can we answer with a simple template, or do we need the LLM?
- Does the reply actually match the data we got back?

Simple requests like "what's my balance" might not need the LLM at all. That's where most of the savings would come from.

What to check:

- [ ] Take about 1,000 recent conversations and count how many LLM calls each turn makes, and what each one is for.
- [ ] Work out what share of those calls are really just picking from a list.
- [ ] Work out how many whole turns could skip the LLM.
- [ ] Decide what happens when System One isn't confident: fall back to the LLM, or ask the customer.

Good result: real numbers from our own traffic, not estimates.

## 3. Is it accurate enough?

There isn't much public data on how well these models do, and most of what exists comes from the vendors. Early users report mixed results. So we need to test it on our own conversations.

What to check:

- [ ] Build a labeled test set for each decision, around 500 examples each, from real Fargo conversations.
- [ ] Include the tricky ones: two requests in one message, "not that account", vague wording, long chats, Spanish.
- [ ] Run the same set through System One and our current LLM and compare.
- [ ] Check whether its confidence scores mean anything. When it says 90% sure, is it right about 90% of the time?
- [ ] Pick confidence cut-offs: act on its own, ask the customer, or hand to the LLM.
- [ ] Try to fool it with hidden instructions in the message.

Good result: when it's confident enough to act alone, it's at least as accurate as the LLM.

## 4. Is it faster and cheaper?

On paper, yes. The hosted System One model costs $0.042 per million input tokens with free output, and claims answers in 70 to 500 ms ([OpenRouter](https://openrouter.ai/typesafe/jev-1.13)). But those numbers come from the vendor, measured in the US. The bigger win is fewer LLM calls per turn, which also helps with the token cost problem we flagged in the Fargo FMEA.

What to check:

- [ ] Measure today's speed and cost per turn so we have a baseline.
- [ ] Measure System One's speed from our own network, including the slow cases.
- [ ] Estimate the new cost per turn, counting the times we still fall back to the LLM.
- [ ] Make sure its rate limits can handle our busiest hour.

Good result: turns get noticeably faster and the monthly bill drops, by a margin we agree on up front.

## 5. Can we use it safely?

This is the one most likely to stop us. The hosted System One model is only offered as an outside API, it's still in early access, and there's no published policy on how long it keeps our data. Sending customer data there would need a lot of sign-off.

What to check:

- [ ] List which decisions would send account details, transactions or personal data.
- [ ] Test whether we can strip personal data out first without hurting accuracy.
- [ ] Get the vendor's data retention and training terms in writing.
- [ ] Ask about private or on-prem deployment.
- [ ] Run it through vendor risk and model risk review.
- [ ] Never use it as our only defense against prompt attacks.
- [ ] Log every question, answer and confidence score for audit.

Good result: security, legal, vendor risk and model risk all approve, even if only with personal data removed.

## 6. How it plugs into Fargo

System One has its own API. It doesn't look like a normal chat model, so we can't just swap it in through ADK or Tachyon. We'd wrap it as a small decision service that the Supervisor and agents call.

What to check:

- [ ] Decide where it gets called: inside the agents, or as a step in the Flink flow.
- [ ] Find out whether Tachyon can route to it, or needs a new kind of connection.
- [ ] Make sure its calls show up in Arize and Overwatch next to the LLM calls.
- [ ] Work out how it fits with Supervisor routing and the Dialogflow CX handoff.
- [ ] Plan what happens if it's slow or down: fall back to the LLM without the customer noticing.
- [ ] Run it quietly alongside the LLM first, compare, then switch on one decision at a time.

Good result: a reviewed design that adds at most one extra call per turn and has a working fallback.

## 7. Models to compare

We shouldn't test just one option. If the hosted model fails the safety review, we need something else ready.

| Model | Where it runs | Good at | Watch out for |
| --- | --- | --- | --- |
| System One (hosted) | Vendor's API only | Accurate out of the box, very fast | Data leaves the bank; young vendor |
| GPT-6 Luna | OpenAI, Azure, Bedrock | Can decide and write replies; already on clouds we use | Slower (1 to 2.6 s); confidence scores need checking |
| CLM-8B | Our own servers | Fast with fixed lists of intents or tools | A bit less accurate |
| Laya | Our own servers, small | Cheap, runs without a GPU | Needs training on our data first |

What to check:

- [ ] Run the section 3 tests on at least two of these. For GPT-6 Luna, turn off reasoning, force a fixed answer format, and check whether it gives probabilities.
- [ ] Keep our decision service model-agnostic so we can switch later.
- [ ] Look at the vendor's support, uptime promises and how they handle new versions.

Good result: at least one model passes sections 3 to 6.

## 8. POCs we can run in Postman

We can do 12 quick POCs in Postman without writing code. Each one is a collection: a CSV of test messages, the Collection Runner sending them to the model, and a small test script that checks each answer.

| # | POC | What we check |
| --- | --- | --- |
| 1 | Intent routing | Does it pick the right intent? |
| 2 | Off-topic check | Does it spot non-banking questions? |
| 3 | Prompt attacks | Does it catch messages trying to trick it? |
| 4 | Tool choice | Does it pick the right tool? |
| 5 | Which account | Does it pick the account the customer means? |
| 6 | Transfer risk | Do risky transfers land in the right band? |
| 7 | Template or LLM | Can it tell when a simple answer is enough? |
| 8 | Reply check | Does it catch replies that don't match the data? |
| 9 | Side by side | System One vs GPT-6 Luna on the same messages |
| 10 | Batched questions | Is one Luna call with several questions as good as separate calls? |
| 11 | Consistency | Does it give the same answer every time? |
| 12 | Speed and outages | How fast is it, and does our fallback work when it's down? |

Some things Postman can't do well. We'll need a spreadsheet or Python to check whether the confidence scores hold up and to get proper P95 speeds, a load-testing tool for peak traffic, and real code for the Fargo integration.

One caution: Postman saves collections and results to its cloud by default. Use made-up or cleaned data, keep API keys out of shared collections, and check if we need a local-only workspace.

## Scorecard

Fill this in as each check is done.

| Check | Result | Notes / owner |
| --- | --- | --- |
| 1. What it can do | Not started |  |
| 2. Where it fits | Not started |  |
| 3. Accuracy | Not started |  |
| 4. Speed and cost | Not started |  |
| 5. Safety | Not started |  |
| 6. Fit with Fargo | Not started |  |
| 7. Model comparison | Not started |  |

How we decide:

- **Go:** everything passes.
- **Go, but partly:** some decisions pass, or it only passes with personal data removed, or a different model (GPT-6 Luna, CLM-8B, Laya) does better. We use it where it works.
- **No:** it fails safety with no workaround, or it would save too few LLM calls to be worth it.

My expectation is "go, but partly": System One for routing, checks and risk scoring, and the LLM for everything the customer reads.

## Sources

- [System One model page (OpenRouter)](https://openrouter.ai/typesafe/jev-1.13)
- [System One overview (Lindy)](https://www.lindy.ai/blog/jev-ai)
- [The Register on System One](https://www.theregister.com/a/5298431)
- [GPT-6 Luna on OpenRouter](https://openrouter.ai/models/openai/gpt-6-luna-20260922)
