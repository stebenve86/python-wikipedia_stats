#!/usr/bin/python

"""
Copyright 2015 Stefano Benvenuti <ste.benve86@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
import os
import argparse
import urllib
import urllib2
import json
import re
import time

### Argument parser ###
parser = argparse.ArgumentParser(description="Get Wikipedia articles for a given category")
parser.add_argument("category", help="the Wikipedia category")
parser.add_argument("-l", "--language", default="en", help="the Wikipedia language (default: %(default)s)")
parser.add_argument("-d", "--days", choices=["30", "60", "90"], default="30", help="time range for stats (days) (default: %(default)s)")
parser.add_argument("-o", "--output_folder", default="output", help="the output folder (default: %(default)s)")
parser.add_argument("--no-stats", dest="no_stats", action="store_true", help="no stats queries are sent")

args = parser.parse_args()

# check if output folder exists
if not os.path.isdir(args.output_folder):
  print("")
  print("ERROR: Missing output folder")
  print("")
  sys.exit(1)

### Query to Wikipedia API ###
api_url = "http://" + args.language + ".wikipedia.org/w/api.php"
api_params = { "action" : "query",
               "list" : "categorymembers",
               "continue" : "",
               "cmtitle" : "Category:" + args.category,
               "cmlimit" : 500,
               "cmprop": "title",
               "format" : "json" 
             }
try:
  params = urllib.urlencode(api_params)
  req = urllib2.Request(api_url, params)
  req.add_header("User-Agent", "python-wikipedia_stats")
  print("")
  sys.stdout.write("Querying " + args.language + ".wikipedia.org... ")
  response = urllib2.urlopen(req)
  response_content = response.read()
except Exception:
  print("")
  print("")
  print("Error querying Wikipedia API for category \"" + args.category + "\"") 
  print("")
  sys.exit(1)
print("done.")

parsed_response = json.loads(response_content)

### Get stats ###
articles = parsed_response["query"]["categorymembers"]
num_articles = len(articles)
print("")
# exit if no articles have been found
if num_articles == 0:
  print("No articles found for category \"" + args.category + "\"") 
  print("")
  sys.exit(1)
print(str(num_articles) + " articles found for category \"" + args.category + "\":")
print("")
# print the list of articles found
counter = 1
for article in articles:
  print(str(counter) + " | " + article["title"])
  counter += 1
print("")
print("")

if args.no_stats:
  sys.exit(1)

# query the stats url for each article, save the values in a dictionary
all_hits = {}
stats_url_base = "http://stats.grok.se/" + args.language + "/latest" + args.days + "/"
for article in articles:
  title = article["title"].encode("utf-8")
  urltitle = urllib.quote(title).replace("%20", "_").replace("%2F", "/")
  stats_url = stats_url_base + urltitle
  try:
    req = urllib2.Request(stats_url)
    req.add_header("User-Agent", "python-wikipedia_stats")
    print("Querying stats.grok.se for " + title)
    response = urllib2.urlopen(req)
    response_content = response.read()
  except Exception:
    print("EXCEPTION getting stats for: " + title)
    continue
  # find the number of hits for the given article
  regex_sentence = re.compile("has been viewed (\d+)")
  match_sentence = regex_sentence.search(response_content)
  num_hits = int(match_sentence.group(1))
  if num_hits not in all_hits:
    all_hits[num_hits] = []
  all_hits[num_hits].append([title, urltitle])
  time.sleep(2)

### Print output file sorted by the number of hits ###
category_file = urllib.quote(args.category).replace("%20", "_").replace("%2F", "/")
output_file_name = category_file + "_" + args.language + "_" + args.days + "_" + time.strftime("%Y%m%d%H%M%S") + ".csv"
output_file_path = os.path.join(args.output_folder, output_file_name)
try:
  output_file = open(output_file_path, "w")
  output_file.write("Title|URL|Hits_" + args.days + "\n")
  for key in sorted(all_hits, reverse=True):
    for article in all_hits[key]:
      output_file.write(article[0] + "|" + "http://" + args.language + ".wikipedia.org/wiki/" + article[1] + "|" + str(key) + "\n")
except Exception:
  print("")
  print("EXCEPTION writing output file for article: " + article[0])
  print("")
finally:
  output_file.close()
print("")
print("Output file: " + output_file_path)
print("")
