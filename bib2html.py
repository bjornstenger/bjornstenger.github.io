# -*- coding: utf-8 -*-

'''Convert utility from bibtex to html'''

# --------------------------------------------------------------------------------
# Copyright (C) 2011 by Bjørn Ådlandsvik and Björn Stenger
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# --------------------------------------------------------------------------------
# Python script to convert bibtex to html (4.01)
#
# Usage:
# bib2html [bibfile] [htmlfile]
#
# Currently not a full bibtex parser.
# Restrictions:
#   entries must end with "}" in first column of a new line
#   no blank lines allowed within an entry
#   must have space before and after the "=" in the field definitions
#   limited special symbols (accents etc.)
#
# Fields such as author, year, title, ... are marked with <span class=...>
# in the html file. Appearance can be controlled with a CSS style sheet.
# Selected authors (for instance yourself, your research group)
# can be set in the selected_author list (surname only).
# They will be marked by <span class="selected>.
#
# A url field is transferred as [ link ] to the html file,
# if url is missing and doi is presented a url is created,
# A pdf field can point to a local pdf file
#
# Italic text (such as latin species names) may be marked with
# \emph{ ... } in the bibtex file. This is handled correctly
# by both bib2html and LaTeX.
#
# --------------------------------------------------------------------------------
# Bjørn Ådlandsvik <bjorn@imr.no>
# Institute of Marine Research
#
# Björn Stenger [bjorn@cantab.net]
# Rakuten Institute of Technology
# --------------------------------------------------------------------------------

import os
import sys
import re
import datetime
import codecs

# --------------------------------------------------------------------------------
# user settings
# --------------------------------------------------------------------------------

# output html encoding
encoding = 'UTF-8'
#encoding = 'ISO-8859-1'

# html page title
title = u'Publication List'

# list of authors for which the font can be changed
selected_authors = [u'Yournamehere,']

# location of pdf-files
#pdfpath = './pdf'
pdfpath = 'http://bjornstenger.github.io/papers/'

# css style file to use
css_file = 'style_rbg.css'

# now = yyyy-mm-dd
now = str(datetime.date.today())


# html prolog
# modify according to your needs
prolog = """<!DOCTYPE HTML
    PUBLIC "-//W3C//DTD HTML 4.01//EN"
    "http://www.w3.org/TR/html4/strict.dtd">
<head>
  <meta http-equiv=Content-Type content="text/html; charset=%s">
  <title>%s</title>
  <link rel="stylesheet" type="text/css" href="%s">
  <link href='http://fonts.googleapis.com/css?family=Lato:400,700,400italic,700italic' rel='stylesheet' type='text/css'>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
  <style type="text/css">
     span.selected {color: #000000}
     span.author {color: #000000}
     span.papertitle {font-weight: 700;}
     li {margin-top: 0px; margin-bottom: 14px}
  </style>
</head>
<body>

<div class="section">
<h2 id="reports">Bj&ouml;rn Stenger - List of Publications</h2>
<br>
%s
<br><br>
<a href="bjornstenger.bib"><i class="fa fa-file-o" style="width:4.2ch;margin-top:1px;"></i> bibtex file</a>
<br><br>
<div class="paper">

""" % (encoding, title, css_file, now)



# html epilog
epilog = """
</div>
</div>
<br>
<hr>
Created %s with <a href="bib2html.py">bib2html.py</a>
</p>

</body>
</html>
""" % (now)







# --------------------------------------------------------------------------------
# class and function definitions
# --------------------------------------------------------------------------------

# regular expression for \emph{...{...}*...}
emph = re.compile(u'''
            \\\\emph{                       # \emph{
            (?P<emph_text>([^{}]*{[^{}]*})*.*?)  # (...{...})*...
            }''', re.VERBOSE)               # }



# --------------------------------------------------------------------------------
# class: bibtex entry
# --------------------------------------------------------------------------------
class Entry(object):
    """Class for bibtex entry"""

    def clean(self):
        '''Clean up an entry'''
        for k, v in self.__dict__.items():

            # remove leading and trailing whitespace
            v = v.strip()

            # replace special characters - add more if necessary
            v = v.replace('\\AE', u'Æ')
            v = v.replace('\\O',  u'Ø')
            v = v.replace('\\AA', u'Å')
            v = v.replace('\\ae', u'æ')
            v = v.replace('\\o',  u'ø')
            v = v.replace('\\aa', u'å')
            v = v.replace('\\\'a', '&aacute;')
            v = v.replace('\\\'e', '&eacute;')
            v = v.replace('\\c{c}' , '&ccedil;')

            # fix \emph in title
            if k == 'title':
                v = re.sub(emph, '<I>\g<emph_text></I>', v)

            # remove "{" and "}"
            v = v.replace('{', '')
            v = v.replace('}', '')
            v = v.replace('"', '')

            # remove trailing comma and dot
            if len(str(v))>0:
              if v[-1] == ',': v = v[:-1]

            # fix author
            if k == 'author':

                # split into list of authors
                authors = v.split(' and ')

                # strip each author ;)
                authors = [a.strip() for a in authors]

                # make blanks non-breakable
                authors = [a.replace(' ', '&nbsp;') for a in authors]

                # reverse first and surname
                for i, a in enumerate(authors):
                    #print a + "\n"
                    #surname =
                    namearray = a.split('&nbsp;')
                    surname = namearray[0]
                    surname = surname.replace(',', '')
                    firstname = ' '.join(namearray[1:])
                    authors[i] = firstname + " " + surname


                # mark selected authors - if there are any
                #for i, a in enumerate(authors):
                #    surname = a.split('&nbsp;')[0]
                #    if surname in selected_authors:
                #        a = ''.join(['<span class="selected">', a, '</span>'])
                #        authors[i] = a



                # concatenate the authors again
                #if len(authors) == 1:
                #    v = authors[0]
                #elif len(authors) == 2:
                #    v = authors[0] + " and " + authors[1]
                #else:  # len(authors) > 2:
                #    v =  ", ".join(authors[:-1]) + " and " + authors[-1]
                v = ", ".join(authors[:])

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


        if 'chapter' in edict:
            fid.write('<span class="papertitle">')
            fid.write(self.chapter)
            fid.write('</span>')
            fid.write(',<br>')
        else:
            fid.write('<span class="papertitle">')
            fid.write(self.title)
            fid.write('</span>')
            fid.write(',<br>')


        # --- author ---
        #fid.write('<span class="author">')
        fid.write(self.author)
        #fid.write('</span>')
        fid.write(',<br>')

        # -- if book chapter --
        if 'chapter' in edict:
          fid.write('in: ')
          fid.write('<i>')
          fid.write(self.title)
          fid.write('</i>')
          fid.write(', ')
          fid.write(self.publisher)


        # --- journal or similar ---
        journal = False
        chapter = False
        if 'journal' in edict:
            journal = True
            fid.write('<i>')
            fid.write(self.journal)
            fid.write('</i>')
        elif 'booktitle' in edict:
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

        # --- volume, pages, notes etc ---
        if 'volume' in edict:
            fid.write(', Vol. ')
            fid.write(edict['volume'])
        if ('number' in edict and edict['type']!='techreport'):
            fid.write(', No. ')
            fid.write(edict['number'])
        if 'pages' in edict:
                fid.write(', p.')
                fid.write(edict['pages'])

        if 'month' in edict:
            fid.write(', ')
            fid.write(self.month)

        # --- year ---
        #fid.write('<span class="year">')
        fid.write(' ');
        fid.write(self.year)
        #fid.write('</span>')

        # final period
        fid.write('.')

        if 'note' in edict:
            if journal or chapter: fid.write(' <i>')
            fid.write(edict['note'])
            # final period
            fid.write('</i>.')

        # --- Links ---

        fid.write('<br>')

        if 'pdf' in edict:
            #line = '\n[&nbsp;<a href="papers/%s">pdf</a>&nbsp;]' % self.pdf
            line = '\n[<a href="papers/%s">pdf</a>]' % self.pdf
            fid.write(line)

        if 'arxiv' in edict:
            #line = '\n[&nbsp;<a href="%s">arxiv</a>&nbsp;]' % self.arxiv
            line = '\n[<a href="%s">arxiv</a>]' % self.arxiv
            fid.write(line)




        # Terminate the list entry
        fid.write('\n</li>\n')




# --------------------------------------------------------------------------------
# generator: bibtex reader
# --------------------------------------------------------------------------------
def bib_reader(filename):
    '''Generator for iteration over entries in a bibtex file'''

    fid = open(filename)

    while True:

        # skip irrelevant lines
        while True:
            #line = fid.next()
            line = next(fid)
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
                #line = fid.next()
                line = next(fid)
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




# --------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------
def main():

  args = sys.argv[1:]

  if not args:
      bibfile="bjornstenger.bib"
    #print 'usage: bib2html [bibfile] [htmlfile]'
    #sys.exit(1)
  else:
      bibfile=args[0]
      del args[0:1]

  if not args:
    htmlfile="publist.html" #default
  else:
    htmlfile=args[0]


  # create the html file with opted encoding
  f1 = codecs.open(htmlfile, 'w', encoding=encoding)

  # write the initial part of the file
  f1.write(prolog)

  # lists according to publication type
  bookchapterlist =[]
  journallist =[]
  conflist =[]
  techreportlist =[]
  thesislist =[]

  alllist = []

  # read bibtex file
  f0 = bib_reader(bibfile)

   # Iterate over the entries and bib2html directives
  for e in f0:
    e.clean()
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

    alllist.append(e)


  sort_by_type = False

  # write list according to publication type
  if sort_by_type:
      f1.write('<h2>Journals</h2>');
      f1.write('\n<ol reversed>\n\n')
      for e in journallist:
        e.write(f1)
      f1.write('\n</ol>\n\n')

      f1.write('<h2>Conferences and Workshops</h2>');
      f1.write('\n<ol reversed>\n\n')
      for e in conflist:
        e.write(f1)
      f1.write('\n</ol>\n\n')

      f1.write('<h2>Book Chapters</h2>');
      f1.write('\n<ol reversed>\n\n')
      for e in bookchapterlist:
        e.write(f1)
      f1.write('\n</ol>\n\n')

      f1.write('<h2>Technical Reports</h2>');
      f1.write('\n<ol reversed>\n\n')
      for e in techreportlist:
        e.write(f1)
      f1.write('\n</ol>\n\n')

      f1.write('<h2>Thesis</h2>');
      f1.write('\n<ol reversed>\n\n')
      for e in thesislist:
        e.write(f1)
      f1.write('\n</ol>\n\n')

      # write epilog
      f1.write(epilog)
      f1.close()

  else: # sort by year
      f1.write('\n<ol reversed>\n\n')
      for e in alllist:
        e.write(f1)
      f1.write('\n</ol>\n\n')
      # write epilog
      f1.write(epilog)
      f1.close()



  print ('written: '+htmlfile+'\n')

if __name__ == '__main__':
  main()
