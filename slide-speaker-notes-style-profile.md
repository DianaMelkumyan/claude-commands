# Speaker Notes Style Profile

This profile defines the voice, tone, and structure for webinar speaker notes at Thanx. It is the source of truth for how notes should sound. Read this before generating any speaker notes.

## Voice and Tone

- Conversational and direct. Speak to the merchant audience as peers.
- Use "we" when referring to the Thanx team. Use "you" when addressing merchants.
- Confident but not salesy. Factual, value-focused.
- Occasional personality is welcome ("On a different, but not less fun topic").
- Sound like a real person talking to an audience they respect, not like marketing copy.
- **Light and easy to listen to.** These notes will be read aloud. Every sentence should feel like something a person would actually say at a podium. If it sounds like a product brief being read aloud, rewrite it.

## Structure per Slide

Always follow this structure, regardless of whether existing notes are present:

1. Open with context or a transition. Examples:
   - "Let's talk about AI for a moment."
   - "Thanx is reimagining several workflows with AI in mind, starting with segment creation."
   - Reference the previous slide naturally when appropriate.
2. What it is: describe the feature and what it does for the merchant.
3. How it works: explain with specific details. Name real systems (Toast, NCR, Olo, Valutec), give timelines, describe mechanics.
4. What opportunity it unlocks / what goal it achieves: the business value, the outcome it enables, or what becomes possible.
5. Close with impact or forward-looking excitement.

Not every slide needs all five beats. Some slides are simple enough for steps 1-2 and a close.

**Match detail level to feature weight.** Complex features (new systems, new data flows, compliance requirements) benefit from specific mechanics - name the systems, describe the flow, give timelines. Simpler improvements (UI enhancements, expanded capabilities, quality-of-life updates) should stay at the benefit level - what it means for the merchant, not how it works under the hood. When in doubt, lead with the benefit and only add mechanics if they make the value more concrete.

## How to Handle Existing Notes on a Slide

Some slides already have notes. These range from polished and complete to rough talking-point reminders. Evaluate before deciding what to do:

**If the existing note already covers the structure well** (what it is, how it works, what problem it solves), keep it. Polish for tone and flow if needed, but don't rewrite what's already working.

**If the existing note is incomplete or one-dimensional** (e.g., it captures one angle but skips the structure), write fresh notes from the PRD using the standard structure. You can fold in the existing angle where it fits, but don't let it become the skeleton of the note.

How to tell the difference: check whether the note covers all three beats (what it is, how it works, what it achieves). If it only has one or two, it needs a rewrite, not an expansion.

**Common mistake to avoid**: When an existing note has a strong opinion like "This is table stakes for the DoorDash generation", don't build the entire note around that framing. That's color commentary. The note still needs the full structure: what the feature is, how it works across providers, what it achieves for the business. The commentary can stay as a line within that structure.

## Length

- Typically 4-6 short paragraphs per slide, 100-200 words total.
- Each paragraph is 1-3 sentences.
- Err toward shorter. Only exceed this range when the topic genuinely demands more detail, which is rare.

## Format

- Flowing paragraphs that read naturally when spoken aloud. NOT bullet points.
- No blank lines between paragraphs. Single-spaced paragraphs are easier to scan in the notes panel.
- Use **bold** for emphasis on key terms in the written version.
- No numbered lists or structured outlines in the notes.

### Sentence rhythm

- **One idea per sentence.** Don't pack multiple concepts into a single sentence. "Operations Center brings those tools together in one place" is good. "Operations Center brings together order management, location health, error reports, and delivery settings under a single tab with unified navigation" is too dense.
- **No inline lists.** If you're tempted to write "things like X, Y, Z, and W" in the middle of a sentence, either pick the one or two most important, or break them across sentences.
- **Give points breathing room.** Let each idea land before introducing the next. Use natural spoken connectors: "The goal here is simple:", "This is also an important foundation for the future."
- **Keep sentences short and varied.** Mix one-clause sentences with occasional two-clause ones. If a sentence has a comma and a dash and a parenthetical, it's too heavy for spoken delivery.

## Slide Content vs. Speaker Notes

The notes should complement the slide, not repeat it. The audience can read what's on the slide. The notes add value by explaining what the feature enables, how it works at a high level, and why it matters for the merchant. Don't restate every bullet on the slide unless it needs clarification.

The way to add value beyond the slide is to go forward (what this enables, what becomes possible), not backward (what was broken, what the current limitations are). "Complementing the slide" means enriching with opportunity and context, not contrasting with the status quo.

## How to Use the PRD

The PRD is a reference for accuracy, not a checklist. Do NOT try to cover every detail from the PRD. Do not introduce facts, claims, or capabilities that are not grounded in the PRD or slide content.

- Distill to value: focus on what matters to the merchant, not the mechanics of how it works internally.
- Lead with the feature and the opportunity, not the problem. Present what we're building first, then how it works, then the value it unlocks. Do not open with the pain point or frame the feature as fixing what was broken. These are merchant-facing notes - the tone should be forward-looking and positive. A brief nod to the current state is fine ("today, customers don't have visibility"), but it should not be the framing or the opening.
- Pick 2-3 of the most impactful points rather than enumerating every feature, pillar, or metric from the PRD.
- Save granular details (specific numbers, framework names, internal terminology) for only when they strengthen the point. "32 recommendations across four pillars" is product-doc language. "Personalized recommendations based on how you're currently using Thanx" is speaker language.
- If the PRD has a long list of capabilities, choose the ones that resonate most with the audience and mention the rest exist without listing them.

## Do

- Name systems and integrations when relevant (Toast, NCR, Olo, Valutec, Brame.io). Prefer brief, unified descriptions over per-provider breakdowns ("the experience will vary by provider" is often enough). But when providers differ in ways that matter to the merchant (e.g., one supports enrollment natively and others don't), calling that out is valuable.
- Make clear technical distinctions (e.g., POS types with enrollment flows trigger SMS on enrollment request; others trigger on any unknown phone number lookup)
- Keep transitions lightweight
- Use concrete examples over abstract promises
- Frame limitations honestly ("for security purposes, we have decided to limit this to purchases made within 48 hours")
- Distill complex features to their value proposition first, then add select details
- Ground features in what the merchant can actually do with them. Don't just describe the capability - help the audience picture using it. "You'll be able to send a notification with a branded image and a full message" is functional. "Whether that's promoting a seasonal offer, announcing a rewards milestone, or driving traffic to a campaign" is what makes it real. A brief use-case example turns a feature into a benefit.
- Preserve important caveats when they affect the merchant: phased rollout, partner-specific behavior, or how a feature works differently across systems. Frame these as "here's how it works" not "here's what's limited". These build trust.

## Do Not

- Repeat the same concept across slides (flagged: "faster turnarounds" appearing twice, "soon" overused)
- Use vague marketing language or superlatives
- Over-explain. If a point is clear, move on.
- Use bullet points in speaker notes
- Pad notes to seem thorough. Brevity is preferred.
- Use AI-polished phrasing: "revolutionize", "seamlessly", "empower", "game-changer", "cutting-edge"
- Use em dashes
- Use generic recap summaries ("In summary..." or "Overall, this means..."). A short closing line that reinforces the business goal is fine and expected - the structure ends on value/impact, so the close should land there. Just don't restate what was already said.
- Enumerate every detail from the PRD. Speaker notes are not product documentation.
- Use internal framework names or jargon the audience wouldn't know (e.g., "Crawl, Walk, Run" is internal; "scales with your program maturity" is audience-friendly)
- Front-load specific examples before the audience understands the concept
- Frame features as fixes for past mistakes or current gaps. "That's a gap", "the biggest fix", "right now it just gets cut off", "directly addresses feedback about X" all make the audience feel behind. This is the most common mistake in generated notes. Lead with what's coming and what it enables. A one-line nod to the current state is fine mid-note, but it must never be the opening, the framing, or the closing.
- Echo claims from the slide without verifying them against the PRD. The slide may overstate, misframe, or generalize. Always check before writing notes that repeat slide language.
- Overclaim beyond what the source material supports. Do not say "best in class", "industry-leading", or similar unless the PRD explicitly backs it. If a capability is partial or phased, say so.
- Use negative positioning. NEVER frame a feature by contrasting it with a bad current experience. "Instead of bouncing between multiple pages, you'll have a consolidated view" leads with frustration. The same applies to "no more X", "eliminates the need to Y", "unlike today where Z". Instead, state what the feature does and what business opportunities it opens up. "You'll have a consolidated view of operations across all your locations, which makes it much easier to spot trends and act on them quickly."

## Example: What Good Looks Like

Here is a real speaker note that reflects this style:

> Guests will soon be able to enroll in loyalty right at the counter. When a new guest enters their phone number or email at the POS, Thanx will send an SMS with a link to App-less, where they can complete their account using our new lightweight signup form.
>
> Toast and NCR already support native enrollment flows, so in those systems, an SMS is sent only when an actual enrollment request is triggered. For all other integrated POS systems, where native enrollment doesn't exist, we'll send the SMS whenever an unknown phone number is looked up. This ensures guests can still create or enhance their profiles, even if the POS itself doesn't drive enrollment.
>
> On Toast specifically, guests can also earn points for the purchase tied to their enrollment request. To ensure security and prevent misuse, this earning window is limited to purchases made within the last 48 hours.

Here is another example showing feature-first structure with business value at the end:

> Next, let's talk about order status and real-time order tracking.
> This gives guests much better visibility into what happens after they place an order from confirmation, to preparation, to pickup or delivery. Instead of feeling like the order disappears into a black box, they'll be able to follow its progress directly in the Thanx experience.
> For pickup orders, that means clear preparation stages and readiness updates. For delivery, we'll also support ETA-based updates. The exact experience will vary a bit by provider, but the goal is the same: give guests meaningful, real-time visibility no matter how the order is fulfilled.
> This keeps your customers engaged in your app after they order, cuts down on "where's my order?" calls to your stores, and brings your first-party ordering experience up to the standard set by DoorDash and Uber Eats.
> This is also an important foundation for Thanx building smarter recovery workflows. More on that later.

## Updating This Profile

After each session, if corrections or feedback reveal a lasting preference change (not a one-off adjustment), update this profile. Add specifics to the Do/Do Not sections. This is a living document.
