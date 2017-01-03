{% if user.timer_groups.count > 0 %}
You did not provide a valid timer name, here is a list of your most used timers:

{% for t in user.timer_groups.order_by_usage.with_position|slice:':15' %}{{ t.queryset_position }}. {{ t.name }}
{% endfor %}
{% else %}
Please provide a valid timer name. Examples:

- `/<trigger> start making coffee`
- `/<trigger> start important meeting`

{% endif %}
