{% load trax_tags %}{% if timer_groups|length > 0 %}Your timers for {{ date }} are:
{% for group in timer_groups %}
- {{ group.name }}{% if group.is_started %}*{% endif %}: {{ group.today_duration|humanize_timedelta }}{% endfor %}
{% else %}You did not started any timer on {{ date }} :){% endif %}
{% with user.timer_groups.order_by_usage.with_position|slice:':15' as qs %}{% if qs|length > 0 %}Your most used timers are: {% for t in qs %}
{{ t.queryset_position }}. {{ t.name }}{% endfor %}{% endif %}{% endwith %}
