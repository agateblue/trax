{% if reminders|length == 0 %}
You don't have any reminders.
{% else %}
Your reminders are:

| ID   | Message | Type | Next call |
| ---- | ------- | ---- | --------- |{% for reminder in reminders %}
| {{ reminder.pk }} | {{ reminder.message }} | {% if reminder.is_recurring %}Recurring (`{{ reminder.crontab }}`){% else %}One shot{% endif %} | {{ reminder.next_call }} |{% endfor %}
{% endif %}
