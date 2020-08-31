#!/usr/bin/env python3
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import json
import os
import sys
import argparse

EMAIL_FIELD = "Field9"

TIME_FIELD = "Field6"

NOTE_FIELD = "Field12"

CLICKORENTER = "clickOrEnter"

URL = "https://kpmg.wufoo.com/forms/ag-er-a-mat-a-b27/"

CONF_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "food.json")

def load_config():
    conf = {}
    if os.path.exists(CONF_PATH):
        with open(CONF_PATH, "r") as f:
            conf = json.load(f)
    return conf

def write_config(time, email, note):
    conf = {
        "time": time,
        "email": email,
        "note": note
    }
    with open(CONF_PATH, "w") as f:
        json.dump(conf, f)

def delete_config():
    if os.path.exists(CONF_PATH):
        os.remove(CONF_PATH)

def get_formdata(session, ua):

    page = session.get(URL, headers={'User-Agent': ua})

    if page.status_code != 200:
        print("An error occured while loading the form. You'll likely need to try again.")
        raise RuntimeError("Failed to load food form")

    soup = BeautifulSoup(page.content, 'html.parser')
    form = soup.find("form", class_="wufoo")

    inputs = form.find_all("input")

    input_values = {
        inp["name"]: inp["value"] for inp in inputs
    }

    choices = [inp["value"] for inp in inputs if inp["name"] == TIME_FIELD and inp["value"]]

    return input_values, choices



def prompt_data(conf, choices, prompt_note, no_email_from_env):
    if "time" in conf and conf["time"] in choices:
        time = conf["time"]
    else:
        print("Choose a time")
        for i, s in enumerate(choices):
            print("%d: %s" % (i + 1, s))
        while True:
            try:
                s = input("Choose a time slot: ")
                time = choices[int(s) - 1]
                break
            except ValueError:
                print("Please enter a valid choice")
                continue

    if "email" in conf:
        email = conf["email"]
    elif not no_email_from_env and os.getenv("ASANA_GIT_EMAIL", None) is not None:
        email = os.getenv("ASANA_GIT_EMAIL")
    else:
        email = input("Enter email: ")


    if "note" in conf and conf["note"]:
        note = conf["note"]
    elif prompt_note:
        note = input("Enter note (optional): ")
    else:
        note = ""

    return time, email, note

def confirm_values():
    if not input("Does this look correct? (y/n): ").lower().startswith("y"):
        print("Aborted registration")
        sys.exit(1)


def post_form(session, ua, input_values):
    response = session.post(URL, headers={"User-Agent": ua, "Referer": URL}, data=input_values)
    if response.status_code == 200 or response.status_code == 302:
        print("Success! You are registered for lunch at", input_values[TIME_FIELD])
    else:
        print("An error occured when submitting the form. You'll likely need to try again")
        raise RuntimeError("Failed to submit food form")


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--clear-config", help="Clear out the food.json saved config file", action="store_true")
    parser.add_argument("-m", "--skip-config", help="Skip using the food.json saved config file", action="store_true")
    parser.add_argument("-n", "--note", help="Prompt for a note", action="store_true")
    parser.add_argument("-e", "--no-email-from-env", help="Prompt for the email even though it is in the environment", action="store_true")
    parser.add_argument("-d", "--dry-run", help="Don't actually submitt the form", action="store_true")
    parser.add_argument("-p", "--no-confirm", help="Don't confirm before submitting the form", action="store_true")

    args = parser.parse_args(argv)

    if not args.skip_config and not args.clear_config:
        conf = load_config()
    else:
        conf = {}

    ua = UserAgent().random

    session = requests.Session()

    input_values, choices = get_formdata(session, ua)

    time, email, note = prompt_data(conf, choices, args.note, args.no_email_from_env)

    if not args.skip_config:
        write_config(time, email, note)
    elif args.clear_config:
        delete_config()

    print("Registering for lunch with the following values:")
    print("Time:", time)
    print("Email:", email)
    print("Note:", note)
    if not args.no_confirm:
        confirm_values()

    if not args.dry_run:
        input_values[EMAIL_FIELD] = email
        input_values[TIME_FIELD] = time
        if note:
            input_values[NOTE_FIELD] = note

        input_values[CLICKORENTER] = "click"

        post_form(session, ua, input_values)



if __name__ == "__main__":
    argv = sys.argv[1:]
    main(argv)
