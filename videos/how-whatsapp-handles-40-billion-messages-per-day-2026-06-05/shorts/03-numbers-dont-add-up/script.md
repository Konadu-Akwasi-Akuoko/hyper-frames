<!-- HOOK -->
WhatsApp's own message numbers don't add up.

<!-- COUNTER-TWIST -->
On one ordinary day, twenty billion messages sent turned into sixty-four billion. Same messages. Where do the extra forty billion come from?

<!-- BODY -->
The answer is groups. When you fire a message into a group chat, your phone uploads it exactly once — a single copy, tagged with a group ID. That's all your battery and your data ever pay for.

The multiplying happens on the server. It looks up every member of that group and quietly queues a separate copy for each one. One message in, a hundred messages out.

This is server-side fan-out. And on the second of April, twenty fourteen, twenty billion messages people sent fanned out into forty-four billion delivered. Sixty-four billion in a single day. That gap isn't an error — it's fan-out, made visible.

And the real kicker: the cost scales with how big the group is, not with how many people are actually typing. One person can trigger thousands of deliveries.

<!-- CTA -->
But a few years later, they had to flip fan-out completely inside-out — just to let you read your chats on a laptop. Why? To see it, subscribe.
