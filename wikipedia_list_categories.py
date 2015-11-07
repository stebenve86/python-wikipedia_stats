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
import json

### Argument parser ###
parser = argparse.ArgumentParser(description="List Wikipedia categories for a given language")
parser.add_argument("-l", "--language", default="en", help="the Wikipedia language (default: %(default)s)")
parser.add_argument("-p", "--prefix", help="the prefix for the categories to be retrieved")
parser.add_argument("-f", "--from", dest="from_category", help="the starting category to be retrieved")

args = parser.parse_args()

### Query to Wikipedia API ###
api_url = "http://" + args.language + ".wikipedia.org/w/api.php"
api_params = { "action" : "query",
               "list" : "allcategories",
               "continue" : "",
               "aclimit" : 500,
               "format" : "json" 
             }
if args.prefix:
  api_params["acprefix"] = args.prefix
if args.from_category:
  api_params["continue"] = "-||"
  api_params["accontinue"] = args.from_category
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
  print("Error querying Wikipedia API for language \"" + args.language + "\"") 
  print("")
  sys.exit(1)
print("done.")
print("")

parsed_response = json.loads(response_content)

### Get categories ###
categories = parsed_response["query"]["allcategories"]
print(str(len(categories)) + " categories found for language \"" + args.language + "\":")
# print the list of categories found
counter = 1
for category in categories:
  print(str(counter) + " | " + category["*"].encode("utf-8"))
  counter += 1
print("")
print("")
try:
  parsed_response["continue"]
  print("More than 500 results found.")
  print("")
  print("In order to retrieve the next set of categories, run again the script with the following \"-f\" option:")
  print(parsed_response["continue"]["accontinue"].encode("utf-8"))
  print("")
  print("")
except:
  pass
