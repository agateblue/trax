{% load trax_tags %}
{% with current_timer=timer_group.current_timer %}
{% if current_timer.duration > 1 %}
Timer "{{ timer_group.name }}" is already timing and so far you have tracked {{ timer_group.today_duration|humanize_timedelta }}.
{% else %}
Timer "{{ timer_group.name }}" was started.
{% endif %}
{% endwith %}
