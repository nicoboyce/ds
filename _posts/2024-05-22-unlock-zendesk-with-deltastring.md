---
layout: post
title: How do you unlock your Zendesk? Why bring in Deltastring?
meta: Your customers see Zendesk as a core part of your service. Now you can treat it accordingly.
---

I was chatting with a friend-of-a-friend on [LinkedIn](https://www.linkedin.com/in/nicoboyce/){:target="_blank"} and while they were familiar with Zendesk, they weren't sure what a Zendesk consultant would do for a business. Maybe this is true more generally, so here's how I explained it on this day in history.

Bringing someone like me in is often not an obvious route. Zendesk is marketed as a no code solution, usually it is owned within BizOps and they just have their techiest support agent add macros etc. But then down the road it becomes a sprawling mess of disjointed objects<!--excerpt-end--> and there's no way they are handing it over to a product team like that. Your agents all need two screens and their fingers lock in to the shape of ctrl+c/v because your systems don't talk.

Usually at this point your ops managers answer the call from whichever SaaS vendor is cold calling at this time and they have all sorts of services to reduce the cost per ticket. But ultimately bigger savings can be achieved by just outsourcing to a BPO in the Philippines for example.

Where I come in is unlocking this cost-quality doom spiral. Because I am external, a third party engineer, I can translate from Ops to Product and back again, and because I have managed support agents and other customer-facing roles I can help to identify the opportunities.

The first thing is to get everything out there and understood. From the Ops side we need the process maps, particularly including escalation points, and all the documentation. I export all of the Zendesk objects over the API and have my own tooling for mapping these to CSVs which marry easily to the processes. We get all those files into version control, usually Github. Sometimes organisations prefer to keep Ops config in a separate Git instance to the product.

Next it’s about bringing in the Product people, which is straightforward when you have VCS, automated deployment, and the Zendesk sandbox test environment aligned. Collaboration becomes straightforward when what the Ops people see as GSheets/Excel/etc the engineers receive as the corresponding JSON.

![Deltastring unlock Zendesk collaboration.](/public/img/zendesk-integration-development-deltastring.jpeg)
*Deltastring unlock Zendesk collaboration.*

From there it’s about making Zendesk the hub for all the systems where support queries might end up. Sometimes this requires an external service to bridge APIs but mostly it’s not even that complex. Worse case scenario we have some BeautifulSoup as a stop-gap but I discourage this. Temporary solutions have a habit of becoming permanent. Any action the agent needs to take, they should be able to do this from the ticket. My personal favourite is when an agent can choose a macro to pull the transaction data from eg. Stripe as an internal note on the ticket - then that can pre-populate a response in liquid. It’s magic when it comes together.

But the real thing I leave clients with is that link between teams, the processes for proper continuous improvement and handling Zendesk like it’s a key part of the product stack.

Not everyone can appreciate the difference this could make to their organisation but plenty enough “get it” for me to keep busy. I’m often introduced to prospects by SaaS vendors who I have worked with before. My services start at £40k for a solo three month project or I can bring in other Zendesk or ops experts as needed (eg. UAT or project management specialists) so there’s a lot of flexibility.

Most companies will go for a band-aid solution instead — just get more people rather than make our tools efficient — but the problem with a band-aid solution is it hurts when it comes time to rip it off.