
conn = new Mongo();
db = conn.getDB("procurement");

db.users.insert({ 
    "_id" : ObjectId("5c707dbb81f1f375f6e1c4a4"), 
    "netID" : "(string)", 
    "email" : "oddrun@utdallas.edu", 
    "role" : "admin", 
    "status" : "current", 
    "course" : "(string)", 
    "lastName" : "Mahaffey", 
    "firstName" : "Oddrun", 
    "groupID" : "(string)", 
    "password" : BinData(0,"LB334CiGuSIEpWpUJewb1ykHOkiqWEX7xIYeg9KN7yE="), 
    "salt" : BinData(0,"uh2SlTzR1UhYzJ03Qr4UGsHExgRAXNOxJRNUFOFzouA=") 
})
