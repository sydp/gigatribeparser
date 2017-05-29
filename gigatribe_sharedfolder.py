'''
GigaTribe v3 Shared Folder parser

Author: Syd Pleno
Contact: syd.pleno@gmail.com

Copyright 2012 Syd Pleno - All rights reserved

TODO: point to <share>,XML in <USERID>\sharedfolders\
then load the corresponding DAT file under <USERID>\sharedfolders\dbs\<share>\<share>.dat
and shared XML file under 
<USERID\sharedfolders\customs\<X>.xml
where X is an arbitrary numerical value set by the program.
It can be matched through the <path> element
'''

import struct
import sys
import os
from optparse import OptionParser
from DateConverter import DateConverter
import xml.etree.ElementTree as xml

def safe_str(obj):
    """ return the byte string representation of obj """
    try:
        return str(obj)
    except UnicodeEncodeError:
        # obj is unicode
        return unicode(obj).encode('unicode_escape')
		
def unpack_qstring(h):
	str_len = struct.unpack(">I", h[0:4])
	qstring = h[4:].decode("utf-16-be")
	return qstring

def unpack_stream_qstring(h):
	str_len = struct.unpack(">I", h.read(4))[0]
	if str_len == 0xffffffff:
		return None
	return h.read(str_len).decode("utf-16-be") # does this convert to UTF-8?

def qdatetimeToStr(utc, date, time):
	(D,M,Y) = DateConverter.JDNtoGD(date)
	date_format = "%i-%i-%i %i:%02i:%06.3f"
	milliseconds = time
	hours, milliseconds = divmod(milliseconds, 3600000)
	minutes, milliseconds = divmod(milliseconds, 60000)
	seconds = float(milliseconds) / 1000
	if utc:
		date_format += " UTC"
	return date_format % (D, M, Y, hours, minutes, seconds)
	
def unpack_stream_qdatetime(h):
	date = struct.unpack(">I", h.read(4))[0]
	time = struct.unpack(">I", h.read(4))[0]
	utc = struct.unpack("B", h.read(1))[0]
	return qdatetimeToStr(utc, date, time)

class GigaTribe_v3_SharedFolder:

	def __init__(self):
		self.records = []
		
	def unpack_stream_record(self, h, path):
		filename = unpack_stream_qstring(h);
		flag1 = struct.unpack("b", h.read(1))[0]
		flag2 = struct.unpack("b", h.read(1))[0]
		timestamp = unpack_stream_qdatetime(h)
		return (filename, flag1, flag2, timestamp, path)
		
	def unpack_header(self,h):
		num_records = struct.unpack(">I", h.read(4))[0]
		return num_records
		
	def ParseFile(self, h, path, do_recursive, share_path):
		new_records = []
		for n in range(self.unpack_header(h)):
			new_records.append(self.unpack_stream_record(h, share_path))#os.path.dirname(path)))
		self.records += new_records
		if do_recursive:
			for rec in new_records:
				if rec[1] == 1:
					sub = os.path.dirname(path) + "\\" + rec[0] + "\\" + rec[0] + ".dat"
					try:
						with open(sub, "rb") as f:
							self.ParseFile(f, sub, do_recursive, share_path + "\\" + rec[0])
					except:
						print >> sys.stderr, "Error: " + sub + " does not exist"
		
		
	def SortRecords(self):
		# sort by share then 
		self.records = sorted(self.records, cmp=lambda x,y: cmp(x[4], y[4]))
		
	def PrintCSV(self, num_column=False):
		headers = ["#", "Filename", "Folder", "Flag", "Timestamp", "Share path"]
		if num_column:
		    print ",".join(x for x in headers)
		else:
			print ",".join(x for x in headers[1:])
		for row, record in enumerate(self.records):
			line = ""
			if num_column:
				line = str(row+1)+","
			for v, y in enumerate(record):
				#print y
				line += "\""+safe_str(y)+"\","
			print line.strip(",")
	
	def PrintHTML(self, filename):
		with open(os.path.basename(filename) + ".html", 'wb') as f:
			headers = ["#", "Filename", "Folder", "Flag", "Timestamp", "Share path"]
			header = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">"
			header += "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">"
			header += "p, li { white-space: pre-wrap; }"
			header += "</style></head><body style=\" font-family:'Tahoma'; font-size:8pt; font-weight:400; font-style:normal;\">"
			f.write(header)
			f.write("<h3> Filename:" + filename + "</h3>")
			table = "<table border=\"1\"><tr>"
			for h in headers:
				table += "<td>"+h+"</td>"
			f.write(table+"\n")	
			for x, record in enumerate(self.records):
				row = "<tr><td>"+str(x+1)+"</td>"
				for y, cell in enumerate(record):
					row += "<td>" + safe_str(cell) + "</td>"
				row += "</tr>\n"
				f.write(row)
			f.write("</tr></table></body></html>\n")
			
def main():
	description = "Extracts records from GigaTribe shared library"
	usage = "Usage: %prog [-n] <shared file.dat> (CSV)\nUsage: %prog -d <shared file.dat> (HTML)"
	optparser = OptionParser(description=description, usage=usage, version="%prog 0.1")
	optparser.add_option("-r", "--recursive", dest="recursive", 
						 action="store_true", default=False, 
						 help="Recursively parse any sub folders")
	optparser.add_option("-n", "--num_column", dest="num_column", 
						 action="store_true", default=False, 
						 help="Add Row Number to CSV row")
	optparser.add_option("-d", "--html_report", dest="do_html",
						action="store_true", default=False,
						help="Generate HTML report")
	optparser.add_option("-s", "--sort_records", dest="do_sort",
						action="store_true", default=False,
						help="Sort results")
	optparser.add_option("-x", "--load_xml", dest="load_xml",
						action="store_true", default=False,
						help="Load Shared Library from XML")
	(options, args) = optparser.parse_args()
	if len(args) < 1:
		print optparser.print_help()
		sys.exit()
	with open(args[0], 'rb') as f:
		chat = GigaTribe_v3_SharedFolder()
		chat.ParseFile(f, args[0], options.recursive, os.path.basename(args[0][:-4]))
		if options.do_sort:
			chat.SortRecords()
		if options.do_html:
			chat.PrintHTML(args[0])
		else:
			chat.PrintCSV(options.num_column)
			
if __name__ == "__main__":
	main()
	