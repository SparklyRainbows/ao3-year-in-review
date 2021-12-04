import AO3

import time
from heapdict import heapdict
from datetime import datetime, timedelta
from getpass import getpass

def main():
    username = input("Username: ")
    password = getpass("Password: ")
    #password = "b/6&vMqZ#$7JmAF"

    session = AO3.Session(username, password)

    print("Fetching history...")

    num_words = 0
    most_visited = heapdict()
    relationships = heapdict()
    fandoms = heapdict()
    tags = heapdict()
    authors = heapdict()

    lastyear = datetime.now() - timedelta(days=3*365)

    #history = session.get_history(hist_sleep=3, start_page=0, max_pages=0, timeout_sleep=60)
    history = session.get_history()
    print("Fetching works...")
    for item in history:
        if (item[2] < lastyear):
            break
        work = item[0]

        try:
            loaded = work.loaded
            while loaded == False:
                try:
                    work.reload()
                    loaded = True

                except AO3.utils.HTTPError:
                    print(f"Rate limited, sleeping for 60 seconds")
                    time.sleep(60)

            print(work.title)

            num_words += work.words
            most_visited[work.title] = -item[1]
            
            for ship in work.relationships:
                add_to_heapd(ship, relationships)

            for fandom in work.fandoms:
                add_to_heapd(fandom, fandoms)

            for tag in work.tags:
                add_to_heapd(tag, tags)

            for author in work.authors:
                add_to_heapd(author.username, authors)

            time.sleep(3)
        except:
            print("Error fetching", work)
            continue

    print()
    print("===STATS===")

    print("Words:", num_words)
    print("Works:", len(most_visited))
    print("Relationships:", len(relationships))
    print("Fandoms:", len(fandoms))

    print()
    print("===TOP===")

    print_arr("Top fics: ", top_5(most_visited))
    print_arr("Top ships: ", top_5(relationships))
    print_arr("Top fandoms: ", top_5(fandoms))
    print_arr("Top tags: ", top_5(tags))
    print_arr("Top authors: ", top_5(authors))

def add_to_heapd(item, heapd):
    if item in heapd:
        heapd[item] -= 1
    else:
        heapd[item] = -1

def top_5(heapd):
    top = []

    for x in range(5):
        if not heapd:
            return
        
        item = heapd.popitem()
        tup = (item[0], -item[1])
        top.append(tup)

    return top

def print_arr(text, arr):
    print(text)
    for x in arr:
        print(x)
    print()

def test():
    work = AO3.Work(21952651)
    work.reload()
    print(work.title)
    print(work.words)
    print(work.relationships)
    print(work.fandoms)
    print(work.tags)
    print(work.authors)

if __name__ == "__main__":
    main()
    #test()