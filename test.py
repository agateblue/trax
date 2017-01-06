"""
Reminder

Usage:
  remind add <message> <when>

Mandatory arguments:
  <message>           The message that will be sent when the reminder is triggered
  <when>              When to set the reminder. It can either be:

                        * A relative hint, such as "in two hours" or "tomorrow at noon"
                        * An absolute date/time, such as "2017-01-10 17:15"

Note that it you provide multiple words for these arguments,
you have to enclose them using double quotes:

    * GOOD: remind add something tomorrow
    * GOOD: remind add "something important" tomorrow
    * GOOD: remind add "something important" "tomorrow at noon"
    * BAD: remind add something tomorrow at noon
    * BAD: remind add something important "tomorrow at noon"
"""

import docopt
import sys
arguments = docopt.docopt(__doc__, sys.argv[1:])
print(arguments, sys.argv[1:])
