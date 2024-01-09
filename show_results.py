#!/usr/bin/env python
" spit out a list of players in 'A sends to A+1' order "
# TODO: what if someone signs up forging someone else's name ?
from collections import defaultdict
import sqlite3

# sqlite3 -box ss2024.db "select tstamp, name, country from signups;"

# where's the beef
DBFILE = "ss2024.db"
# salted hash for the pseudo-random sorting
SALT = "ss2024"
# extra flag on the n-to-n+1 match
SHIPTYPES = ["Heart", "Diamond", "Spade"]


# hello database please talk nicely to me
CONN = sqlite3.connect(DBFILE)
CONN.row_factory = sqlite3.Row


def check_for_dupes():
    " did people sign-up more than once? "
    cur = CONN.cursor()
    sql = "SELECT remote_addr, LOWER(name) as name FROM signups ORDER BY name;"
    culprits = defaultdict(list)
    for row in cur.execute(sql):
        culprits[row["name"]].append(row["remote_addr"])
    cur.close()
    found = False
    for name in culprits:
        if len(culprits[name]) > 1:
            print(
                f"""WARN {name} signed up more than once: {culprits[name]}""")
    if found:
        print("---")

# I want random sort, but the same order each time I run this on the same data!


def uniquify_signups():
    " give me list of participants but only their most recent sign-ups "
    # TODO: need a better way to keep only the best data of multiple submissions
    signups = defaultdict(dict)
    cur = CONN.cursor()
    sql = "SELECT * FROM signups ORDER BY tstamp ASC;"
    for row in cur.execute(sql):
        name = row["name"].lower()
        for field in row.keys():
            signups[name][field] = row[field]
    cur.close()
    return [signups[i] for i in signups]


def spew_results(participants):
    " human-friendly spew of n-sends-to-n+1 "
    def _sortkey(i):
        " random but reliably so and hope to keep in same country if needed "
        return f"""{i["country"]}.{i["foreignokay"]}.{hash(i["name"].lower() + SALT)}"""
    participants.sort(key=_sortkey)
    i = 0
    k = len(participants)
    for j in range(k):
        thisone = participants[j]
        if j+1 < k:
            thatone = participants[j+1]
        else:
            thatone = participants[0]
        i = (i+1) % 3
        print(f"""Name: {thisone["name"]} <{thisone["email"]}> """)
        print(
            f"""Country: ({thisone["country"]}, foreignokay {thisone["foreignokay"]})""")
        print("")
        print(f"""Sends_to: {thatone["name"]} ({thatone["country"]})""")
        print(f"""Moon: {thatone["moon"]}""")
        print(f"""Quadrant: {SHIPTYPES[i]}""")
        print("Address: " + thatone["address"].replace("%0A", "\n         "))
        print("Info: " + thatone["intro"].replace("%0A", "\n      "))
        print("---")


# main()
check_for_dupes()
PEEPS = uniquify_signups()
spew_results(PEEPS)
