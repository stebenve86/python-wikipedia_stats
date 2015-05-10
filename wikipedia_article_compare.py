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
import argparse
import urllib
import urllib2
import urlparse
import json
import re
import time

### Argument parser ###
parser = argparse.ArgumentParser(description="Compare Wikipedia articles for two languages")
parser.add_argument("title", help="the Wikipedia article title")
parser.add_argument("-l1", "--language1", default="en", help="the language of the argument article (default: %(default)s)")
parser.add_argument("-l2", "--language2", default="simple", help="the second language to be checked (default: %(default)s)")
parser.add_argument("-d", "--days", choices=["30", "60", "90"], default="30", help="time range for stats (days) (default: %(default)s)")

args = parser.parse_args()

### Query to Wikipedia API ###
api_url = "http://" + args.language1 + ".wikipedia.org/w/api.php"
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
  sys.stdout.write("Querying " + args.language1 + ".wikipedia.org... ")
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
  print("Article \"" + args.title + "\" not found for language \"" + args.language1 + "\"")
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
second_language = filter(lambda lang: lang["lang"] == args.language2, languages)
if len(second_language) == 0:
  print ("Article \"" + args.title + "\" not found for language \"" + args.language2 + "\"")
  print("")
  print(str(num_languages) + " other languages found for article \"" + args.title + "\":")
  # print the list of languages found
  counter = 1
  for language in languages:
    print(str(counter) + " | " + language["lang"] + " | " + language["*"] + " | " + language["url"])
    counter += 1
  print("")
  sys.exit(1)
print("")

# first language
first_urltitle = urllib.quote(args.title).replace("%20", "_").replace("%2F", "/")
stats_url = "http://stats.grok.se/" + args.language1 + "/latest" + args.days + "/" + first_urltitle
try:
  req = urllib2.Request(stats_url)
  req.add_header("User-Agent", "python-wikipedia_stats")
  print("Querying stats.grok.se for " + args.language1)
  response = urllib2.urlopen(req)
  response_content = response.read()
except Exception:
  print("EXCEPTION getting stats for: " + args.language1)
# find the number of hits for the given article
regex_sentence = re.compile("has been viewed (\d+)")
match_sentence = regex_sentence.search(response_content)
num_hits1 = match_sentence.group(1)
time.sleep(2)

# second language
second_urltitle = '/'.join(urlparse.urlparse(second_language[0]["url"]).path.split('/')[2:])
stats_url = "http://stats.grok.se/" + args.language2 + "/latest" + args.days + "/" + second_urltitle
try:
  req = urllib2.Request(stats_url)
  req.add_header("User-Agent", "python-wikipedia_stats")
  print("Querying stats.grok.se for " + args.language2)
  response = urllib2.urlopen(req)
  response_content = response.read()
except Exception:
  print("EXCEPTION getting stats for: " + args.language2)
# find the number of hits for the given article
regex_sentence = re.compile("has been viewed (\d+)")
match_sentence = regex_sentence.search(response_content)
num_hits2 = match_sentence.group(1)
print("")
print(args.language1 + " " + first_urltitle.encode("utf-8") + " " + num_hits1)
print(args.language2 + " " + second_urltitle.encode("utf-8") + " " + num_hits2)
print("")
