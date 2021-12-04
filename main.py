import my_AO3 as AO3

import time
from heapdict import heapdict
from datetime import datetime, timedelta
from getpass import getpass

import csv, os
import timeit

def main():
    username = input("Username: ")
    password = getpass("Password: ")
    #password = "b/6&vMqZ#$7JmAF"

    try:
        session = AO3.Session(username, password)
    except:
        x = input("Error logging in. Make sure your username and password are correct.")
        return

    num_years = int(input("Number of years to analyze (put zero for entire history): "))

    start = timeit.default_timer()

    num_words = 0
    most_visited = heapdict()
    relationships = heapdict()
    fandoms = heapdict()
    tags = heapdict()
    authors = heapdict()

    lastyear = datetime.now() - timedelta(days=3*365)
    endDate = datetime.now() - timedelta(days=num_years*365)

    print("Fetching history...")
    history = session.get_history(hist_sleep=3, start_page=0, max_pages=0, timeout_sleep=60)
    #history = session.get_history()
    print("Analyzing works...")
    for item in history:
        if (num_years != 0 and item[2] < endDate):
            break

        data = item[3]

        num_words += data["Words"]
        most_visited[data["Title"]] = -item[1]
        
        for ship in data["Relationships"]:
            add_to_heapd(ship, relationships)

        for fandom in data["Fandoms"]:
            add_to_heapd(fandom, fandoms)

        for tag in data["Tags"]:
            add_to_heapd(tag, tags)

        for author in data["Authors"]:
            add_to_heapd(author, authors)

        '''work = item[0]

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
            continue'''

    print("Finished compiling data!")
    print("Writing to file...")

    statspath = 'stats.csv'
    if os.path.exists(statspath):
        os.remove(statspath)
    toppath = 'top_data.csv'
    if os.path.exists(toppath):
        os.remove(toppath)
    top_five_path = 'top_5_data.csv'
    if os.path.exists(top_five_path):
        os.remove(top_five_path)

    with open(statspath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Words", num_words])
        writer.writerow(["Works", len(most_visited)])
        writer.writerow(["Relationships", len(relationships)])
        writer.writerow(["Fandoms", len(fandoms)])


    headers = ["Top fics", "", "Top ships", "", "Top fandoms", "", "Top tags", "", "Top authors", ""]
    row_data = [most_visited, relationships, fandoms, tags, authors]
    output_rows = get_output_rows(row_data)

    with open(toppath, 'w', encoding='UTF-8', newline='') as f:
        writer = csv.writer(f)
        
        writer.writerow(headers)
        writer.writerows(output_rows)

    with open(top_five_path, 'w', encoding='UTF-8', newline='') as f:
        writer = csv.writer(f)
        
        writer.writerow(headers)
        writer.writerows(output_rows[:5])

    print("Done! Total runtime:", (timeit.default_timer() - start)/60, "mins")
    x = input("Press enter to exit.")

    '''print()
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
    print_arr("Top authors: ", top_5(authors))'''

def get_output_rows(row_data):
    output = []
    longest = 0

    for heapd in row_data:
        longest = max(longest, len(heapd))

    for x in range(longest):
        element = []

        for heapd in row_data:
            if heapd:
                el = heapd.popitem()
                element.append(el[0])
                element.append(-el[1])
            else:
                element.append("")
                element.append("")
        
        output.append(element)
    
    return output


def get_element(heapd):
    if heapd:
        return heapd.popitem()
    return ""

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
    if arr is None:
        return
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