{% if setting %}{% if updated %}
Setting "{{ setting }}" was updated from "{{ old_value }}" to "{{ new_value }}".
{% else %}
The current value for setting "{{ setting }}" is "{{ old_value }}".
{% endif %}
{% else %}
Available settings are:

| Setting  | Current value | Description |
| -------- | -----------   | ----------- |{% for conf, value in available_settings %}
| {{ conf.name }} | {{ value }}   | {{ conf.description }} |
{% endfor %}
{% endif %}
