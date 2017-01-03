{% extends "trax/handlers/base_help.md" %}

{% block content %}You can also use shortcuts to start a timer. Consider the following output from /<trigger> start:

    You did not provide a valid timer name, here is a list of your most used timers:

        1. make coffee
        2. have a meeting
        3. take a nap

Then you can call `/<trigger> start 3` to start the `take a nap` timer.
{% endblock %}
