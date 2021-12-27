from flask import Flask, render_template, request, Response, send_file
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64

import uuid
import main
import my_AO3 as AO3
import time

from heapdict import heapdict
from datetime import datetime, timedelta

import csv, os, sys
import timeit
import json

app = Flask(__name__)

def convert_to_json(heapd):
    ret = []
    for key in heapd:
        pair = {"name": key, "value": heapd[key]}
        ret.append(pair)
    #j_ret = json.dumps(ret)
    #return j_ret[1:-1]
    return ret

def add_to_heapd(item, heapd):
    if item in heapd:
        #heapd[item] -= 1
        heapd[item] += 1
    else:
        #heapd[item] = -1
        heapd[item] = 1

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

@app.route('/')
def index():
  return render_template('index.html')

def decrypt(enc):
    private_key = """-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQCxbTIZN2KtvkIH+BLndOJkd3yIqpuQuYlP7PmQxIHGHhNkksCh
xRdL9rylpSibv8aVjeXd6QETccN+9XHb95aswOEuoCGUt98CH+kyP0P/G47VKear
3+Rr5kJzDS3SuBT8o2fY90kTvK/g9pCDHOWE2JSTj0CEDH5rMS0Z4Cbb6QIDAQAB
AoGBAI/Fvlz0pn/HtlYizZ7E9lcXA9Dy/tBNqFkd3DVVJxvVbz2GNZZg0Tn7HG7V
4Iwk4NR7gZNKplaNTy9n0PXAMVU8gvmuNrxNKAwrUFEl8Jviw+DI0vBFeF64zL/k
7kH4PqqR7htFx+ObAOwqOnZyNyw0kj5S/iJpBdSPgmb5hY4hAkEA6vcv/s985Er+
2jhsCI3hPLfFGayhWkuVmcp4Kp3uaGqUqR/VLeo1DDuxPgUKyZUtWcjbZfSaDL1F
/n+5IQsibQJBAMFPXDXlyFOXSMwYPYLqcJMmJCR0f9oeDoyB40GX93wjD3+a0Pz7
wLN/dfrJJobxmMHRic0MX1rBb8F3hTqR0e0CQGMke+7zk8osTs67QfJ2E1TwYc1M
hyS3gd9LjFrHGuKaHjIiiWv/R/TqdwYpUHzwYhthYhnqFNpNPux87hugPB0CQQCb
IshazNzXENswR+fdj63mub5Zr1EHyAVfB8JM2tuXuT9v5dwAmz3MD+er6xBLTcqN
CU9wypQf7ot0lSnLlkkFAkAIOU9aGV6xqu1En4ATyDtH+mg64XKUtC0ZJWcYvVwz
qGajydJv2ts5jmnzFScX7+coaMXGDkUx0rCKPksO3bRF
-----END RSA PRIVATE KEY-----"""

    rsa = RSA.importKey(private_key)
    cipher = PKCS1_v1_5.new(rsa)

    encStr = enc + "=" * ((4 - len(enc) % 4) % 4)

    ciphertext = base64.b64decode(encStr)
    plaintext = cipher.decrypt(ciphertext, b'DECRYPTION FAILED')
    return plaintext.decode('utf8')

def get_total_pages(username, password):
    #return "2"
    try:
        session = AO3.Session(username, password)
        return str(session._history_pages)
    except Exception as e:
        print(e)
        return "Error logging in. Make sure your username and password are correct."

def process(username, password, page):
    try:
        session = AO3.Session(username, password)

        endDate = datetime.now() - timedelta(days=365)

        #read 1 page
        history = session.get_history(hist_sleep=3, start_page=int(page), max_pages=int(page)+1, timeout_sleep=60)

        num_words = 0
        most_visited = dict()
        relationships = dict()
        fandoms = dict()
        tags = dict()
        authors = dict()

        #stats in the past year
        num_words_year = 0
        most_visited_year = dict()
        relationships_year = dict()
        fandoms_year = dict()
        tags_year = dict()
        authors_year = dict()
 
        for item in history:
            # if isinstance(item, str):
            #   yield item
            #   continue
            # if (num_years != 0 and item[2] < endDate):
            #     break

            num_words += add_helper(item, most_visited, relationships, fandoms, tags, authors)
            # only add if last visited date is past the prev year
            if (item[2] > endDate):
                num_words_year += add_helper(item, most_visited_year, relationships_year, fandoms_year, tags_year, authors_year)

        ret = {
            "totalwords": num_words,
            "mostvisited": convert_to_json(most_visited),
            "relationships": convert_to_json(relationships),
            "fandoms": convert_to_json(fandoms),
            "tags": convert_to_json(tags),
            "authors": convert_to_json(authors),

            "totalwords_year": num_words_year,
            "mostvisited_year": convert_to_json(most_visited_year),
            "relationships_year": convert_to_json(relationships_year),
            "fandoms_year": convert_to_json(fandoms_year),
            "tags_year": convert_to_json(tags_year),
            "authors_year": convert_to_json(authors_year),
        }

        #print(ret)

        return ret
    except Exception as e:
        print(e)
        return str(e)

def add_helper(item, most_visited, relationships, fandoms, tags, authors):
    data = item[3]

    #num_words += data["Words"]
    most_visited[data["Title"]] = item[1]
    
    for ship in data["Relationships"]:
        add_to_heapd(ship, relationships)

    for fandom in data["Fandoms"]:
        add_to_heapd(fandom, fandoms)

    for tag in data["Tags"]:
        add_to_heapd(tag, tags)

    for author in data["Authors"]:
        add_to_heapd(author, authors)

    return data["Words"]

@app.route('/apicall', methods=['post', 'get'])
def api_call():
    if request.method == 'POST':
        username = request.form.get('username')  # access the data inside 
        enc_password = request.form.get('password')
        #num_years = int(request.form.get('years'))
        page = request.form.get('page')

        password = decrypt(enc_password)

        if page == "-1":
            #return get_total_pages(username, password)
            #val = 'kI3i8buptEVmZevcnU20ALa+xi9Z02fhMBAlVd0PQBjv1QHgrjPc1GV46BSEHzsrSgoenC0L5gH+Ef/snA8Io5ebH9oEwUK02tOvhB7ceO0aVnAAcouuROx/xuXxjuMVnAadGLW+sT45vQuBY9ZS52OZo1RcNppOiHoGrpB4jzk='
            return get_total_pages(username, password)

        return process_wrapper(username, password, page)
        #return "abc"


def process_wrapper(username, password, page):
    ret = process(username, password, page)
    if ret == "Error logging in. Make sure your username and password are correct.":
        time.sleep(60)
        return process_wrapper(username, password, page)
    return ret

# @app.route('/login/', methods=['post', 'get'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')  # access the data inside 
#         password = request.form.get('password')
#         global num_years
#         num_years = int(request.form.get('years'))


#     try:
#         global session
#         session = AO3.Session(username, password)
#     except Exception as e:
#         print(e)
#         #x = input("Error logging in. Make sure your username and password are correct.")
#         print("Error logging in. Make sure your username and password are correct.")
#         return

#     #main.main(session, num_years)

#     #return render_template('index.html', output=output)
#     #return main.main(username, password, num_years)
#     #search()
#     return render_template('progress.html')
#     #return send_file('templates/progress.html', session=session, num_years=num_years)


@app.route('/download/<filename>')
def sendfile(filename):
  path1=sys.path[0]+"/" + filename
  return send_file(path1,as_attachment=True)

@app.route('/download1')
def sendfile1():
  path=sys.path[0]+"/stats.csv"
  return send_file(path,as_attachment=True)

@app.route('/download2')
def sendfile2():
  path=sys.path[0]+"/top_data.csv"
  return send_file(path,as_attachment=True)

@app.route('/download3')
def sendfile3():
  path=sys.path[0]+"/top_5_data.csv"
  return send_file(path,as_attachment=True)


# @app.route('/debugtext')
# def debugtext():
#   def generate():           
#       start = timeit.default_timer()
#       uid = str(uuid.uuid4())
#       num_words = 0
#       most_visited = heapdict()
#       relationships = heapdict()
#       fandoms = heapdict()
#       tags = heapdict()
#       authors = heapdict()

#       endDate = datetime.now() - timedelta(days=num_years*365)

#       yield "data:Fetching history...\n\n"
      
#       history = session.get_history(hist_sleep=3, start_page=0, max_pages=3, timeout_sleep=60)
#       #history = session.get_history()

#       for x in history:
#         for item in x:
#           if isinstance(item, str):
#             yield item
#             continue
#           if (num_years != 0 and item[2] < endDate):
#               break

#           data = item[3]

#           num_words += data["Words"]
#           most_visited[data["Title"]] = -item[1]
          
#           for ship in data["Relationships"]:
#               add_to_heapd(ship, relationships)

#           for fandom in data["Fandoms"]:
#               add_to_heapd(fandom, fandoms)

#           for tag in data["Tags"]:
#               add_to_heapd(tag, tags)

#           for author in data["Authors"]:
#               add_to_heapd(author, authors)

#       yield "data:Finished compiling data!\n\n"
#       yield "data:Writing to file...\n\n"

#       statspath = 'stats' + uid + '.csv'
#       if os.path.exists(statspath):
#           os.remove(statspath)
#       toppath = 'top_data' + uid + '.csv'
#       if os.path.exists(toppath):
#           os.remove(toppath)
#       top_five_path = 'top_5_data'  + uid + '.csv'
#       if os.path.exists(top_five_path):
#           os.remove(top_five_path)

#       with open(statspath, 'w', newline='') as f:
#           writer = csv.writer(f)
#           writer.writerow(["Words", num_words])
#           writer.writerow(["Works", len(most_visited)])
#           writer.writerow(["Relationships", len(relationships)])
#           writer.writerow(["Fandoms", len(fandoms)]) 

#       headers = ["Top fics", "", "Top ships", "", "Top fandoms", "", "Top tags", "", "Top authors", ""]
#       row_data = [most_visited, relationships, fandoms, tags, authors]
#       output_rows = get_output_rows(row_data)

#       with open(toppath, 'w', encoding='UTF-8', newline='') as f:
#           writer = csv.writer(f)
          
#           writer.writerow(headers)
#           writer.writerows(output_rows)

#       with open(top_five_path, 'w', encoding='UTF-8', newline='') as f:
#           writer = csv.writer(f)
          
#           writer.writerow(headers)
#           writer.writerows(output_rows[:5])

#       yield "data:Total runtime: " + str((timeit.default_timer() - start)/60)+ " mins\n\n"
#       yield 'data:<a href="/download/' +   statspath +  '>Overall stats</a><br>\n\n'
#       yield 'data:<a href="/download/' + toppath + '>All data</a><br>\n\n'
#       yield 'data:<a href="/download/' + top_five_path + '>Top 5 data</a><br>\n\n'
#       yield "data:Done!\n\n"

#   return Response(generate(), mimetype= 'text/event-stream')
    
# '''@app.route('/debugtext')
# def debugtext():
#   def generate():
#         x = 0
#         while x < 100:
#             x = x + 10
#             time.sleep(0.2)
#             yield "data:" + str(x) + "\n\n"
#   return Response(generate(), mimetype= 'text/event-stream')'''

if __name__ == '__main__':
  app.run(debug=True)
