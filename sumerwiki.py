import numpy as np
from bs4 import BeautifulSoup
import requests
import time

base_wiktionary_url = 'https://en.wiktionary.org/wiki/'
addon = '#Sumerian'

wikiURL = "https://en.wikipedia.org/wiki/List_of_cuneiform_signs"
wikireq = requests.get(wikiURL)
wikitext = wikireq.text

wikisoup = BeautifulSoup(wikitext, 'html.parser')

SIGNNAMELIST = []
CODELIST = []

DICT = {}
REVDICT = {}

BASEDIR = "public/data/"

def fetchWikiSourceData(sign):
	url = base_wiktionary_url + sign# + addon
	req = requests.get(url)
	text = req.text

	soup = BeautifulSoup(text, 'html.parser')
	for table in soup.find_all('table'):
		table.decompose()

	sumertext = soup.findAll('h2')
	
	result_text = ''

	result_html = ''

	for el in sumertext:
		if "Sumerian" in el.get_text():
			for sib in el.find_next_siblings():
				result_text += sib.get_text() + "\n"
				result_html += str(sib)

	result_text = result_text.replace('[edit]', '')

	#trim out the extras, no need for anything after the references and before the
	#descriptions of the etymologies
	if 'References' in result_text:
		result_text = result_text[:result_text.index('References')]
	if 'Etymology' in result_text:
		result_text = result_text[result_text.index('Etymology'):]

	#now we want to trim down the individual definitions to get keywords
	result_text = result_text.split("Etymology")

	while '' in result_text:
		result_text.remove('')

	for i in range(len(result_text)):
		if "See also" in result_text[i]:
			result_text[i] = result_text[i][:result_text[i].index("See also")]

		if "Derived" in result_text[i]:
			result_text[i] = result_text[i][:result_text[i].index("Derived")]

		#result_text[i] = result_text[i]

		result_text[i] = result_text[i].split("\n")

		while '' in result_text[i]:
			result_text[i].remove('')

	return result_text, result_html

def writeSignData(name):
	data = fetchWikiSourceData(DICT[name][0])[0]
	sign = DICT[name][0]
	f = open(BASEDIR + name + ".txt", "w")
	for d in data:
		f.write("----------\n")
		for i in range(1, len(d)):
			line = d[i].replace(sign, '')
			#prep for html display
			inds = []
			for j in range(len(line)):
				if ord(line[j]) > 500:
					inds.append(j)

			#we have to iterate backwards so the indices
			#don't change as we update the string
			for ind in inds[::-1]:
				line = line[:ind] + "<span style='font-family: sinacherib'>" + line[ind] + "</span>" + line[ind + 1:]

			f.write(line + "\n")
	f.close()

	n = open(BASEDIR + "namelist.txt", "a+")
	n.write(name + "\n")
	n.close()

	s = open(BASEDIR + "signlist.txt", "a+")
	s.write(sign + "\n")
	s.close()

for table in wikisoup.findAll('table'):
	for row in table.tbody.findAll('tr'):
		l = list(row.findAll('td'))
		try:
			targetind = 5
			target = l[targetind].get_text()
			if target[0:2] == "U+":
				targetind -= 1
				target = l[targetind].get_text()

			#create a list of characters in the value
			value = list(l[targetind + 1].get_text())

			#strip down all the characters except the sumerian sign
			#since the result of ord(<sign character>) is going to be
			#very large
			value = [val for val in value if ord(val) > 1000]

			value = ''.join(value)

			if value == '':
				continue

			if target in DICT.keys():
				DICT[target] += [value]
			else:
				DICT[target] = [value]

			if value in REVDICT.keys():
				REVDICT[value] += [target]
			else:
				REVDICT[value] = [target]
			#SIGNNAMELIST.append(target)
			#CODELIST.append(l[targetind + 1].get_text().split(" & "))
		except IndexError:
			pass

f = open(BASEDIR + "namelist.txt", "w")
f.close()

f = open(BASEDIR + "signlist.txt", "w")
f.close()

for key in DICT.keys():
	writeSignData(key)
	time.sleep(0.5)
