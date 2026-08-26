---
layout: page
title: Karıncalar & Hayvanlar
permalink: /hayvanlar/
---

<ul class="post-list">
{% for post in site.categories.hayvanlar %}
  <li>
    <span class="post-meta">{{ post.date | date: site.minima.date_format }}</span>
    <h3><a class="post-link" href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
  </li>
{% endfor %}
</ul>
