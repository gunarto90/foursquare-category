This dataset is obtained from http://snap.stanford.edu/ with some modification in the venue ID.

4 Files are used in the dataset:
- checkin.csv
- friend.csv
- user.csv
- venue.csv

### checkin.csv
user_id , unix timestamp, latitude, longitude, venue id
- user id : integer
- unix timestamp : long integer
- latitude : float
- longitude : float
- venue id : integer

### friend.csv
user 1, user 2
- user 1: integer
- user 2: integer

### user.csv
user id, row uid, #checkins, rank #checkins, #friends, rank #friends
- user id : integer
- row uid : integer
- #checkins : integer
- rank #checkins : integer
- #friends : integer
- rank #friends : integer

### venue.csv
venue id, visited frequency, popularity (visit frequency/max visit frequency), weight popularity (1-popularity)
- venue id : integer
- visited frequency : integer
- popularity : float
- weight popularity : float

### Statistics:
#Users: 58,228
#Venues: 772,966	(472,957 has checkins)
#Checkins: 4,747,281
#Invalid checkins (no coordinates) : 256,207

#Users - checkin > 0   		: 50,686
#Users - checkin > 50  		: 12,609
#Users - checkin > 100 		: 8,173
#Users - checkin > 150 		: 6,103
#Users - checkin > 200 		: 4,929
#Users - checkin > 250 		: 4,093
#Users - checkin > 300 		: 3,484
#Users - checkin > 350 		: 3,004
#Users - checkin > 400 		: 2,647
#Users - checkin > 450 		: 2,355
#Users - checkin > 500 		: 2,115
#Users - checkin > 1000 	: 1,005
#Users - checkin > 1500 	: 568
#Users - checkin > 2000 	: 342
#Users - checkin > 88 (avg)	: 8,943

#Venue - checkin > 0   		: 472,957
#Venue - checkin > 5 (avg)	: 52,183
#Venue - checkin > 10  		: 26,686
#Venue - checkin > 20  		: 13,795
#Venue - checkin > 30  		: 9,397
#Venue - checkin > 40  		: 7,259
#Venue - checkin > 50  		: 5,890
#Venue - checkin > 60  		: 4,943
#Venue - checkin > 70  		: 4,269
#Venue - checkin > 80  		: 3,785
#Venue - checkin > 90  		: 3,349
#Venue - checkin > 100 		: 3,019
#Venue - checkin > 110 		: 2,786
#Venue - checkin > 120 		: 2,550
#Venue - checkin > 130 		: 2,381
#Venue - checkin > 140 		: 2,220
#Venue - checkin > 150 		: 2,089