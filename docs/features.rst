Features
===============

Philosophy
----------

Trax was designed from the ground-up to be a simple time tracker, integrated within a chat server, such as Mattermost.

Because of that philosophy, at the moment, the only available interface to trax is the chat server, via the slash command. The only exception is the trax admin interface, which is only here for configuration and management purposes.

This may evolve in the future.


Timers
------

Time tracking is provided using timers, a timer has basically a name, a start date and an end date.

Users can create, start and stop their own timers to track their time, and can use built-in reporting to
see the time they spend on each timer, per day.

Reminders
---------

Trax also offers in-chat reminders : once you set up a reminder, it will be send directly in-chat when the time comes.

This is useful to remember a meeting, or to remind your coworker something important needs to be done when you're not here.

Trax allow recurring reminders too, using the crontab syntax.

Human dates and time
------------------------

One of the pain with time-related software is how different human and computers handles dates.

While we want to use shorter, easier to type date or time references, such as "tomorrow" or "in ten minutes", machines need a precise date, such as "2017-09-01 12:37".

Trax supports human-like date and times when needed as well as more explicit ones, so you can focus on doing things instead of on trax.
