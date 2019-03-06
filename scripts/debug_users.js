
conn = new Mongo();
db = conn.getDB("procurement");


db.users.insert({
    "email" : "admin@utdallas.edu", 
    "role" : "admin", 
    "status" : "current", 
    "lastName" : "Mahaffey", 
    "firstName" : "Oddrun",
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
    "projectNumbers" : [844],
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
    "projectNumbers" : [844],
    "password" : BinData(0,"LB334CiGuSIEpWpUJewb1ykHOkiqWEX7xIYeg9KN7yE="), 
    "salt" : BinData(0,"uh2SlTzR1UhYzJ03Qr4UGsHExgRAXNOxJRNUFOFzouA=") 
})

db.requests.insert({
    "vendor" : "Bunning's warehouse",
    "URL" : "https://www.bunnings.com.au/",
    "justification" : "They're fluffy!",
    "status" : "pending",
    "projectNumber" : 844,
    "additionalInfo" : "I want them",
    "items" : [ {
        "description" : "Bunny",
        "partNo" : "1",
        "quantity" : "2",
        "unitCost" : 6.42
    }, {
        "description" : "Squirrel",
        "partNo" : "2",
        "quantity" : "1",
        "unitCost" : 4.32
    } ]
})