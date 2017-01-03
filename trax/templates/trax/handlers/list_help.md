{% extends "trax/handlers/base_help.md" %}

{% block content %}You can also provide a date or a hint to query timers from a specific point of time. Example:

- `/<trigger> list yesterday`
- `/<trigger> list sunday`
- `/<trigger> list 2016-09-07`
- `/<trigger> list two weeks ago`
- `/<trigger> list last month`
{% endblock %}
