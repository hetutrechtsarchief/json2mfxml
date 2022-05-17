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

if len(argv)!=4:
  print(f"Usage: {argv[0]} INPUT.json HEADER.mfxml OUTPUT.mfxml")
  sys.exit(1)

inputfilename = argv[1] #"items2.json"
header_template = argv[2] #"header_template.xml"
outputfilename = argv[3] #"Hardenbroek.mfxml"

with open(header_template) as infile:
  header = infile.read()
  header = header.replace('<MFEXPORT VERSION="31.0" ENCODING="UTF-8">\n','') # strip this tag..


# this is to replace references to id=1 to the id from the template
top_id = int(re.findall(r"<ID>(.*)</ID>", header)[0])


#load template files
soorten = [ "db","eb","hsk","inl","inv","lst","pgf","rub","vb","audit", "err" ] #err=error   "abk",
for soort in soorten:
  os.chdir(script_dir)
  tpl[soort] = Liquid("templates/"+soort+".xml", liquid_from_file=True) 


#----------------------------

os.chdir(caller_dir)
with open(inputfilename) as json_file:
  items = json.load(json_file)

  #open output file
  with open(outputfilename, 'w', encoding='utf-8') as outfile: # let op: moet UTF8 mét BOM zijn.
    # outfile.write(u'\ufeff') # write UTF8 BOM signature
    print(u"Writing to " + outputfilename)


    # print header
    print(header, file=outfile)


    for item in items:

      if item["aet"]=="abk":
        continue # skip because where using the ABK from the HEADER template

      
      if not "nummer" in item:
        item["nummer"] = ""


# print(top_id)

# sys.exit()

      # nummer = ""
      # code = ""
      # if "code" in item:
      #   if item["code"].isnumeric():
      #     nummer = item["code"]
      #   else:
      #     code = item["code"]

      if item["parentIndex"]==1:
        item["parentIndex"] = top_id




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
        "Nummer": item["nummer"],
        "Beginjaar": item["Beginjaar"] if "Beginjaar" in item else "",
        "Eindjaar": item["Eindjaar"] if "Eindjaar" in item else "",
        "Datering": item["Datering"] if "Datering" in item else "",
        "Aantal": item["Aantal"] if "Aantal" in item else "",
        "UiterlijkeVorm": item["UiterlijkeVorm"] if "UiterlijkeVorm" in item else "",
        "Orde": "",
        "Notabene": item["Notabene"] if "Notabene" in item else "",
        "Code": item["code"],
        "TopID": top_id   #items[0]["index"]
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

