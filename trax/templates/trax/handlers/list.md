{% if timer_groups|length > 0 %}
{% for group in timer_groups %}
- {{ group.name }}{% if group.is_started %}*{% endif %}
{% endfor %}
{% else %}
    You did not started any timer today :)
{% endif %}
