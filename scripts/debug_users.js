
conn = new Mongo();
db = conn.getDB("procurement");


db.users.insert({
    "netID" : "N/A", 
    "email" : "admin@utdallas.edu", 
    "role" : "admin", 
    "status" : "current", 
    "course" : "N/A", 
    "lastName" : "Mahaffey", 
    "firstName" : "Oddrun", 
    "groupID" : "N/A", 
    "password" : BinData(0,"LB334CiGuSIEpWpUJewb1ykHOkiqWEX7xIYeg9KN7yE="), 
    "salt" : BinData(0,"uh2SlTzR1UhYzJ03Qr4UGsHExgRAXNOxJRNUFOFzouA=") 
})


db.users.insert({ 
    "netID" : "dvj170000", 
    "email" : "manager@utdallas.edu", 
    "role" : "manager", 
    "status" : "current", 
    "course" : "CS 4485.001", 
    "lastName" : "Joshi",
    "firstName" : "Dhwanika", 
    "groupID" : "844", 
    "password" : BinData(0,"LB334CiGuSIEpWpUJewb1ykHOkiqWEX7xIYeg9KN7yE="), 
    "salt" : BinData(0,"uh2SlTzR1UhYzJ03Qr4UGsHExgRAXNOxJRNUFOFzouA=") 
})


db.users.insert({ 
    "netID" : "jat161230", 
    "email" : "student@utdallas.edu", 
    "role" : "student", 
    "status" : "current", 
    "course" : "CS 4485.001", 
    "lastName" : "Tackett",
    "firstName" : "Jack", 
    "groupID" : "844", 
    "password" : BinData(0,"LB334CiGuSIEpWpUJewb1ykHOkiqWEX7xIYeg9KN7yE="), 
    "salt" : BinData(0,"uh2SlTzR1UhYzJ03Qr4UGsHExgRAXNOxJRNUFOFzouA=") 
})
