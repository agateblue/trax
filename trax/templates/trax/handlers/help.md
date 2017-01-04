{% if help_content %}{{ help_content }}{% else %}Trax is a small tool to help tracking your time without hassle.

Available commands:

| Command | Description | Example |
| -------- | ----------- | ------- |{% for handler in handlers %}
| {{ handler.entrypoint }} | {{ handler.description }} | {{ handler.get_example }} |{% endfor %}
{% endif %}
