---
layout: post
title: "Zendesk sins: spam relay"
---

We all make mistakes. Ultimately the difference between a rookie Zendesk contractor and a greybeard is in the length of the trail of errors you leave behind. Perhaps also your rookie status is evident if [you leave your only charger in a meeting room](https://deltastring.com/2023/10/23/contracting-is-all-in-the-prep/)!

Here's a Zendesk sin I've encountered in the wild: making your own instance a handy relay for spammers.<!--excerpt-end-->

### Story time

I was pretty fresh to a gig at a company Bebop. They had never had a Zendesk pro come in and make sense of the spaghetti routing that had developed over time. Bebop had basically dropped all channels apart from a webform (of the one-form-to-rule-them-all variety) and these triggered an acknowledgement with some information about SLAs and some legal text.

The webform wasn't connected to the application identity, so there was no validation of who was creating tickets and no filtering of the body text, or description field in Zendesk terms. You can see where this is going. Spammers identified they could put any old rubbish into the webform and it would be included in an email to anyone they wanted to send it to.

![Statue I snapped somewhere.](/public/img/noo.jpeg)
*See no evil, or something.*

Bebop had inadvertantly created a handy tool for online villains.

### What's the big deal?

There's a whole bunch of reasons this kind of business is lucrative for miscreants. In this case, it was straightforward to deliver a malicious link to many different email addresses, with the Bebop brand legitimising it.

Since most email applications and browsers will precache linked content, in some cases the objective of the attacker can be achieved without any action at all from the targets.

> If I have seen further it is by standing on the shoulders of giants.

*Isaac Newton never had to debug in prod.*

### What is the right way to deal with this?

There are a whole bunch of things that were being done wrong here, but if there's one lesson then that lesson is never send any string in an automatic response that you didn't either create or validate. Yes, I am telling you that "Your ticket has been received" is sufficient.

It turned out that the baddies were periodically testing the results of their attack, with an individual email always precipitating a batch of a thousand or so from whatever botnet they were working with. As soon as I removed the {% raw %}`{{ticket.description}}`{% endraw %} placeholder then they gave up and moved on. Hopefully not to your instance!