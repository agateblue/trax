{% load trax_tags %}
Your time tracking statistics for the period from {{ start_date }} to {{ end_date }}:

|          | {% for header in headers %}{{ header.date }} | {% endfor %} **Total** |
| -------- | ----------- | ------- |{% for row in rows %}
| {{ row.label }} | {% for value in row.values %}{% if value %}{{ value }}{% else %}-{% endif %} |{% endfor %} **{% if row.total %}{{ row.total }}{% else %}-{% endif %}** |{% endfor %}
| **Total**    | {% for v in interval_totals %}**{% if v %}{{ v }}{% else %}-{% endif %}** | {% endfor %} **{% if total %}{{ total }}{% else %}-{% endif %}** |
