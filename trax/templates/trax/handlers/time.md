{% load tz %}
{% timezone timezone %}
The current date/time in timezone {{ timezone }} is **{{ current }}**
{% endtimezone %}
