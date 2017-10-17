#!/usr/bin/env python3

# pylint: disable=missing-docstring
# pylint: disable=c0103
# pylint: disable=c0122
# pylint: disable=c0301
# pylint: disable=w0102
# pylint: disable=r0903
# pylint: disable=r0911
# pylint: disable=r0912

import os
import parser
import datetime

def drop_md(text):
    if text[-3:] == ".md":
        return text[:-3]
    return text

def save(fn, z):
    d = open(fn, 'w', encoding="utf-8")
    d.write(z)
    d.close()

def head():
    z = ''
    z += '<!DOCTYPE html>\n'
    z += '<html lang="en">\n'
    z += '	<head>\n'
    z += '		<meta charset="utf-8" />\n'
    z += '		<title>Benoit Viguier</title>\n'
    z += '		<link rel="shortcut icon" href="images/manpage.ico" type="image/x-icon">\n'
    z += '		<link rel="stylesheet" type="text/css" href="css/style.css" />\n'
    z += '	</head>\n'
    z += '	<body id=\'manpage\'>\n'
    z += '	  <div class=\'mp\' id=\'man\'>\n'
    return z

def man_head():
    z = ''
    z += '<ol class=\'man-decor man-head man head\'>\n'
    z += '	<li class=\'tl\'>Benoit Viguier</li>\n'
    z += '	<li class=\'tc\'></li>\n'
    z += '	<li class=\'tr\'>Benoit Viguier</li>\n'
    z += '</ol>\n'
    return z

def man_menu(state):
    z = ''
    z += '<div class=\'man-navigation\' style=\'display:none\'>\n'
    z += state.toc()
    z += '</div>\n'

    return z

def foot():
    now = datetime.datetime.now()
    z = ''
    z += '    			<p>Copyright (C) ' + str(now.year) + ' Benoit Viguier.</p>\n'
    z += '    			<ol class=\'man-decor man-foot man foot\'>\n'
    z += '    				<li class=\'tl\'></li>\n'
    z += '    				<li class=\'tc\'> ' + now.strftime("%B") + ' ' + str(now.year) + '</li>\n'
    z += '    				<li class=\'tr\'>Benoit Viguier</li>\n'
    z += '    			</ol>\n'
    z += '    		</div>\n'
    z += '    	</body>\n'
    z += '    </html>\n'
    return z

def load(fn):
    d = open(fn, 'r', encoding="utf-8")
    z = d.read()
    d.close()
    return z

########################################
#
#		PARSING AND EXPORTING
#
########################################
def main():
    pages = os.listdir('pages')
    for pagesfile in pages:
        if pagesfile[-3:] == '.md':
            file_in = load('pages/' + pagesfile)
            file_out = pagesfile[0:-3] + '.html'

            content = parser.State(file_in)
            content.tokenize()

            output = ''
            output += head()
            output += man_menu(content)
            output += man_head()
            output += content.interpreter()
            output += foot()

            save(file_out, output)
            print("\tdone : " + file_out)

    print("\tBuild completed !")

main()
