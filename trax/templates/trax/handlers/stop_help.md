{% extends "trax/handlers/base_help.md" %}

{% block content %}When stopping your timer, you can also provide an optional time at which the timer should be stopped. This is especially useful if you forget to stop a timer:

    # we start a timer
    /<trigger> start some task

    # we work one hour and forgot to stop the timer
    # two hours after that, we retroactively stop the timer
    /<trigger> stop one hour ago

You can provide relative times or absolute ones. Examples:

- `/<trigger> stop 10 minutes ago`
- `/<trigger> stop 17:35`
{% endblock %}
