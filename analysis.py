#!/usr/bin/env python

# Custom import
import json
import foursquare
import re
import time
import os
import errno
import sys

from pympler import asizeof
from datetime import date
from datetime import datetime
import time

# Setting variables
dataset = 'brighkite'
global f_config, f_categories, f_users, f_checkins, f_friends, f_venues, f_profile
f_config = 'config_secret.json'
f_categories = 'categories.csv'
f_users = dataset + '/user.csv'
f_checkins = dataset + '/checkin_small.csv'
f_friends = dataset + '/friend.csv'
f_venues = dataset + '/venue.csv'
f_profile = 'users' # folder for each user profile

search_area = 500 # in meters
category_parent = 1
input_folder = ''

# Global variables
users = {}
categories = {}
cat_int = {}

# Class and Functions
class User:
    cat_dis = []
    def __init__(self, _id):
        self.id = _id
        self.timeslots = []
        self.init_categories = 0
        self.total_cat_dis = 0
        self.total_checkins = 0
        # Init timeslots
        for i in range(0, 24):
            self.timeslots.append(0)
    def init_cat_dis(self, num):
        for i in range(0, num):
            self.cat_dis.append(0)
        self.init_categories = 1
    def increment_category(self, cid):
        self.cat_dis[cat_int[cid]] += 1
        self.total_cat_dis += 1
    def add_checkin(self, unixtime, cat_ids):
        self.total_checkins += 1
        # Deal with time slots
        stime = datetime.fromtimestamp(unixtime)
        #print stime
        # Deal with categories
        if self.init_categories == 0:
            self.init_cat_dis(len(categories))
        for cid in cat_ids:
            self.increment_category(cid)
            # Handle parent categories
            cc = categories[cid]
            level = cc.level
            if category_parent == 1:
                while level > 0 or cc is not None:
                    cc = cc.parent
                    if cc is None:
                        break
                    cid = cc.id
                    self.increment_category(cid)
                    level -= 1
            pass

class Category:
    def __init__(self, _id, _name, _parent, _level):
        self.id = _id
        self.name = _name
        self.parent = _parent # reference to Category instance
        self.level = _level

# Utility functions
def show_object_size(obj, name):
    size = asizeof.asizeof(obj)
    print 'Size of {0} is : {1} Bytes'.format(name, size)

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def write_to_file(filename, text, append=True):
    if append:
        mode = 'a'
    else:
        mode = 'w'
    with open(filename, mode) as fw:
        fw.write(str(text) + '\n')

# Foursquare related
def auth_4sq():
    # Construct the client object
    client = foursquare.Foursquare(client_id=client_id, client_secret=client_secret)
    # Build the authorization url for your app
    auth_uri = client.oauth.auth_url()
    return client

def search_venue_categories(lat, lon):
    ll = str(lat) + ',' + str(lon)
    b = client.venues.search(params={'ll': ll, 'radius':search_area})
    venues = b['venues']
    cat_ids = []
    for v in venues:
        cats = v['categories']
        for cat in cats:
            cat_id = cat['id']
            cat_ids.append(cat_id)
    return cat_ids

# Init functions
def init_categories(filename):
    counter = 0
    with open(filename, 'r') as fr:
        for line in fr:
            split = line.strip().split(',')
            _id = split[0]
            _name = split[1]
            _parent_id = split[2]
            _level = int(split[3])
            cat_int[_id] = counter
            parent = None
            if _parent_id != '':
                parent = categories[_parent_id]
            categories[_id] = Category(_id, _name, parent, _level)
            counter = counter + 1
            if counter % 10000 == 0:
                print 'Processing %d categories' % counter
    print 'Initialized {0} categories'.format(counter)

def init_users(filename):
    counter = 0
    with open(filename, 'r') as fr:
        for line in fr:
            split = line.strip().split(',')
            _id = int(split[0])
            u = User(_id)
            # u.init_cat_dis(len(cat_int))
            users[_id] = u
            counter = counter + 1
            if counter % 10000 == 0:
                print 'Processing %d users' % counter
    print 'Initialized {0} users'.format(counter)

def init_checkins(filename):
    print 'Initializing checkins ...'
    # global checkins
    # checkins = {}
    counter = 0
    with open(filename, 'r') as fr:
        for line in fr:
            try:
                split = line.strip().split(',')
                uid = int(split[0])
                time = long(split[1])
                lat = float(split[2])
                lon = float(split[3])
                if lat == 0.0 or lon == 0.0 :
                    continue
                cat_ids = search_venue_categories(lat, lon)
                users[uid].add_checkin(time, cat_ids)
                counter = counter + 1
                if counter % 1000 == 0:
                    print '[{0}] Processing {1} checkins'.format(str(datetime.now()), counter)
            except Exception as ex:
                print 'Init checkins - Exception [counter = {0}]: {1}'.format(counter, ex)
    print 'Initialized {0} checkins'.format(counter)

# Configuration
def load_config(config_secret):
    global client_id
    global client_secret
    with open(config_secret, 'r') as cred:
        json_str = cred.read()
        json_data = json.loads(json_str)
        client_id = json_data['client_id']
        client_secret = json_data['client_secret']
    print 'Configuration loaded'

def init_folder():
    if input_folder != '':
        global f_config, f_categories, f_users, f_checkins, f_friends, f_venues, f_profile
        f_config        = input_folder + '/' + f_config
        f_categories    = input_folder + '/' + f_categories
        f_users         = input_folder + '/' + f_users
        f_checkins      = input_folder + '/' + f_checkins
        f_friends       = input_folder + '/' + f_friends
        f_venues        = input_folder + '/' + f_venues
        f_profile       = input_folder + '/' + f_profile

# Main function
if __name__ == '__main__':
    arglen = len(sys.argv)
    if arglen == 2:
        input_folder = sys.argv[1]
        init_folder()
        print input_folder
    else :
        print 'No input folder provided, use <blank> as default'
    start_time = time.time()
    ### Initialize foursquare API
    load_config(f_config)  # Load config_secret.json for credential
    client = auth_4sq()
    ### Initialize categories on 4sq
    init_categories(f_categories)
    ### Initialize users
    init_users(f_users)
    ### Assign check-ins
    init_checkins(f_checkins)

    make_sure_path_exists(f_profile)

    counter = 0
    for uid, user in users.iteritems():
        counter += 1
        if counter % 10000 == 0:
            print 'Processing %d users' % counter
        if user.total_cat_dis > 0:
            f_out = '{0}/{1}.txt'.format(f_profile, uid)
            result = re.sub('(\[)|(\])', '', str(user.cat_dis))
            write_to_file(f_out, result, False)
            #print uid
            #print user.total_cat_dis
            #print user.cat_dis

    # show_object_size(categories, 'categories')
    # show_object_size(users, 'users')
    
    print('Program finished in {0} seconds'.format(time.time() - start_time))