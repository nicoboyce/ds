---
layout: post
title: "Quick wins: Getting started with the Zendesk API"
---

I am always always hearing ops managers who want to get better at Zendesk having this particular problem. 

They've some understanding of engineering and they're looking to explore how Zendesk objects look via the API. They have set up token access but hit a roadblock<!--excerpt-end-->:

"I can't get Postman to talk to Zendesk! It just says error 401"

It's not obvious but this is how to do it. You just choose "basic auth" and add /token to the username, which will be the email address for your Zendesk account. The password is the token.

For example if your email address is nico@deltastring.com (probably not because that's my email address) set your Basic Auth username to be "nico@deltastring.com/token" and the password to be the token string.

![Connecting to Zendesk in Postman.](/public/img/postman.png)
*Connecting to Zendesk in Postman.*

Make sure you're using a GET type request and take a look through the responses to queries such as https://{your-domain}.zendesk.com/api/v2/{object}.json where {object} can be macros, views, triggers, and other objects as described in the [Zendesk developers API reference](https://developer.zendesk.com/api-reference/ticketing/introduction/).

Be sure to let me know any suggestions you have for more quick wins I can share!