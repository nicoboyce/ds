---
layout: post
title: Zendesk teams are mostly using Pending wrong
published: false
---

It's 2023 and we all ought to know better than to be dragged into daft debates on the internet. This is particularly true on two of my favourite sites, Stack Overflow and [LinkedIn](https://www.linkedin.com/in/nicoboyce/){:target="_blank"}. Yet here I am needing more words and space to explain this one. At least we're now on my own website where no one can write underneath "You're wrong Nico!" and create further confusion.

If you're reading this, you're probably familiar with the Pending status in Zendesk and also might have chuckled at the post which led to this. It was just a daft meme of someone celebrating, captioned "When they finally let you solve the thousands of tickets in the Pending view" or similar. This was of course sufficient to trigger a lengthy argument: what is the Pending status even for?<!--excerpt-end-->

### Isn't it obvious?

Okay, so on the face of it the purpose of Pending is evident. It's where a ticket is in a paused state waiting for the Requester to take an action. In fact we can go straight to the Zendesk admin panel and check how they describe Pending:

![Zendesk status families.](/public/img/pending.jpeg)
*Status in Zendesk, without any custom configuration.*

So there we have it, let's put our tickets in pending when it's the turn of the Requester to respond. But wait, why are we doing that? Does this help us help the customer better?

### What's wrong with the traditional ticket lifecycle?

Ultimately, the customer is reaching out (or we're creating a proactive ticket) because there's an issue that needs some resolution. That issue is usually one of information asymmetry. Even in the case of, say, a damaged physical product being received, this is true. The Zendesk ticket is not the actual process of fixing or replacing that item, it is where the information is exchanged that subsequently can enable that situation to be closed.

Each of the status values in Zendesk correspond to a position in the process of each party informing the other of their knowledge. These positions are as follows:

* New: the Requester is bringing the initial situation to your attention, hopefully with some context to help towards finding a solution.
* Open: now the Agent must process and decide what action to take based on the facts in the ticket, most likely providing information to the Requester in the process.
* Pending: the Agent has requested a response from the Requester, which may be key data (an order number, an address) or it may be to confirm acceptance of a proposed resolution.
* On Hold: the Agent has processed the information from the ticket in the Open state and identified a third party who needs to take an action before the Requester can be informed of a conclusion.
* Solved: each party has accepted the outcome of the situation and no further action or discussion is needed.
* Closed: this is an archived state following from Solved where the ticket remains only for review purposes.

![Zendesk ticket lifecycle.](/public/img/zendesk-ticket-lifecycle.jpeg)
*The possible routes between Zendesk status families.*

However, it then becomes apparent that there is a weak link in the chain as we put together workflows. We can (hopefully) presume a timely and useful response to our On Hold tickets. So long as our views are well-configured then we can also know that Open and New tickets are put in front of agents. The Pending status puts our workflow in jeopardy though. We can't rely on the Requester to respond.

### To chase? Or let it rot?

The instinctive approach is to chase these Pending tickets, automate some reminders to the Requester and basically nag them into coming back to us and letting us try and solve their problem.

Is this the right approach though? I'm not sure it's best for either party.