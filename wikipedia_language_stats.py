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
import urlparse
import json
import re
import time

### Argument parser ###
parser = argparse.ArgumentParser(description="Get Wikipedia articles for all the possible languages")
parser.add_argument("title", help="the Wikipedia article title")
parser.add_argument("-l", "--language", default="en", help="the language of the argument article (default: %(default)s)")
parser.add_argument("-d", "--days", choices=["30", "60", "90"], default="30", help="time range for stats (days) (default: %(default)s)")
parser.add_argument("-o", "--output_folder", default="output", help="the output folder (default: %(default)s)")

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
               "prop" : "langlinks",
               "continue" : "",
               "llprop" : "url",
               "lllimit" : 500,
               "titles" : args.title, 
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
  print("Error querying Wikipedia API for article \"" + args.title + "\"") 
  print("")
  sys.exit(1)
print("done.")
print("")

parsed_response = json.loads(response_content)

### Get stats ###
page_id = (parsed_response["query"]["pages"].keys())[0]
languages = {}
try:
  pageid = parsed_response["query"]["pages"][page_id]["pageid"]
except:
  print("Article " + args.title + " not found for language " + args.language)
  print("")
  sys.exit(1)
try:
  languages = parsed_response["query"]["pages"][page_id]["langlinks"]
  num_languages = len(languages)
except:
  num_languages = 0
# exit if no languages have been found
if num_languages == 0:
  print("No other languages found for article \"" + args.title + "\"") 
  print("")
  sys.exit(1)
print(str(num_languages) + " languages found for article \"" + args.title + "\":")
print("")
# print the list of languages found
counter = 1
for language in languages:
  print(str(counter) + " | " + language["lang"] + " | " + language["*"] + " | " + language["url"])
  counter += 1
print("")
print("")

all_hits = {}

# first language
first_urltitle = urllib.quote(args.title).replace("%20", "_").replace("%2F", "/")
stats_url = "http://stats.grok.se/" + args.language + "/latest" + args.days + "/" + first_urltitle
try:
  req = urllib2.Request(stats_url)
  req.add_header("User-Agent", "python-wikipedia_stats")
  print("Querying stats.grok.se for " + args.language)
  response = urllib2.urlopen(req)
  response_content = response.read()
except Exception:
  print("EXCEPTION getting stats for: " + args.language)
# find the number of hits for the given article
regex_sentence = re.compile("has been viewed (\d+)")
match_sentence = regex_sentence.search(response_content)
num_hits = int(match_sentence.group(1))
if num_hits not in all_hits:
  all_hits[num_hits] = []
all_hits[num_hits].append([args.language, first_urltitle])
time.sleep(2)

# query the stats url for each language, save the values in a dictionary
for language in languages:
  urltitle = '/'.join(urlparse.urlparse(language["url"]).path.split('/')[2:])
  stats_url = "http://stats.grok.se/" + language["lang"] + "/latest" + args.days + "/" + urltitle
  try:
    req = urllib2.Request(stats_url)
    req.add_header("User-Agent", "python-wikipedia_stats")
    print("Querying stats.grok.se for " + language["lang"])
    response = urllib2.urlopen(req)
    response_content = response.read()
  except Exception:
    print("EXCEPTION getting stats for: " + language["lang"])
    continue
  # find the number of hits for the given article
  regex_sentence = re.compile("has been viewed (\d+)")
  match_sentence = regex_sentence.search(response_content)
  num_hits = int(match_sentence.group(1))
  if num_hits not in all_hits:
    all_hits[num_hits] = []
  all_hits[num_hits].append([language["lang"], urltitle])
  time.sleep(2)

### Print output file sorted by the number of hits ###
output_file_name = first_urltitle + "_" + args.language + "_" + args.days + "_" + time.strftime("%Y%m%d%H%M%S") + ".csv"
output_file_path = os.path.join(args.output_folder, output_file_name)
try:
  output_file = open(output_file_path, "w")
  output_file.write("Language|URL|Hits_" + args.days + "\n")
  for key in sorted(all_hits, reverse=True):
    for article in all_hits[key]:
      output_file.write(article[0] + "|" + "http://" + article[0] + ".wikipedia.org/wiki/" + article[1] + "|" + str(key) + "\n")
except Exception:
  print("")
  print("EXCEPTION writing output file for article: " + article[0])
  print("")
finally:
  output_file.close()
print("")
print("Output file: " + output_file_path)
print("")
