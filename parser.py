# pylint: disable=missing-docstring
# pylint: disable=c0122
# pylint: disable=c0103
# pylint: disable=c0301
# pylint: disable=w0102
# pylint: disable=r0903
# pylint: disable=r0904
# pylint: disable=r0911
# pylint: disable=r0912
# pylint: disable=r0913

import sys

# sys.setrecursionlimit(15000)

###############################################################################
#                           Define the tokens
###############################################################################

class Token():
    def __init__(self, typ="type", val="UnknownVal"):
        self.typ = typ
        self.val = val

    def out(self):
        if self.typ != "word":
            return self.typ

        return self.val

    def __repr__(self):
        if self.typ == "word":
            return self.val
        if self.typ == " ":
            return '∙'
        if self.typ == "\n":
            return '↩'
        return self.typ



###############################################################################
#                           Define the Tokenizer
###############################################################################

class Node():

    def __init__(self, typ='', val='', children=[], attr=[]):
        self.typ = typ
        self.val = val
        self.attr = attr
        self.children = children

    def __repr__(self):
        if self.typ == "word":
            return self.val
        if self.typ == " ":
            return '∙'
        if self.typ == "\n":
            return '↩'

        output = ''
        for child in self.children:
            output += child.__repr__()
        return self.typ + output

    def interpret(self, dic={}):
        output = ''
        for child in self.children:
            output += child.interpret(dic)

        attributes = ''
        for attr in self.attr:
            attributes += attr.interpret(dic)

        if self.typ == "word":
            return self.val
        if self.typ == 'b':
            return '<b>' + output + '</b>'
        if self.typ == 'a':
            src = dic.get(str(self.val), 'default')
            return '<a href="' + src + '" ' + attributes + '>' + output + '</a>'
        if self.typ == 'img':
            href = dic.get(str(self.val), 'default')
            return '<img src="' + href + '" alt="' + output +'" ' + attributes + ' />'
        if self.typ == 'ltd':
            prep = ''
            prep += '<dl>'
            prep += '<dt' + self.val + '>'
            prep += output
            prep += '</dt>'
            prep += '<dd>'
            prep += '<p>'
            prep += attributes
            prep += '</p>'
            prep += '</dd>'
            prep += '</dl>'
            return prep + '\n'
        if self.typ == 'td':
            prep = ''
            prep += '<dt' + self.val + '>'
            prep += output
            prep += '</dt>'
            prep += '<dd>'
            prep += '<p>'
            prep += attributes
            prep += '</p>'
            prep += '</dd>'
            return prep + '\n'
        if self.typ == 'br':
            return '<br />\n'
        if self.typ == 'i':
            return '<i>' + output + '</i>'
        if self.typ == 'H1':
            return '<H1 ' + attributes + '>' + output + '</H1>'
        if self.typ == 'H2':
            return '<H2 ' + attributes + '>' + output + '</H2>'
        if self.typ == 'H3':
            return '<H3 ' + attributes + '>' + output + '</H3>'
        if self.typ == 'H4':
            return '<H4 ' + attributes + '>' + output + '</H4>'
        if self.typ == 'H5':
            return '<H5 ' + attributes + '>' + output + '</H5>'
        if self.typ == 'H6':
            return '<H6 ' + attributes + '>' + output + '</H6>'
        if self.typ == '`' or self.typ == 'code':
            return '<code>' + output + '</code>'
        return self.typ

def update(fun, output_list, i, istop, start_line):
    l, i = fun(i, istop)
    output_list += l
    return output_list, i, start_line

class State():

    def __init__(self, txt):
        self.lexed = []
        self.lexer(txt)
        self.listtoken = []
        self.links = {}


###############################################################################
#                           Define the Lexer
###############################################################################


    def lexer(self, txt):
        tokens = [' ', '\n', '*', '-', '+', '#', '[', ']', '{', '}', '(', ')', '\\', '<', '>', '`', ':', '!', '|']
        idx = 0
        length = len(txt)
        word = ''
        while idx < length:
            char = txt[idx]
            if char in tokens:
                if word != '':
                    self.lexed += [Token("word", word)]
                    word = ''
                self.lexed += [Token(char)]
            else:
                word += char
            idx += 1

        # check if there was a word in queue...
        if word != '':
            self.lexed += [Token("word", word)]
            word = ''

    def get(self, i):
        if 0 <= i and i < len(self.lexed):
            return self.lexed[i]
        return Token('none')

    def find_next(self, istart, istop, neddle):
        i = istart
        while i < istop:
            if self.get(i).typ == neddle:
                return i
            else:
                i += 1
        return -1

    def is_sequence_2(self, i, n1, n2):
        return self.get(i).typ == n1 and self.get(i+1).typ == n2

    def is_sequence_3(self, i, n1, n2, n3):
        return self.get(i).typ == n1 and self.get(i+1).typ == n2 and self.get(i+2).typ == n3

    def is_sequence_4(self, i, n1, n2, n3, n4):
        return self.get(i).typ == n1 and self.get(i+1).typ == n2 and self.get(i+2).typ == n3 and self.get(i+3).typ == n4

    def find_sequence_2(self, istart, istop, n1, n2):
        i = istart
        while i < istop:
            if self.is_sequence_2(i, n1, n2):
                return i
            else:
                i += 1
        return -1

    def find_sequence_3(self, istart, istop, n1, n2, n3):
        i = istart
        while i < istop:
            if self.is_sequence_3(i, n1, n2, n3):
                return i
            else:
                i += 1
        return -1

    def find_sequence_4(self, istart, istop, n1, n2, n3, n4):
        i = istart
        while i < istop:
            if self.is_sequence_4(i, n1, n2, n3, n4):
                return i
            else:
                i += 1
        return -1

    def find_next_duo(self, istart, istop):
        return self.find_sequence_2(istart, istop, "*", "*")

    def get_attr_dist(self, istart, istop):
        n = self.find_next(istart, istop, '{')
        m = self.find_next(istart, istop, '}')
        p = self.find_next(istart, istop, '\n')
        if 0 < p:
            if  0 < n and 0 < m and n < m and m < p:
                # we have an attribute
                return n, m, p
            # we don't have attribute : the closure of } is after the newline
            return -1, -1, p
        if  0 < n and 0 < m and n < m:
            # we have an attribute but no newline
            return n, m, -1
        return -1, -1, -1

    def newline(self, i, istop):
        t = i + 1
        while t < istop:
            typ = self.get(t).typ
            if typ == ' ':
                t += 1

            elif typ == '#':
                print("s" + str(self.get(i)))
                return [Node('\n', '', [])], t

            elif typ == '\n':

                typ = self.get(t+1).typ
                if typ == '#':
                    print("s" + str(self.get(i)))
                    return [Node('\n', '', [])], t

                if typ == '\n':
                    print("d" + str(self.get(i)))
                    return [Node('br', '', [])], t + 1

                print("s"+ str(self.get(t)))
                return [Node('\n', '', [])], t + 1

            else:
                print("s" + str(self.get(i)))
                return [Node('\n', '', [])], t
                # return self.tokenizer(t, istop, True)
        return [], istop

    def backtic(self, i, istop):
        print('`')
        n = self.find_next(i+1, istop, '`')
        if n > 0:
            return [Node('code', '', self.tokenizer(i+1, n))], n + 1
        return [Node('code', '', self.tokenizer(i+1, istop))], istop

    def bang(self, i, istop):
        print('!')
        if self.get(i+1).typ == '[':
            print('img')
            # find the address !!!
            n = self.find_next(i+2, istop, ']')
            if n > 0:

                if self.get(n+1).typ == '[':
                    m = self.find_next(n+2, istop, ']')
                    if m > 0:
                        ab, ae, _ = self.get_attr_dist(m+1, istop)
                        #idx of the link is here : n+2 -> m
                        if m + 1 == ab:
                            return [Node('img', self.interpret(self.tokenizer(n+2, m)), self.tokenizer(i+2, n), self.tokenizer(ab+1, ae))], ae + 1
                        return [Node('img', self.interpret(self.tokenizer(n+2, m)), self.tokenizer(i+2, n))], m + 1
                    else:
                        return [Node('word', 'MISSING ]')], n + 1

                if self.get(n+1).typ == '(':
                    m = self.find_next(n+2, istop, ')')
                    #idx of the link is here : n+2 -> m-1
                    if m > 0:
                        print("found link")
                        linkval = self.interpret(self.tokenizer(n+2, m))
                        print()
                        self.links[linkval] = linkval
                        print(linkval)
                        # print(self[self.interpret(self.tokenizer(n+2,m))])
                        ab, ae, _ = self.get_attr_dist(m+1, istop)
                        #addr of the link is here : n+2 -> m-1
                        if m + 1 == ab:
                            return [Node('img', self.interpret(self.tokenizer(n+2, m)), self.tokenizer(i+2, n), self.tokenizer(ab+1, ae))], ae + 1
                        return [Node('img', self.interpret(self.tokenizer(n+2, m)), self.tokenizer(i+2, n))], m + 1
                    return [Node('word', 'MISSING )')], n + 1

            else:
                return [Node('word', 'MISSING ]', self.tokenizer(i+2, istop))], istop
        else:
            return [Node('word', '!')], i + 1

    def link(self, i, istop):
        print('[')
        n = self.find_next(i+1, istop, ']')
        if 0 < n:

            if self.get(n+1).typ == '[':
                m = self.find_next(n+2, istop, ']')
                if m > 0:
                    ab, ae, _ = self.get_attr_dist(m+1, istop)
                    #idx of the link is here : n+2 -> m
                    if m + 1 == ab:
                        return [Node('a', self.interpret(self.tokenizer(n+2, m)), self.tokenizer(i+1, n), self.tokenizer(ab+1, ae))], ae + 1
                    return [Node('a', self.interpret(self.tokenizer(n+2, m)), self.tokenizer(i+1, n))], m + 1
                else:
                    return [Node('word', 'MISSING ]')], n + 1

            elif self.get(n+1).typ == '(':
                m = self.find_next(n+2, istop, ')')
                #idx of the link is here : n+2 -> m-1
                if m > 0:
                    print("found link")
                    print(self.interpret(self.tokenizer(n+2, m)))
                    self.links[self.interpret(self.tokenizer(n+2, m))] = self.interpret(self.tokenizer(n+2, m))

                    ab, ae, _ = self.get_attr_dist(m+1, istop)
                    if m + 1 == ab:
                        return [Node('a', self.interpret(self.tokenizer(n+2, m)), self.tokenizer(i+1, n), self.tokenizer(ab+1, ae))], ae + 1
                    return [Node('a', self.interpret(self.tokenizer(n+2, m)), self.tokenizer(i+1, n))], m + 1
                else:
                    return [Node('word', 'MISSING )')], n + 1

            elif self.get(n+1).typ == ':' and self.get(n+2).typ == " ":
                print("found link")
                idx = self.interpret(self.tokenizer(i+1, n))
                m = self.find_next(n+3, istop, '\n')
                #idx of the link is here : n+2 -> m-1
                if m > 0:
                    print(str(self.get(m)) + "found")

                    self.links[idx] = self.interpret(self.tokenizer(n+3, m))
                    return [], m + 1
                self.links[idx] = self.interpret(self.tokenizer(n+3, istop))
                return [], istop
            else:
                return [Node('word', '[')], i + 1


        else:
            return [Node('word', '[')] + self.tokenizer(i+1, istop)

    def stars(self, i, istop):
        print('*')
        if self.get(i+1).typ == '*':
            print('*')
            if self.get(i+2).typ == '*':
                print('*')
                n = self.find_next_duo(i+3, istop)
                if n > 0:
                    m = self.find_next(n+2, istop, '*')
                    if m > 0:
                        return [Node('i', '', [Node('b', '', self.tokenizer(i+3, n))] + self.tokenizer(n+2, m))], m + 1
                    return [Node('word', '*', []), Node('b', '', self.tokenizer(i+3, n))], n + 1
            else:
                n = self.find_next_duo(i+2, istop)
                if n > 0:
                    return [Node('b', '', self.tokenizer(i+2, n))], n + 2
                return [Node('word', '*', []), Node('word', '*', [])], n + 1
        else: # simple <i>
            n = self.find_next(i+1, istop, '*')
            if n > 0:
                return [Node('i', '', self.tokenizer(i+1, n))], n + 1
            # it was nothing
            return [Node('word', '*', [])], i + 1

    def sequence_ltd(self, i, istop):
        mid = self.find_sequence_2(i+2, istop, '|', '|')
        if mid > 0:
            end = self.find_sequence_2(mid+2, istop, '>', '>')
            if end > 0:
                return [Node('ltd', ' ', self.tokenizer(i+2, mid - 1), self.tokenizer(mid+2, end - 1))], end + 2
            return [Node('word', 'MISSING >>')], i + 2
        return [Node('word', 'MISSING ||')], i + 2

    def sequence_td_flush(self, i, istop):
        mid = self.find_sequence_2(i+3, istop, '|', '|')
        if mid > 0:
            end = self.find_sequence_2(mid+2, istop, '>', '>')
            if end > 0:
                return [Node('td', ' class="flush"', self.tokenizer(i+3, mid - 1), self.tokenizer(mid+2, end - 1))], end + 2
            return [Node('word', 'MISSING >>')], i + 2
        return [Node('word', 'MISSING ||')], i + 2

    def sequence_td_light(self, i, istop):
        mid = self.find_sequence_2(i+3, istop, '|', '|')
        if mid > 0:
            end = self.find_sequence_2(mid+2, istop, '>', '>')
            if end > 0:
                return [Node('td', '', self.tokenizer(i+3, mid - 1), self.tokenizer(mid+2, end - 1))], end + 2
            return [Node('word', 'MISSING >>')], i + 2
        return [Node('word', 'MISSING ||')], i + 2

    def sharps(self, i, istop, H):
        print('SHARP : ' + str(H))
        node_type = 'H'+str(H)
        n, m, p = self.get_attr_dist(i, istop)
        if 0 < n and 0 < m and 0 < p:
            print('found endline and attr')
            return [Node(node_type, '', self.tokenizer(i, n-1), self.tokenizer(n+1, m))], p + 1
        if 0 < p:
            print('found endline')
            return [Node(node_type, '', self.tokenizer(i, p))], p + 1
        if 0 < n and 0 < m:
            print('found attr without endline')
            return [Node(node_type, '', self.tokenizer(i, n), self.tokenizer(n+1, m))], m + 1
        print('not found endline/attr')
        return [Node(node_type, '', self.tokenizer(i, istop))], istop

    def backslashize(self):
        i = 0
        istop = len(self.lexed)
        l = []
        while i < istop:
            if self.get(i).typ == '\\':
                typ = self.get(i+1).typ
                if typ == 'word':
                    val = self.get(i+1).val
                    l += [Node('word', '\\' + val)]
                else:
                    l += [Node('word', '\\' + typ)]
                i += 1
            else:
                l += [self.get(i)]
            i += 1
        return l

    def linkRecognise(self):
        i = 0
        istop = len(self.lexed)
        l = []
        while i < istop:
            if self.get(i).typ == 'word':
                val = self.get(i).val
                if val == 'https' or val == 'http' or val == 'href="http' or val == 'href="https':
                    if self.get(i+1).typ == ':':
                        if self.get(i+2).typ == 'word':
                            l += [Node('word', val + ':' + self.get(i+2).val)]
                            i += 3
                            continue
                        # do nothing
                    # do nothing
            l += [self.get(i)]
            i += 1
        return l

    def preprocess(self):
        self.lexed = self.backslashize()
        self.lexed = self.linkRecognise()

    def tokenizer(self, istart, istop, start_line=False):
        i = istart
        H = 0
        output_list = []
        while i < istop:
            if self.is_sequence_4(i, '<', '!', '-', '-'):
                t = self.find_sequence_3(i+4, istop, '-', '-', '>')
                if t < 0: # the comment goes to the end of the text = STOP
                    return output_list
                i = t + 3
            elif self.is_sequence_2(i, '<', '<'):
                output_list, i, start_line = update(self.sequence_ltd, output_list, i, istop, start_line)
            elif self.is_sequence_3(i, '!', '<', '<'):
                output_list, i, start_line = update(self.sequence_td_flush, output_list, i, istop, start_line)
            elif self.is_sequence_3(i, ':', '<', '<'):
                output_list, i, start_line = update(self.sequence_td_light, output_list, i, istop, start_line)
            elif self.is_sequence_3(i, ' ', ' ', '\n'):
                output_list += [Node('br', '', [])]
                i = i+3
                start_line = True
            elif self.get(i).typ == ' ' and start_line:
                i += 1
            elif self.get(i).typ == ' ' and not start_line:
                output_list += [Node('word', ' ', [])]
                i += 1
            elif self.get(i).typ == '#' and start_line:
                H += 1
                i += 1
            elif H > 0:
                l, i = self.sharps(i, istop, H)
                output_list += l
                start_line = True
                H = 0
            elif self.get(i).typ == '\n':
                output_list, i, start_line = update(self.newline, output_list, i, istop, True)
            elif self.get(i).typ == 'word':
                output_list += [Node('word', self.get(i).val, [])]
                start_line = False
                i += 1
            elif self.get(i).typ == '`':
                output_list, i, start_line = update(self.backtic, output_list, i, istop, False)
            elif self.get(i).typ == '!':
                output_list, i, start_line = update(self.bang, output_list, i, istop, False)
            elif self.get(i).typ == '[':
                output_list, i, start_line = update(self.link, output_list, i, istop, False)
            elif self.get(i).typ == '*':
                output_list, i, start_line = update(self.stars, output_list, i, istop, start_line)
            else:
                output_list += [Node('word', self.get(i).typ, [])]
                i += 1
        return output_list

    def tokenize(self):
        self.preprocess()
        self.listtoken = self.tokenizer(0, len(self.lexed), True)

###############################################################################
#                           Define the Interpreter
###############################################################################
    def interpret(self, listtoken):
        output = ''
        for n in listtoken:
            output += n.interpret(self.links)
        return output

    def interpreter(self):
        return self.interpret(self.listtoken)
