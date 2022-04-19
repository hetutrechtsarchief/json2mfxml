#!/usr/bin/env python3
import json,csv,sys,re,datetime,os,uuid
from sys import argv
from liquid import Liquid

def generateGUID():
  return uuid.uuid4().hex.upper()

def getDateString():
  return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

tpl = {}
username = "MFRCOMPA"

caller_dir = os.getcwd()
script_dir = os.path.dirname(os.path.realpath(__file__))

if len(argv)!=3:
  print(f"Usage: {argv[0]} input.json output.xml")
  sys.exit()

inputfilename = argv[1] #"items2.json"
outputfilename = argv[2] #"Hardenbroek.xml"

#load template files
soorten = [ "abk","db","eb","hsk","inl","inv","lst","pgf","rub","vb","audit" ]
for soort in soorten:
  os.chdir(script_dir)
  tpl[soort] = Liquid("templates/"+soort+".xml", liquid_from_file=True) 


#----------------------------

with open(inputfilename) as json_file:
  items = json.load(json_file)

  #open output file
  with open(outputfilename, 'w') as outfile: # let op: moet UTF8 mét BOM zijn.
    outfile.write(u'\ufeff') # write UTF8 BOM signature
    print(u"Writing to " + outputfilename)

    for item in items:
      
      nummer = ""
      code = ""
      if "code" in item:
        if item["code"].isnumeric():
          nummer = item["code"]
        else:
          code = item["code"]


      data = {
        "ID": item["index"],
        "ParentID": item["parentIndex"],
        "Text": item["text"],
        "InventarisTitel": item["inventarisTitel"] if "inventarisTitel" in item else "",  # only in use at Top
        "InventarisAuteur": item["inventarisAuteur"] if "inventarisAuteur" in item else "",  # only in use at Top
        "GUID": generateGUID(),
        "UserCreated": username,
        "DateCreated": getDateString(),
        "UserMutated": username,
        "DateMutated": getDateString(),
        "VoorlopigNummer": "",
        "Volgnummer": item["index"],
        "Nummer": nummer,
        "Beginjaar": "",
        "Eindjaar": "",
        "Datering": "",
        "Aantal": "",
        "UiterlijkeVorm": "",
        "Orde": "",
        "Notabene": item["Notabene"] if "Notabene" in item else "",
        "Code": code,
        "TopID": items[0]["index"]
      }

      # check for known aet
      if not item["aet"] in soorten:
        print("unknown aet",item)
        sys.exit()

      # print result to file
      os.chdir(script_dir)
      result = tpl[item["aet"]].render(**data)
      result = re.sub(r"^#.*", "", result, flags=re.M) # strip comments '#' created by Liquid (use multi line mode)
      result = os.linesep.join([s for s in result.splitlines() if s]) # strip empty lines
      
      os.chdir(caller_dir)
      print(result, file=outfile)
     
      # if items.index(item)>20:
      #   sys.exit()

