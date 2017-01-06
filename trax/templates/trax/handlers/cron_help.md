{% extends "trax/handlers/base_help.md" %}

{% block content %}Cron is a special syntax to describe recurring things:

    * * * * * -> Cron expression
    │ │ │ │ │
    │ │ │ │ └──----- day of week    (0 - 6) (Sunday=0)
    │ │ │ └──------- month          (1 - 12)
    │ │ └──--------- day of month   (1 - 31)
    │ └──----------- hour           (0 - 23)
    └──------------- min            (0 - 59)

Here are a few examples of cron expressions with their meaning:

| Cron expression        | Meaning          |
| ---------------------- | ---------------- |
| `* * * * *`            | Every minute     |
| `0 * * * *`            | Every hour       |
| `15 * * * *`            | Every hour at minute 15       |
| `15 6 * * *`            | Every day at 6:15       |
| `15 6 3 * *`            | At 6:15 on day 3 of the month      |
| `15 6 3 11 *`            | At 6:15 on day 3 of the month, in November |
| `15 6 * 11 5`            | At 6:15 on every Friday, in November |

Advanced examples:

| Cron expression        | Meaning          |
| ---------------------- | ---------------- |
| `0,27,53 * * * *`        | At minutes 0, 27 and 53 every hour |
| `0 */3 * * *`            | Every three hours                  |
| `0 0 1-10 * *`             | At 00:00 AM, between day 1 and 10 of the month       |
| `0 0 1-10,20-30 * *`             | At 00:00 AM, on day 1 through 10 and 20 through 30 of the month |

{% endblock %}
