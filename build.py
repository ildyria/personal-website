# pylint: disable=missing-docstring
# pylint: disable=c0122
# pylint: disable=c0103
# pylint: disable=c0301
# pylint: disable=w0102
# pylint: disable=r0903
# pylint: disable=r0911
# pylint: disable=r0912

import os
import parser

def md_to_html(text):
    s = parser.State(text)
    s.tokenize()
    return s.interpreter()

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
    z += '    	<meta charset="utf-8" />\n'
    z += '    	<title>Benoit Viguier</title>\n'
    # z += '		<!-- <link rel="stylesheet" type="text/css" href="css/normalize.min.css" /> -->\n'
    z += '		<link rel="stylesheet" type="text/css" href="css/style.css" />\n'
    # z += '		<!-- <link rel="stylesheet" type="text/css" href="css/gh-fork-ribbon.css" /> -->\n'
    z += '	</head>\n'
    z += '	<body id=\'manpage\'>\n'
    z += '	  <div class=\'mp\' id=\'man\'>\n'
    return z

def foot():
    z = ''
    z += '     		<h2 id="COPYRIGHT">COPYRIGHT</h2>\n'
    z += '    			<p>Copyright (C) 2017 Benoit Viguier.</p>\n'
    z += '    			<ol class=\'man-decor man-foot man foot\'>\n'
    z += '    				<li class=\'tl\'></li>\n'
    z += '    				<li class=\'tc\'>July 2017</li>\n'
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

            output = ''
            output += head()
            output += md_to_html(file_in)
            output += foot()

            save(file_out, output)
            print("\tdone : " + file_out)

    print("\tBuild completed !")

main()
