{{ reminder.message }}
{% if reminder.is_recurring %}This recurring reminder was scheduled by {{ reminder.user.username }}. Next ones are:

{% for date in reminder.all_next %}- {{ date }}
{% endfor %}
{% else %}
This reminder was scheduled by {{ reminder.user.username }}.
{% endif %}
