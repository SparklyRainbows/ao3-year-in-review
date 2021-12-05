from flask import Flask, render_template, request, Response, send_file
import main
import my_AO3 as AO3
import time

from heapdict import heapdict
from datetime import datetime, timedelta

import csv, os, sys
import timeit

app = Flask(__name__)


def add_to_heapd(item, heapd):
    if item in heapd:
        heapd[item] -= 1
    else:
        heapd[item] = -1

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

@app.route('/login/', methods=['post', 'get'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')  # access the data inside 
        password = request.form.get('password')
        global num_years
        num_years = int(request.form.get('years'))


    try:
        global session
        session = AO3.Session(username, password)
    except Exception as e:
        print(e)
        #x = input("Error logging in. Make sure your username and password are correct.")
        print("Error logging in. Make sure your username and password are correct.")
        return

    #main.main(session, num_years)

    #return render_template('index.html', output=output)
    #return main.main(username, password, num_years)
    #search()
    return render_template('progress.html')
    #return send_file('templates/progress.html', session=session, num_years=num_years)

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


@app.route('/debugtext')
def debugtext():
  def generate():           
      start = timeit.default_timer()

      num_words = 0
      most_visited = heapdict()
      relationships = heapdict()
      fandoms = heapdict()
      tags = heapdict()
      authors = heapdict()

      endDate = datetime.now() - timedelta(days=num_years*365)

      yield "data:Fetching history...\n\n"
      
      #history = session.get_history(hist_sleep=3, start_page=0, max_pages=0, timeout_sleep=60)
      history = session.get_history()

      for x in history:
        for item in x:
          if isinstance(item, str):
            yield item
            continue
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

      yield "data:Finished compiling data!\n\n"
      yield "data:Writing to file...\n\n"

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

      yield "data:Total runtime: " + str((timeit.default_timer() - start)/60)+ " mins\n\n"
      yield "data:Done!\n\n"

  return Response(generate(), mimetype= 'text/event-stream')
    
'''@app.route('/debugtext')
def debugtext():
  def generate():
        x = 0
        while x < 100:
            x = x + 10
            time.sleep(0.2)
            yield "data:" + str(x) + "\n\n"
  return Response(generate(), mimetype= 'text/event-stream')'''

if __name__ == '__main__':
  app.run(debug=True)
