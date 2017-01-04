{% extends "trax/handlers/base_help.md" %}

{% block content %}You can use the `config` command to retrieve and update your personal settings.

- `/<trigger> config`: will list all available settings
- `/<trigger> config <setting>` will display the value of a given setting
- `/<trigger> config <setting> <new_value>` will update the value of a given setting

For example, if you want to know which timezone you are using you can run `/<trigger> config timezone`.

If you want to switch to another timezone, just run `/<trigger> config timezone Europe/Istanbul`
{% endblock %}
