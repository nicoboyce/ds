---
layout: post
title: "Quick wins: Zendesk macro validation"
---

Inspiration for today's quick win comes from Reddit user Yaldabaoth2000, who asked the community "How to prevent a macro being sent until things are filled out" in a post [here](https://www.reddit.com/r/Zendesk/comments/1cx3d08/how_to_prevent_a_macro_being_sent_until_things/).

Let's dive in and see if we can come up with a better answer than Reddit managed<!--excerpt-end-->:

To be honest, Reddit isn't the place to go for this. You'll find experienced Zendesk pros on the Slack at [Support Driven](https://www.supportdriven.com/) or in the Linkedin Zendesk Certified group or plenty of other places, but I don't recommend Reddit. This particular discussion is a great example.

![Reddit doesn't Zendesk.](/public/img/reddit.jpeg)
*Reddit doesn't Zendesk.*

You can totally solve this problem.

For starters, don't have macro sections that need manual editing. Put these things in a ticket field which is only revealed in the form when relevant.

Obviously you can use Liquid markup to populate the macro text from field values, but if you do this directly then you're still not validating the message before sending it to your end user.

What you do instead is you use Liquid in a macro to populate an internal note which validates the field values, then you use the exact same logic in a pair of triggers which send the actual response to the customer.

Here's a real-life example of the macro Liquid markup:

```
{% if clientID != empty and tier != \"-\" %}
Transfer: ok.

Hello accounts team. This ticket was transferred from {{ ticket.group.name }}.
{% else %}
Ticket transfer failed, please check the client and tier fields.
{% endif %}
```

You can see that this macro lets the agent know whether the ticket transfer will go ahead. It also lets the accounts team know where the ticket came from. The macro also adds a tag, something like `transfer-requested` which can activate a trigger.

We follow that up with a pair of triggers. The first applies the new group and sends a response to the customer ("We've passed your query over to the accounts team, they will update you within 24 hours") having checked the fields have values. It also removes the `transfer-requested` tag and instead adds `transfer-completed` for example.

There's a second trigger for the situation where the fields have not been updated but the macro is submitted anyway. This one adds another internal note, assigns the ticket to the submitting agent, removes the `transfer-requested` tag and adds `transfer-denied` for reporting purposes.

It's a little more involved than maybe our Reddit friends would like, but it can save so much time for your teams if your fields are validated rather than teams play ping-pong with tickets!