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
- visited frequency : integer <not put yet>
- latitude: float
- longitude: float

### Statistics:
#Users: 
#Venues: 	( has checkins)
#Checkins: 
#Invalid checkins (no coordinates) : 

#Users - checkin > 0   		: 
#Users - checkin > 50  		: 
#Users - checkin > 100 		: 
#Users - checkin > 150 		: 
#Users - checkin > 200 		: 
#Users - checkin > 250 		: 
#Users - checkin > 300 		: 
#Users - checkin > 350 		: 
#Users - checkin > 400 		: 
#Users - checkin > 450 		: 
#Users - checkin > 500 		: 
#Users - checkin > 1000 	: 
#Users - checkin > 1500 	: 
#Users - checkin > 2000 	: 
#Users - checkin > 88 (avg)	: 

#Venue - checkin > 0   		: 
#Venue - checkin > 5 (avg)	: 
#Venue - checkin > 10  		: 
#Venue - checkin > 20  		: 
#Venue - checkin > 30  		: 
#Venue - checkin > 40  		: 
#Venue - checkin > 50  		: 
#Venue - checkin > 60  		: 
#Venue - checkin > 70  		: 
#Venue - checkin > 80  		: 
#Venue - checkin > 90  		: 
#Venue - checkin > 100 		: 
#Venue - checkin > 110 		: 
#Venue - checkin > 120 		: 
#Venue - checkin > 130 		: 
#Venue - checkin > 140 		: 
#Venue - checkin > 150 		: 