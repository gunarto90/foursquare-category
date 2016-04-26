#!/usr/bin/env python

### Extract the category in foursquare html file to be presented in csv file
### https://developer.foursquare.com/categorytree
### CSV file include 4 columns: category id, category name, parent category id, category level (tree depth)
### Output file: categories.csv (default name)

import re
import urllib2
import os

FOURSQUARE_CATEGORY_LINK = 'https://developer.foursquare.com/categorytree'

def extractCategories(html_text, output_file):
    b_name      = 0
    b_id        = 0
    c_name      = ''
    c_id        = ''
    level       = 0
    parent      = {}
    parent[0]   = ''    # Root
    max_level   = 0
    # Loop through the lines
    os.remove(output_file)
    for line in html_text.splitlines():
        temp = line.strip()
        if b_name == 1:
            b_name = 0
            temp = temp.replace('&amp;', 'and')
            c_name = temp
            #print c_name
            continue
        elif b_id == 1:
            b_id = 0
            temp = re.sub('<(\/)?tt>', '', temp)
            c_id = temp
            #print c_id
            # Set parent id to table
            parent[level] = c_id
            continue
        if c_name != '' and c_id != '':
            c_parent = ''
            try :
                c_parent = parent[level-1]
            except:
                pass
            with open(output_file, 'a') as fw:
                fw.write('{0},{1},{2},{3}\n'.format(c_id, c_name, c_parent, level))
            c_name = ''
            c_id = ''
        elif temp == '<div class="name">':
            b_name = 1
        elif temp == '<div class="id">':
            b_id = 1
        # Check level to identify parents
        if temp == '<ul class="level-1">':
            level = 1
        elif temp == '<ul class="level-2">':
            level = 2
        elif temp == '<ul class="level-3">':
            level = 3
        elif temp == '<ul class="level-4">':
            level = 4
        elif temp == '<ul class="level-5">':
            level = 5
        elif temp == '</ul>':
            level = level - 1
        if max_level < level :
            max_level = level
#        print max_level

# Main function
if __name__ == '__main__':
    response = urllib2.urlopen(FOURSQUARE_CATEGORY_LINK)
    html = response.read()
    extractCategories(html, 'categories.csv')
    print('Program finished')