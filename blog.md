---
layout: page
title: Blog
background: grey
---

<h3>Latest Posts</h3>

{% for post in site.posts %}
<article class="blog-post-preview">
  <h4><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h4>
  <p class="post-meta">{{ post.date | date: "%d/%m/%Y" }}</p>
  <p>{{ post.content | strip_html | truncatewords: 30 }}</p>
  <p><a href="{{ post.url | relative_url }}">Read more →</a></p>
</article>
<hr>
{% endfor %}