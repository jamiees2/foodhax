# Foodhax
Semi-automated food booking system for the cafeteria in B27

Tired of having to manually book things at the same time every day, scripting to the rescue!

<p align="center"><img src="/img/food.gif?raw=true"/></p>

## food.py
```
usage: ./food.py [-h] [-c] [-m] [-n] [-e] [-d] [-p]

optional arguments:
  -h, --help            show this help message and exit
  -c, --clear-config    Clear out the food.json saved config file
  -m, --skip-config     Skip using the food.json saved config file
  -n, --note            Prompt for a note
  -e, --no-email-from-env
                        Prompt for the email even though it is in the
                        environment
  -d, --dry-run         Don't actually submitt the form
  -p, --no-confirm      Don't confirm before submitting the form
```

## Cron
If you like a fixed schedule and to save even more time, use cron!

After running once and saving the config, you can have this auto run by adding
```
30 14 * * 0-4 /Users/<your username>/<path to foodhax>/food.py -p
```
to crontab.

This will automatically book food at 14:30 the day before (so Sunday-Thursday)
