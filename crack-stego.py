#!/usr/bin/env python2
import subprocess
import sys
import itertools
import string

def cat_file(s):
    print "Message: " + open(s).read()

def run_openstego(word):
    cmd = ["openstego", "extract", "-sf", "hide.png", "-p", word]
    outp = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    if "Extracted" in outp:
        print "[+] found bro!"
        print outp
        cat_file("message.txt")
        return True

    return False

def main():
    movies = open('movies.txt','r').read()
    lines = []
    words = []

    lines = movies.split("\n")
    words = movies.split()

    # brute each word
    print "[i] bruting all words in movies.txt"
    for word in words:
        if run_openstego(word):
            print "Password: %s" % word
            sys.exit(0)

    # brute each movie verbatim
    print "[i] bruting all lines in the movies.txt"
    for line in lines:
        if run_openstego(line):
            print "Password: %s" % line
            sys.exit(0)

    # brute a four letter word
    print "[i] about to brute all four letter comboz..."
    for b in itertools.product(string.ascii_lowercase + string.ascii_uppercase + string.digits, repeat=4):
        if run_openstego(''.join(b)):
            print "Password: %s" % ''.join(b)
            sys.exit(0)


main()
