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
f_config = 'config.json'
f_secret = 'config_secret.json'

#search_area = 50 # in meters
input_folder = ''

# Global variables
users = {}
categories = {}
cat_int = {}
venues = {}

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
        
class Venue:
    def __init__(self, _id, _count, _lat, _lon):
        self.id = _id
        self.count = _count
        self.lat = _lat
        self.lon = _lon

# Utility functions
def show_object_size(obj, name):
    size = asizeof.asizeof(obj)
    print 'Size of {0} is : {1:,} Bytes'.format(name, size)

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
def auth_4sq(client_id, client_secret):
    # Construct the client object
    client = foursquare.Foursquare(client_id=client_id, client_secret=client_secret)
    # Build the authorization url for your app
    auth_uri = client.oauth.auth_url()
    return client

def search_venue_categories(lat, lon, search_radius):
    cat_ids = []
    ll = str(lat) + ',' + str(lon)
    try:
        b = client.venues.search(params={'intent':'browse', 'll': ll, 'radius':search_radius, 'limit':50})
        venues = b['venues']
        for v in venues:
            cats = v['categories']
            for cat in cats:
                cat_id = cat['id']
                cat_ids.append(cat_id)
    except Exception as ex:
        print 'Search Venue Categories Exception : {0}'.format(ex)
        with open('error.log', 'a') as fout:
            fout.write('Search Venue Categories Exception : {0}\n'.format(ex))
        if str(ex) == 'Quota exceeded':
            print 'Let the program sleep for 10 minutes'
            time.sleep(600) # Delay 10 minutes for another crawler
            return None
    return cat_ids
    
def process_venue_categories(cat_ids, cat_int, categories, USING_CATEGORY, USING_CATEGORY_DAY, USING_CATEGORY_TIME, USING_CATEGORY_DAY_TIME):
    category_distribution = []
    # Deal with categories
    if USING_CATEGORY or USING_CATEGORY_DAY or USING_CATEGORY_TIME or USING_CATEGORY_DAY_TIME:
        count_assign = 0
        for i in range(0, len(categories)):
            category_distribution.append(0)
        for cid in cat_ids:
            count_assign += 1
            category_distribution[cat_int[cid]] += 1
            # Handle parent categories
            cc = categories[cid]
            level = cc.level
            if USING_PARENT_CATEGORY:
                while level > 0 or cc is not None:
                    cc = cc.parent
                    if cc is None:
                        break
                    count_assign += 1
                    category_distribution[cat_int[cc.id]] += 1
                    level -= 1
        # Normalize category_distribution
        if count_assign > 0:
            for i in range(0, len(category_distribution)):
                x = float(category_distribution[i]) / count_assign
                category_distribution[i] = x
    return category_distribution

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
    
def init_venues(filename):
    counter = 0
    with open(filename, 'r') as fr:
        for line in fr:
            split = line.strip().split(',')
            _id = int(split[0])
            _count = int(split[1])
            _lat = float(split[2])
            _lon = float(split[3])
            venues[_id] = Venue(_id, _count, _lat, _lon)
            counter = counter + 1
            if counter % 10000 == 0:
                print 'Processing %d venues' % counter
    print 'Initialized {0} venues'.format(counter)
    show_object_size(venues, 'venues')

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

def init_checkins(filename, search_radius):
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
    while counter < len(scheckins):
        line = scheckins[counter]
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
                cat_ids = search_venue_categories(lat, lon, search_radius)
            if cat_ids == None:
                continue
            users[uid].add_checkin(time, cat_ids)
            counter = counter + 1
            if counter % 100 == 0:
                print '[{0}] Processing {1} of {2} checkins ({3}%)'.format(str(datetime.now()), counter, len(scheckins), counter*100.0/len(scheckins))
        except Exception as ex:
            print 'Init checkins - Exception [counter = {0}]: ({1}) {2}'.format(counter, type(ex), ex)

# Configuration
def load_config(config_file):
    global USING_PARENT_CATEGORY, USING_CATEGORY, USING_CATEGORY_TIME, USING_CATEGORY_DAY, USING_CATEGORY_DAY_TIME, USING_TIME, USING_DAY_TIME
    with open(config_file, 'r') as file:
        json_str = file.read()
        json_data = json.loads(json_str)
        USING_PARENT_CATEGORY = json_data['USING_PARENT_CATEGORY']
        USING_CATEGORY = json_data['USING_CATEGORY']
        USING_CATEGORY_TIME = json_data['USING_CATEGORY_TIME']
        USING_CATEGORY_DAY = json_data['USING_CATEGORY_DAY']
        USING_CATEGORY_DAY_TIME = json_data['USING_CATEGORY_DAY_TIME']
        USING_TIME = json_data['USING_TIME']
        USING_DAY_TIME = json_data['USING_DAY_TIME']
        search_radius = json_data['search_radius']
        dataset = json_data['dataset']
        f_output_folder = json_data['f_output_folder']
        f_categories = json_data['f_categories']
        f_users = json_data['f_users']
        f_checkins = json_data['f_checkins']
        f_friends = json_data['f_friends']
        f_venues = json_data['f_venues']
    return dataset, search_radius, f_output_folder, f_categories, f_users, f_checkins, f_friends, f_venues

def load_secret(config_secret):
    with open(config_secret, 'r') as cred:
        json_str = cred.read()
        json_data = json.loads(json_str)
        client_id = json_data['client_id']
        client_secret = json_data['client_secret']
    print 'Configuration loaded'
    return client_id, client_secret

def init_config_folder(input_folder, f_config, f_secret):
    if input_folder != '':
        f_config    = input_folder + '/' + f_config
        f_secret    = input_folder + '/' + f_secret
        return f_config, f_secret

def init_files(input_folder, f_categories, f_output_folder, f_users, f_checkins, f_friends, f_venues):
    global dataset
    if input_folder != '':
        input_folder += '/'
    f_categories        = input_folder + f_categories
    f_output_folder     = input_folder + f_output_folder
    f_users             = input_folder + dataset + '/' + f_users
    f_checkins          = input_folder + dataset + '/' + f_checkins
    f_friends           = input_folder + dataset + '/' + f_friends
    f_venues            = input_folder + dataset + '/' + f_venues
    return f_categories, f_output_folder, f_users, f_checkins, f_friends, f_venues

# Main function
if __name__ == '__main__':
    arglen = len(sys.argv)
    MODE_OPTS = ['explore', 'analyze']
    if arglen > 1:
        MODE = sys.argv[1]
        input_folder = sys.argv[2]
        if MODE == MODE_OPTS[0]:
            output_venue_dis = sys.argv[3]
        f_config, f_secret = init_config_folder(input_folder, f_config, f_secret)
        print 'Working directory: %s' % input_folder
    else :
        print 'Please use these parameters to run the program : python analysis.py <MODE> <Input Folder> <Other parameters>'
        exit(0)
    start_time = time.time()
    ### Load configuration in json file
    dataset, search_radius, f_output_folder, f_categories, f_users, f_checkins, f_friends, f_venues = load_config(f_config)
    ### Initialize foursquare API
    client_id, client_secret = load_secret(f_secret)  # Load config_secret.json for credential
    f_categories, f_output_folder, f_users, f_checkins, f_friends, f_venues = init_files(input_folder, f_categories, f_output_folder, f_users, f_checkins, f_friends, f_venues)
    client = auth_4sq(client_id, client_secret)
    ### Initialize categories on 4sq
    init_categories(f_categories)
    ### Initialize venues
    if MODE == MODE_OPTS[0]:
        init_venues(f_venues)
    ### Initialize users
    if MODE == MODE_OPTS[1]:
        init_users(f_users)
    ### Assign check-ins
    if MODE == MODE_OPTS[1]:
        init_checkins(f_checkins, search_radius)

    make_sure_path_exists(f_output_folder)

    counter = 0
    if MODE == MODE_OPTS[0]:
        if USING_CATEGORY or USING_CATEGORY_DAY or USING_CATEGORY_TIME or USING_CATEGORY_DAY_TIME:
            try:
                os.remove(f_output_folder + '/' + output_venue_dis)
            except:
                pass
            query_time = time.time()
            str_out = ''
            for vid, venue in venues.iteritems():
                counter += 1
                if counter % 4500 == 0: # 5000 is the limit
                    process_time = int(time.time() - query_time)
                    print 'Processing {0} venues in {1} seconds'.format(counter, process_time)
                    #wait_time = 3600 - process_time + 1
                    #if wait_time > 0:
                    #    print 'Need to wait %d seconds ... ' % wait_time
                    #    time.sleep(wait_time)
                    #    print 'Continue querying ...'
                try:
                    if venue.count > 0:
                        cat_ids = None
                        while cat_ids == None:
                            cat_ids = search_venue_categories(venue.lat, venue.lon, search_radius)
                            if cat_ids == None:
                                process_time = int(time.time() - query_time)
                                print 'Processing {0} venues in {1} seconds'.format(counter, process_time)
                        category_distribution = process_venue_categories(cat_ids, cat_int, categories, USING_CATEGORY, USING_CATEGORY_DAY, USING_CATEGORY_TIME, USING_CATEGORY_DAY_TIME)
                        # Handle outputs
                        # print category_distribution
                        cats = ','.join(str(x) for x in category_distribution)
                        str_out += '{0},{1}\n'.format(vid , cats)
                    if counter % 10 == 0:
                        with open(f_output_folder + '/' + output_venue_dis, 'a') as fout:
                            fout.write(str_out)
                        str_out = ''
                        process_time = int(time.time() - query_time)
                        print '[{0}] Processing {1} venues in {2} seconds ({3:.2f}% completed)'.format(str(datetime.now()), counter, process_time, float(counter*100.0/len(venues)))
                except Exception as ex:
                    print ex
            # Write remaining output
            if str_out != '':
                with open(f_output_folder + '/' + output_venue_dis, 'a') as fout:
                    fout.write(str_out)
    elif MODE == MODE_OPTS[1]:
        for uid, user in users.iteritems():
            counter += 1
            if counter % 10000 == 0:
                print 'Processing %d users' % counter
            if user.total_cat_dis > 0:
                #print uid
                #print user.total_checkins
                #print user.total_cat_dis
                #print user.total_cat_dis
                #print user.cat_dis
                # Categories
                if USING_CATEGORY:
                    f_out = '{0}/{1}_cat.txt'.format(f_output_folder, uid)
                    result = re.sub('(\[)|(\])', '', str(user.cat_dis))
                    write_to_file(f_out, result, False)
                # Time slots
                if USING_TIME:
                    f_out = '{0}/{1}_time.txt'.format(f_output_folder, uid)
                    result = re.sub('(\[)|(\])', '', str(user.timeslots))
                    write_to_file(f_out, result, False)
                # Time slots
                if USING_DAY_TIME:
                    f_out = '{0}/{1}_alltime.txt'.format(f_output_folder, uid)
                    result = re.sub('(\[)|(\])', '', str(user.all_timeslots))
                    write_to_file(f_out, result, False)           
                # show_object_size(categories, 'categories')
                # show_object_size(user, 'user')
    
    print('Program finished in {0} seconds'.format(time.time() - start_time))