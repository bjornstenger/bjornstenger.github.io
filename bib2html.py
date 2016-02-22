# -*- coding: utf-8 -*-

'''Convert utility from bibtex to html'''

# ------------------------------------------------
# Make a html publication list from a bibtex file
# The html file is strict html 4.01
#
# Publications appear in the same order as in the bibtex file
# Not full bibtex parser:
#   Entries must end with "}" in first column of a new line
#   No blank lines allowed within an entry
#   Must have space before and after the "=" in the field definitions
#
# Arbitrary text (e.g. html code) can be embedded in the bibtex file
# prefixed with 'bib2html:'. It will appear in the html file.
# Such text is ignored if the bibtex file is used with LaTeX.
#
# Fields such as author, year, title, ... are marked with <span class=...>
# in the html file. Appearance can be controlled with CSS style sheet.
#
# Selected authors (for instance yourself, your research group)
# can be set in the selected_author list (surname only).
# They will be marked by <span class="selected>.
#
# An url field is transferred as [ link ] to the html file,
# if url is missing and doi is presented a url is created,
# A pdf field can point to a local pdf file
# A qdf field is a pdf field that has been turned off to not 
# provoke the journal owners.
#
# Italic text (such as latin species names) may be marked with
# \emph{ ... } in the bibtex file. This is handled correctly
# by both bib2html and LaTeX.
#
# -----------------------------------------------------
# 2008-04-28
# Bjørn Ådlandsvik <bjorn@imr.no>
# Institute of Marine Research
#
# 2011-02-24
# modified by Bjorn Stenger [bjorn@cantab.net]
# main modifications:
# - filenames as command line argument
# - output according to publication type
# - text formatting changed
# - removed option to include html code within bibtex file using 'bib2html' prefix
# 
# -----------------------------------------------------


import os
import sys
import re
import datetime
import codecs

# ----------------------
# User settings
# ----------------------

# Input bibtex file
#bibfile   = 'bjornstenger.bib'

# Output html file
#htmlfile  = 'publications.html'

# Output html encoding
#encoding = 'UTF-8'
encoding = 'ISO-8859-1'

# Title element in htmlfile
title = u'Bjorn Stenger - Publications'

# List of authors to emphasis
selected_authors = [u'Stenger,']

# Where to look for pdf-files
#pdfpath = './pdf'
pdfpath = 'http://mi.eng.cam.ac.uk/~bdrs2/papers/'

# CSS style file to use
css_file = 'style.css'

# -----------------------
# HTML prolog and epilog
# -----------------------

prolog = """<!DOCTYPE HTML
    PUBLIC "-//W3C//DTD HTML 4.01//EN"
    "http://www.w3.org/TR/html4/strict.dtd">
    
<head>
  <meta http-equiv=Content-Type content="text/html; charset=%s">
  <title>%s</title>

  <link rel="stylesheet" type="text/css" href="%s">



  <style type="text/css">     
     span.selected {color: #000000}
     span.author {color: #000000}
     span.title {font-weight: bold;}
     li {margin-top: 0px; margin-bottom: 16px}
  </style>


<!--

     li {margin-top: 0px; margin-bottom: 16px}

     body{
       width:700px;
       margin:0px auto;
       text-align:justify;
       padding:25px;
       font-family: Verdana, Arial, Helvetica, sans-serif;
	font-family: Trebuchet MS,Verdana, Arial, Helvetica, sans-serif;

	font-size:10px;
	font: 0.71em Verdana;
	line-height: 1.7;
        color: #404040;
      }
   </style>
-->


</head>

<body>

<div class="header">
<strong>&nbsp;&nbsp;&nbsp;Bj&ouml;rn Stenger</strong><br> 
&nbsp;&nbsp;&nbsp;Computer Vision Group, Toshiba Research Europe
</div>

<div class="container">
<ul id="miniflex">
	<li><a href="index.html">home</a></li>
	<li><a href="pubs.html" class="active">publications</a></li>
</ul>
</div>


<div id="content">
""" % (encoding, title, css_file)

# now = yyyy-mm-dd
now = str(datetime.date.today())

epilog = """
<br>
<hr>
Created %s with <a href="bib2html.py">bib2html.py</a>
</p>
</div>

</body>
</html>
""" % (now)


# -------------------------------
# Class and function definitions
# -------------------------------


# regular expression for \emph{...{...}*...}
emph = re.compile(u'''
            \\\\emph{                       # \emph{
            (?P<emph_text>([^{}]*{[^{}]*})*.*?)  # (...{...})*...
            }''', re.VERBOSE)               # }



class Entry(object):
    """Class for bibtex entry"""

    # -------------------

    def clean(self):
        '''Clean up an entry'''
        for k, v in self.__dict__.items():

            # remove leading and trailing whitespace
            v = v.strip()

            # Fix scandinavian characters
            v = v.replace('\\AE', u'Æ')
            v = v.replace('\\O',  u'Ø')
            v = v.replace('\\AA', u'Å')
            v = v.replace('\\ae', u'æ')
            v = v.replace('\\o',  u'ø')
            v = v.replace('\\aa', u'å')

            # more special symbols
            #v = v.replace('&', u'&amp;')
            v = v.replace('\\\'a', '&aacute;')
            v = v.replace('\\c{c}' , '&ccedil;')

            # Fix \emph in title
            if k == 'title':
                v = re.sub(emph, '<I>\g<emph_text></I>', v)

            # Remove "{" and "}"
            v = v.replace('{', '')
            v = v.replace('}', '')
            v = v.replace('"', '')
        
            # remove trailing comma and dot
            if v[-1] == ',': v = v[:-1]
            #if v[-1] == '.': v = v[:-1]


            # fix author
            if k == 'author':

                # Split into list of authors
                authors = v.split(' and ')

                # Strip each author
                authors = [a.strip() for a in authors]

                # Make blanks non-breakable
                authors = [a.replace(' ', '&nbsp;') for a in authors]

                # Mark selected authors
                for i, a in enumerate(authors):
                    surname = a.split('&nbsp;')[0]
                    #print surname + '\n'
                    if surname in selected_authors:
                        a = ''.join(['<span class="selected">', a, '</span>'])
                        authors[i] = a

                # Concatenate the authors again
                if len(authors) == 1:
                    v = authors[0]
                elif len(authors) == 2:
                    v = authors[0] + " and " + authors[1]
                else:  # len(authors) > 2:
                    v =  ", ".join(authors[:-1]) + " and " + authors[-1]

            # fix pages
            if k == 'pages':
                v = v.replace('--', '&ndash;')
                v = v.replace('-',  '&ndash;')
        
            setattr(self, k, v)
        
    # ------------------ 

    def write(self, fid):
        """Write entry to html file"""

        edict = self.__dict__  # bruke

        # --- Start list ---
        fid.write('\n')
        fid.write('<li>\n')

        # --- author ---
        fid.write('<span class="author">')
        fid.write(self.author)
        fid.write('</span>')
        fid.write(',<br>')

        # --- title ---
        #fid.write('<span class="title">')
        #fid.write(self.title)
        #fid.write('</span>')
        #fid.write(',<br>')

        # --- title with link ---
        fid.write('<span class="title">')
        fid.write(self.title)
        fid.write('</span>')
        fid.write(',<br>')


        # --- chapter ---
        if edict.has_key('chapter'):
          fid.write(self.chapter)
          fid.write(', in: ')
          fid.write('<i>')
          fid.write(self.title)
          fid.write('</i>')
          fid.write(', ')
          fid.write(self.publisher)

        # --- journal or similar ---
        journal = False
        if edict.has_key('journal'):
            journal = True
            fid.write('<i>')
            fid.write(self.journal)
            fid.write('</i>')
        elif edict.has_key('booktitle'):
            journal = True
            fid.write(edict['booktitle'])
        elif edict['type'] == 'phdthesis':
            journal = True
            fid.write('PhD thesis, ')
            fid.write(edict['school'])
        elif edict['type'] == 'techreport':
            journal = True
            fid.write('Tech. Report, ')
            fid.write(edict['number'])
    
        # --- Volume, pages, notes or similar ---
        if edict.has_key('volume'):
            fid.write(', Vol. ')
            fid.write(edict['volume'])
        if (edict.has_key('number') and edict['type']!='techreport'):
            fid.write(', No. ')
            fid.write(edict['number'])
        if edict.has_key('pages'):
                fid.write(', p.')
                fid.write(edict['pages'])
        elif edict.has_key('note'):
            if journal: fid.write(', ')
            fid.write(edict['note'])
        if edict.has_key('month'):
            fid.write(', ')
            fid.write(self.month)

        # --- year ---
        fid.write('<span class="year">')
        fid.write(', ');
        fid.write(self.year)
        fid.write('</span>')
        #fid.write(',\n')

        # Final period
        fid.write('.')

        # --- Links ---
        pdf = False
        url = False
        if edict.has_key('pdf'):
            pdf = True
        if edict.has_key('url') or edict.has_key('doi'):
            url = True

        if pdf or url:
            fid.write('<br>\n[&nbsp;')
            if pdf:
                fid.write('<a href="')
                fid.write(pdfpath + self.pdf)
                fid.write('">pdf</a>&nbsp;')
                if url:
                    fid.write('\n|&nbsp;')
            if url:
                fid.write('<a href="')
                if edict.has_key('url'):
                    fid.write(self.url)
                else:
                    fid.write('http://dx.doi.org/' + self.doi)
                fid.write('">link</a>&nbsp;')
            fid.write(']\n')

        # Terminate the list entry
        fid.write('</li>\n')

# ---------------------------------------

def bib_reader(filename):
    '''Generator for iteration over entries in a bibtex file'''

    fid = open(filename)

    while True:

        # skip irrelevant lines
        while True:
            line = fid.next()
            if len(line) > 0:
                if line[0] == '@': break           # Found entry

        # Handle entry
        if line[0] == '@':
            e = Entry()

            # entry type mellon @ og {
            words = line.split('{')
            e.type = words[0][1:].lower()
            #print e.type + '\n'

            # Iterate through the fields of the entry
            first_field = True
            while True: 
                line = fid.next()
                #print line + '\n'
                words = line.split()
                
                if words[0] == "}": # end of entry
                    # store last field
                    setattr(e, fieldname, fieldtext)
                    break

                if len(words) > 1 and words[1] == "=": # new field
                    # store previous field
                    if not first_field:
                        setattr(e, fieldname, fieldtext)
                    else:
                        first_field = False
                    #inline = True
                    fieldname = words[0].lower()
                    fieldtext = " ".join(words[2:]) # remains a text

                else:  # continued line
                    fieldtext = " ".join([fieldtext] + words)

                
        yield e
        

# --------------------------------------        
# Main action
# --------------------------------------        

def main():

  args = sys.argv[1:]

  if not args:
    print 'usage: bib2html [bibfile] [htmlfile]'
    sys.exit(1)

  bibfile=args[0]
  
  del args[0:1]

  if not args:
    htmlfile="publications.html" #default
  else:
    htmlfile=args[0]

  # Create the html file with opted encoding 
  f1 = codecs.open(htmlfile, 'w', encoding=encoding)

  # Write the initial part of the file
  f1.write(prolog)

  # Open the bibtex file
  bookchapterlist =[]
  journallist =[]
  conflist =[]
  techreportlist =[]
  thesislist =[]

  #f0 = bib_reader(bibfile, elist)
  f0 = bib_reader(bibfile)

   # Iterate over the entries and bib2html directives
  in_list = False       # in/out of unordered list
  for e in f0:  
    e.clean()
    #print "type:" + e.type +"\n"
    if (e.type=="inbook"):
      bookchapterlist.append(e)
    if (e.type=="article"):
      journallist.append(e)
    if (e.type=="inproceedings"):
      conflist.append(e)
    if (e.type=="techreport"):
      techreportlist.append(e)
    if (e.type=="phdthesis"):
      thesislist.append(e)


  f1.write('<h2>Book Chapters</h2>');
  f1.write('\n<ol>\n\n')
  for e in bookchapterlist:
    e.write(f1)
  f1.write('\n</ol>\n\n')

  f1.write('<h2>Journal Publications</h2>');
  f1.write('\n<ol>\n\n')
  for e in journallist:
    e.write(f1)
  f1.write('\n</ol>\n\n')

  f1.write('<h2>Conference Publications</h2>');
  f1.write('\n<ol>\n\n')
  for e in conflist:
    e.write(f1)
  f1.write('\n</ol>\n\n')

  f1.write('<h2>Technical Reports</h2>');
  f1.write('\n<ol>\n\n')
  for e in techreportlist:
    e.write(f1)
  f1.write('\n</ol>\n\n')

  f1.write('<h2>Theses</h2>');
  f1.write('\n<ol>\n\n')
  for e in thesislist:
    e.write(f1)
  f1.write('\n</ol>\n\n')
    

  # Finish the html file
  f1.write(epilog)
  f1.close()
  
  print 'Written: '+htmlfile+'\n'



if __name__ == '__main__':
  main()
