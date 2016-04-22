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