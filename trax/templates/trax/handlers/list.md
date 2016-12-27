{% load trax_tags %}{% if timer_groups|length > 0 %}Your timers for today are:
{% for group in timer_groups %}
- {{ group.name }}{% if group.is_started %}*{% endif %}: {{ group.today_duration|humanize_timedelta }}
{% endfor %}
{% else %}
    You did not started any timer today :)
{% endif %}
