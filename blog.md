---
layout: page
title: Blog
---

<div class="posts">
  {% for post in site.posts %}
  <div class="post">
    <h1 class="post-title">
      <a href="{{ post.url }}">
        {{ post.title }}
      </a>
    </h1>

    <span class="post-date">{{ post.date | date_to_string }}</span>

    <p><em>{{ post.meta }}</em></p>
    {{ post.excerpt }}
    <a href="{{ post.url }}">Read more!</a><br /><br />
    <img src="/public/img/delta.png" width="36" height="36">
  </div>
  {% endfor %}
</div>
