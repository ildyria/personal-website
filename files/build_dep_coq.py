#!/usr/bin/env python3

# Copyright (c) 2016 Benoit Viguier
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to
# do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#
# Script to search for and build coq files in the right order...
#
from sys import argv
from sys import exit
import subprocess
import os.path
import re


def print_help(list_arg):
	print(list_arg[0] + " [-f] files [-i folders] [-e folders]")
	print("----------------------------------------")
	print("")
	print("basic usage: " + list_arg[0] + " files")
	print("")
	print("options:")
	print("-f : files to parse")
	print("-i : folders of allowed sources")
	print("-e : folders of excluded sources (won't be parsed)")
	exit()


def parse_args(i, list_arg, list_path, list_include, list_exclude, action):
	if i < len(list_arg):
		if list_arg[i] == "-f":
			parse_args(i + 1, list_arg, list_path, list_include, list_exclude, "f")
		elif list_arg[i] == "-i":
			parse_args(i + 1, list_arg, list_path, list_include, list_exclude, "i")
		elif list_arg[i] == "-e":
			parse_args(i + 1, list_arg, list_path, list_include, list_exclude, "e")
		elif action == "f":
			list_path.append(list_arg[i])
			parse_args(i + 1, list_arg, list_path, list_include, list_exclude, action)
		elif action == "i":
			list_include.append(list_arg[i])
			parse_args(i + 1, list_arg, list_path, list_include, list_exclude, action)
		elif action == "e":
			list_exclude.append(list_arg[i])
			parse_args(i + 1, list_arg, list_path, list_include, list_exclude, action)
		elif list_arg[i] == "-h":
			print_help(list_arg)
		else:
			print("I don't know what to do")
			exit()


path_to_file = []
# this folders will be included or excluded during the parsing
# the idea here is to avoid trying the compilation of Coq Libraries...
include_folders = []
exclude_folders = ['Coq']

parse_args(1, argv, path_to_file, include_folders, exclude_folders, "f")

if not path_to_file:
	print_help(argv)

if not include_folders:
	include_folders = [x for x in os.listdir() if os.path.isdir(x) and x not in exclude_folders and x[0] != "."]

print("Files to parse:")
print(path_to_file)
print("Folders to include:")
print(include_folders)
print("Folders to exclude:")
print(exclude_folders)

def remove_comments(string):
	str_res = ""
	open_comment = 0
	open_simple_app = 0
	open_double_app = 0
	i = 0
	while i < len(string):
		# start a comment if we are not in a string
		if string[i] == '(' and string[i + 1] == '*' and open_simple_app == 0 and open_double_app == 0:
			open_comment += 1
			i += 2
		# start a comment if we are not in a string
		elif string[i] == '*' and string[i + 1] == ')' and open_simple_app == 0 and open_double_app == 0:
			open_comment = max(0, open_comment - 1)
			i += 2
		# we are not in a comment
		elif open_comment == 0:
			str_res += string[i]

			# if we find a simple appostrophe
			if string[i] == "'" and open_double_app == 0:
				open_simple_app = 1 - open_simple_app

			# if we find a double appostrophe
			if string[i] == '"' and open_simple_app == 0:
				open_double_app = 1 - open_double_app

			i += 1
		elif open_comment > 0:
			i += 1
		else:
			print("WTF are we doing here ?")
			quit()

	return str_res


def find_imports(list_words, i):
	if i < len(list_words):
		if list_words[i] == 'Import' or list_words[i] == 'Export':
			return find_imports(list_words, i + 1)

		elif list_words[i].find('.') > 0:
			return [list_words[i]] + find_imports(list_words, i + 1)

		else:
			return find_imports(list_words, i + 1)
	else:
		return []


def find_dependance_of_file(file):
	depend_on = []
	require_import_export = []
	# print("file : " + file)
	with open(file, "r") as f:
		content = remove_comments(f.read()).splitlines()

		for line in content:
			line = line.strip()
			if line and line.startswith('Require'):
				require_import_export += find_imports(line.split(), 0)

	# print("\tfound : " + '\n\t\t'.join(require_import_export))

	for imports in require_import_export:
		fwords = imports.rstrip(".").split(".")
		# print(fwords)
		fword = fwords[0]
		if len(fwords) == 1:
			depend_on += [imports.rstrip(".").replace(".", "/") + ".v"]
		elif fword in include_folders and fword not in exclude_folders:
			depend_on += [imports.rstrip(".").replace(".", "/") + ".v"]

	# print("\tincld : " + '\n\t\t'.join(depend_on))
	return depend_on


def find_in_list(list_to_search, value):
	for i in range(len(list_to_search)):
		if list_to_search[i] == value:
			return i
	return -1


def do_search(list_done, to_parse):
	# make sure the file do exist
	if os.path.isfile(to_parse):

		# make sure we haven't parsed it yet !
		if to_parse not in list_done:

			depends_on = find_dependance_of_file(to_parse)

			# print("------------------------------")
			# print(to_parse)
			# print("-----")
			# print(depends_on)

			# make sure that we won't parse it twice, just push it to the bottom of the list
			index_insert_to = len(list_done)
			for depend in depends_on:
				idx = find_in_list(list_done, depend)
				if -1 < idx < index_insert_to:
					index_insert_to = idx

			list_done.insert(index_insert_to, to_parse)
			for depend in depends_on:
				do_search(list_done, depend)


# dependency_order = doSearch([], ["name.of.the.file"],0)
dependency_order = []
for files in path_to_file:
	do_search(dependency_order, files)

print("LIST TO COMPILE")
dependency_order.reverse()
print("\n".join(dependency_order))

# print(dependency_order)
print("START COMPILING")

for dep in dependency_order:
	cmd = "coqc " + dep
	print(cmd)
	subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
