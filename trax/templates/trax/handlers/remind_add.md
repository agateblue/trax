Reminder `{{ reminder.message }}` was added and will be sent next time on {{ reminder.next_call }}.

{% if reminder.is_reccuring %}This is a recurring reminder with the following schedule: `{{ reminder.cron_description}}` (crontab: `{{ reminder.crontab }}`).

Following calls are:

{% for date in reminder.all_next|slice:"1:" %}- {{ date }}
{% endfor %}
{% endif %}
