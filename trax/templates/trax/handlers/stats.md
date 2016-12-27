{% load trax_tags %}
Your time tracking statistics for the period from {{ start_date }} to {{ end_date }}:

|          | {% for header in headers %}{{ header.date }} | {% endfor %} **Total** |
| -------- | ----------- | ------- |{% for row in rows %}
| {{ row.label }} | {% for value in row.values %}{{ value }} |{% endfor %} **{{ row.total }}** |{% endfor %}
| **Total**    | {% for v in interval_totals %}**{{ v }}** | {% endfor %} **{{ total }}** |
