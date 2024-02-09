---
layout: post
title: Channel hopping
---

This is a challenge I have seen different clients deal with in different ways.

If you connect every channel going, you can cause multiple problems for yourself and for your customers. Tickets are hard to track for them. There is a kind of choice paralysis. Volume can increase as it's easier to click through to a chat window than work out how to express the issue in a way that the search engine in the help centre parses. Tickets have different levels of enrichment data depending on channel.<!--excerpt-end-->

Alternatively, you can make decisions about where your customers should reach out to you. I have seen this done well, and I have seen this done very badly. A domestic utility company used Whatsapp messaging and telephone calls, which covered where their customers wanted to speak to them (and enabled easy exchanging information, eg. pictures of meters) but I know of a London app developer who have multiple connected channels but if you use any of them except the webform you get sent a link to it and your ticket closed.

There needs to be a little friction to just asking rather than looking for the answer yourself, but the best Zendesk implementations make this feel like "We can help you quicker if you try this likely solution first" rather than when you call up, for instance, your local council tax office and the IVR tells you twenty times "Did you know you could do this online" and you find yourself shouting at a machine. See the livechat from https://www.scottishpower.co.uk/livechat for instance. https://www.ultimate.ai/ are the best at this.

I tend to recommend connecting closed channels last, eg. providing support via Facebook messenger or Xitter or places where your customers would need to have an account to be able to engage with you, except in the circumstance where that platform provides significant business or is where your community exist if that's appropriate. For example, Etsy obviously need to be contactable via Instagram or Apollo via Reddit.

As for open channels (email, xmpp/matrix bridge into Slack or Mattermost etc, sms/rcs, or services via http whether a web async interface or live chat) then the important factors are ease of verifying the identity (or using external authentication) for data protection and case enrichment but also not creating new overhead for customers (particularly in the b2b space) where they need to learn or even train for "this is how we deal with Checkout" which again I have seen elsewhere and is not a good situation. B2c you have the additional factor of reducing churn, consumers tend to give up easily and just go to a competitor.