{% if timer_groups|length > 0 %}
Timers were successfully stopped on {{ end_date }}:
{% for t in timer_groups %}
- {{ t.name }}
{% endfor %}
{% else %}
No timer was running
{% endif %}
