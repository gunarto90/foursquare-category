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
f_checkins = dataset + '/checkin_multiuser.csv'
f_friends = dataset + '/friend.csv'
f_venues = dataset + '/venue.csv'
f_profile = 'users' # folder for each user profile

search_area = 50 # in meters
category_parent = 1
input_folder = ''

USING_PARENT_CATEGORY = True
USING_CATEGORY = False
USING_CATEGORY_TIME = False
USING_CATEGORY_DAY = False
USING_CATEGORY_DAY_TIME = False
USING_TIME = False
USING_DAY_TIME = False

# Global variables
users = {}
categories = {}
cat_int = {}

# Class and Functions
class User:
    def __init__(self, _id):
        self.id = _id               # User id
        self.cat_dis = []           # 4sq categories
        self.cat_dis_tod = []       # 4sq categories - time of day
        self.cat_dis_dow = []       # 4sq categories - day of week
        self.cat_dis_dow_tod = []   # 4sq categories - time of day + day of week
        self.timeslots = []         # Time of day
        self.all_timeslots = []     # Day of week + Time of day
        self.init_categories = 0    # Flag on category initialization
        self.total_cat_dis = 0      # number of distributions
        self.total_checkins = 0     # number of checkins

        # Init timeslots
        if USING_TIME:
            self.init_time()
        # Init all timeslots
        if USING_DAY_TIME:
            self.init_day_time()
    def init_time(self):
        for i in range(0, 24):
            self.timeslots.append(0)
    def init_day_time(self):
        for i in range(0, 7):
            self.all_timeslots.append([])
            for j in range(0, 24):
                self.all_timeslots[i].append(0)
    def init_cat_dis(self, num):
        for i in range(0, num):
            self.cat_dis.append(0)
        self.init_categories = 1
    def increment_category(self, cid):
        self.cat_dis[cat_int[cid]] += 1
        self.total_cat_dis += 1
    def increment_time(self, time, dtime):
        if USING_TIME:
            self.timeslots[time.hour] += 1
        if USING_DAY_TIME:
            self.all_timeslots[dtime.weekday()][time.hour] += 1
    def add_checkin(self, unixtime, cat_ids):
        self.total_checkins += 1
        # Deal with time slots
        if USING_TIME or USING_DAY_TIME:
            time = datetime.fromtimestamp(unixtime)
            dtime = date.fromtimestamp(unixtime)
            self.increment_time(time, dtime)
        #print stime
        # Deal with categories
        if USING_CATEGORY or USING_CATEGORY_DAY or USING_CATEGORY_TIME or USING_CATEGORY_DAY_TIME:
            if self.init_categories == 0:
                self.init_cat_dis(len(categories))
            for cid in cat_ids:
                self.increment_category(cid)
                # Handle parent categories
                cc = categories[cid]
                level = cc.level
                if USING_PARENT_CATEGORY:
                    while level > 0 or cc is not None:
                        cc = cc.parent
                        if cc is None:
                            break
                        cid = cc.id
                        self.increment_category(cid)
                        level -= 1

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
    cat_ids = []
    ll = str(lat) + ',' + str(lon)
    b = client.venues.search(params={'intent':'browse', 'll': ll, 'radius':search_area})
    venues = b['venues']
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
    show_object_size(categories, 'categories')

def init_users(filename):
    counter = 0
    with open(filename, 'r') as fr:
        for line in fr:
            split = line.strip().split(',')
            _id = int(split[0])
            u = User(_id)
            #u.init_cat_dis(len(cat_int))
            users[_id] = u
            counter = counter + 1
            if counter % 10000 == 0:
                print 'Processing %d users' % counter
    print 'Initialized {0} users'.format(counter)
    show_object_size(users, 'users')

def init_checkins(filename):
    print 'Initializing checkins ...'
    # global checkins
    # checkins = {}
    counter = 0
    scheckins = []
    with open(filename, 'r') as fr:
        for line in fr:
            scheckins.append(line)
    print 'Initialized {0} checkins'.format(len(scheckins))
    show_object_size(scheckins, 'scheckins')
    for line in scheckins:
        try:
            split = line.strip().split(',')
            uid = int(split[0])
            time = long(split[1])
            lat = float(split[2])
            lon = float(split[3])
            if lat == 0.0 or lon == 0.0 :
                continue
            cat_ids = []
            if USING_CATEGORY or USING_CATEGORY_DAY or USING_CATEGORY_TIME or USING_CATEGORY_DAY_TIME:
                cat_ids = search_venue_categories(lat, lon)
            users[uid].add_checkin(time, cat_ids)
            counter = counter + 1
            if counter % 100 == 0:
                print '[{0}] Processing {1} of {2} checkins ({3}%)'.format(str(datetime.now()), counter, len(scheckins), counter*100.0/len(scheckins))
        except Exception as ex:
            print 'Init checkins - Exception [counter = {0}]: ({1}) {2}'.format(counter, type(ex), ex)

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
            #print uid
            print user.total_checkins
            print user.total_cat_dis
            #print user.total_cat_dis
            #print user.cat_dis
            # Categories
            if USING_CATEGORY:
                f_out = '{0}/{1}_cat.txt'.format(f_profile, uid)
                result = re.sub('(\[)|(\])', '', str(user.cat_dis))
                write_to_file(f_out, result, False)
            # Time slots
            if USING_TIME:
                f_out = '{0}/{1}_time.txt'.format(f_profile, uid)
                result = re.sub('(\[)|(\])', '', str(user.timeslots))
                write_to_file(f_out, result, False)
            # Time slots
            if USING_DAY_TIME:
                f_out = '{0}/{1}_alltime.txt'.format(f_profile, uid)
                result = re.sub('(\[)|(\])', '', str(user.all_timeslots))
                write_to_file(f_out, result, False)           
            # show_object_size(categories, 'categories')
            # show_object_size(user, 'user')
    
    print('Program finished in {0} seconds'.format(time.time() - start_time))