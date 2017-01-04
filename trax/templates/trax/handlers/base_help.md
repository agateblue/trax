{% block header %}
| Command | Description | Example |
| -------- | ----------- | ------- |
| {{ handler.entrypoint }} | {{ handler.description|safe }} | {{ handler.get_example|safe }} |
{% endblock %}
{% block content %}
{% endblock %}
