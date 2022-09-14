#!/usr/bin/python
#coding:UTF-8
# Filename : calendarthu.py
# Author: CareF.LM
# Version 2.2, 加入对单双周, 前八周, 后八周的支持
from datetime import *
from unicodedata import category
import xlrd
def newevent(startd,day,start,end,name,loc,\
	freq = 'WEEKLY', count = 16, dsp = ""):
	EVENT = '''BEGIN:VEVENT
DTSTART;TZID=Asia/Shanghai:%s
DTEND;TZID=Asia/Shanghai:%s
%sDESCRIPTION:%s
LOCATION:%s
SEQUENCE:0
STATUS:CONFIRMED
SUMMARY:%s
TRANSP:OPAQUE
%sEND:VEVENT
'''
	REPEAT = '''RRULE:FREQ=%s;COUNT=%d;%sBYDAY=%s
'''
	ALARM = '''BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:This is an event reminder
TRIGGER:-P0DT0H15M0S
END:VALARM
'''
	WEEK = ('MO','TU','WE','TH','FR','SA','SU')
	date = (startd + timedelta(day)).strftime('%Y%m%d')
	start = date+'T'+start+'00Z'
	end = date+'T'+end+'00Z'
	if(freq == 'WEEKLY'):
		return EVENT%(start,end,REPEAT%(freq,count,"",WEEK[(day-1)%7]),dsp,loc,name,ALARM)
	elif(freq == 'DOUBLE'):
		return EVENT%(start,end,REPEAT%('WEEKLY',count,"INTERVAL=2;",WEEK[(day-1)%7]),dsp,loc,name,ALARM)
	else:
		return EVENT%(start,end,'',dsp,loc,name,ALARM)

def getclass(exlfile,startd):
	import re
	numfosucc = 0
	numoffail = 0
	oclass = re.compile(r'(.*)\((.*)\)')
	oclaswk = re.compile(r'.*(全|前八|后八|单|双)周')
	olec = re.compile(r'(.*)\(第(\d+)周\)')
	other = re.compile(r'(.*)\(([^)]*?)；第(.*)周\)')
	forwks = re.compile(r'(\d+)-(\d+)周')
	sttime = ('0800','0950','1330','1520','1710','1910')
	edtime = ('0935','1215','1505','1655','1840','2145')
	data = exlfile.sheet_by_index(0)
	classes = []
	for x in range(1,8):
		for y in range(2,8):
			cell = data.cell_value(rowx = y,colx = x)
			if(cell == ''):
				continue
			#print cell.encode('utf-8'),"x = ",x,"y=",y
			cell.replace('','')
			clas = cell.split('\n')
			for cla in clas:
				if oclass.match(cla):
					infos = oclass.match(cla)
					name = infos.group(1)
					print(cla, end='')
					parts = infos.group(2).split('；')
					if len(parts)==4:
						claswk, loc = parts[-2:]
					elif len(parts)==3:
						claswk = parts[-1]
						loc = 'none'
					else:
						numoffail += 1
						continue
					nw = oclaswk.match(claswk)
					if(nw == None):
						print(' fails')
						numoffail += 1
						continue
					if(nw.group(1) == u'全'):
						event = newevent(startd,x,sttime[y-2],edtime[y-2],name,loc,dsp = cla)
					elif(nw.group(1) == u'前八'):
						event = newevent(startd,x,sttime[y-2],edtime[y-2],name,loc,dsp = cla,count = 8)
					elif(nw.group(1) == u'后八'):
						event = newevent(startd+timedelta(days=7*7),x,sttime[y-2],edtime[y-2],name,loc,dsp = cla,count = 8)
					elif(nw.group(1) == u'双'):
						event = newevent(startd+timedelta(days=7),x,sttime[y-2],edtime[y-2],name,loc,dsp = cla,count = 8,freq = 'DOUBLE')
					elif(nw.group(1) == u'单'):
						event = newevent(startd,x,sttime[y-2],edtime[y-2],name,loc,dsp = cla,count = 8,freq = 'DOUBLE')
					else:
						print(' fails')
						numoffail += 1
						continue
					classes.append(event)
					print(' succeeds')
					numfosucc += 1

	return (classes,numfosucc,numoffail)

def getweeknum(startd):
	NWEEK = u'''BEGIN:VEVENT
DTSTART;VALUE=DATE:%s
DTEND;VALUE=DATE:%s
DESCRIPTION:
SEQUENCE:0
STATUS:CONFIRMED
SUMMARY:第%d周
TRANSP:TRANSPARENT
END:VEVENT
'''
	weeknum = []
	for day in range(0,18):
		wsd = (startd+timedelta(day*7+1) ).strftime('%Y%m%d')
		event = NWEEK%(wsd,wsd,day+1)
		weeknum.append(event)
	return weeknum

BASE = '''BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-TIMEZONE:Asia/Shanghai
%sEND:VCALENDAR'''

def calget(book,startd):
	# startd = date(2015,3,1)
	result = getclass(book,startd)
	classes = result[0]
	items = classes
	ics = BASE%("".join(items))
	return (ics,result[1],result[2])

if __name__ == "__main__":
	import sys
	try:
		path = sys.argv[1]
	except:
		path = 'table.xls'
	startd = date(2022,9,11) # should be a SUNDAY
	book = xlrd.open_workbook(path)
	result = calget(book,startd)
	with open('sca.ics','w', encoding="utf-8") as outf:
		outf.write(result[0])
	print('成功添加课程信息%d条, 失败%d条'%(result[1],result[2]))
