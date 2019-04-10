//first drop the original database (inside mongo client):
//use procurement
//db.dropDatabase()
//then run this (outside mongo client):
//mongo scripts/debug_users.js

conn = new Mongo();
db = conn.getDB("procurement");
db.dropDatabase();

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
    "netID" : "man123456", 
    "email" : "manager2@utdallas.edu", 
    "role" : "manager", 
    "status" : "current", 
    "course" : "CS 4485.001", 
    "lastName" : "man2",
    "firstName" : "man2", 
    "projectNumbers" : [845, 846],
    "password" : BinData(0,"LB334CiGuSIEpWpUJewb1ykHOkiqWEX7xIYeg9KN7yE="), 
    "salt" : BinData(0,"uh2SlTzR1UhYzJ03Qr4UGsHExgRAXNOxJRNUFOFzouA=") 
})

db.users.insert({ 
    "netID" : "jat123456", 
    "email" : "jack@utdallas.edu", 
    "role" : "student", 
    "status" : "current", 
    "course" : "CS 4485.001", 
    "lastName" : "Tackett",
    "firstName" : "Jack", 
    "projectNumbers" : [844],
    "password" : BinData(0,"LB334CiGuSIEpWpUJewb1ykHOkiqWEX7xIYeg9KN7yE="), 
    "salt" : BinData(0,"uh2SlTzR1UhYzJ03Qr4UGsHExgRAXNOxJRNUFOFzouA=") 
})

db.users.insert({ 
    "netID" : "ajw123456", 
    "email" : "xander@utdallas.edu", 
    "role" : "student", 
    "status" : "current", 
    "course" : "CS 4485.001", 
    "lastName" : "Wong",
    "firstName" : "Xander", 
    "projectNumbers" : [844],
    "password" : BinData(0,"LB334CiGuSIEpWpUJewb1ykHOkiqWEX7xIYeg9KN7yE="), 
    "salt" : BinData(0,"uh2SlTzR1UhYzJ03Qr4UGsHExgRAXNOxJRNUFOFzouA=") 
})

db.users.insert({ 
    "netID" : "msn123456", 
    "email" : "monica@utdallas.edu", 
    "role" : "student", 
    "status" : "current", 
    "course" : "CS 4485.001", 
    "lastName" : "Neivandt",
    "firstName" : "Monica", 
    "projectNumbers" : [844],
    "password" : BinData(0,"LB334CiGuSIEpWpUJewb1ykHOkiqWEX7xIYeg9KN7yE="), 
    "salt" : BinData(0,"uh2SlTzR1UhYzJ03Qr4UGsHExgRAXNOxJRNUFOFzouA=") 
})

db.users.insert({ 
    "netID" : "mwd123456", 
    "email" : "marcus@utdallas.edu", 
    "role" : "student", 
    "status" : "current", 
    "course" : "CS 4485.001", 
    "lastName" : "Deng",
    "firstName" : "Marcus", 
    "projectNumbers" : [844],
    "password" : BinData(0,"LB334CiGuSIEpWpUJewb1ykHOkiqWEX7xIYeg9KN7yE="), 
    "salt" : BinData(0,"uh2SlTzR1UhYzJ03Qr4UGsHExgRAXNOxJRNUFOFzouA=") 
})

db.users.insert({ 
    "netID" : "abc123456", 
    "email" : "student1@utdallas.edu", 
    "role" : "student", 
    "status" : "current", 
    "course" : "CS 4485.001", 
    "lastName" : "last1",
    "firstName" : "first1", 
    "projectNumbers" : [844],
    "password" : BinData(0,"LB334CiGuSIEpWpUJewb1ykHOkiqWEX7xIYeg9KN7yE="), 
    "salt" : BinData(0,"uh2SlTzR1UhYzJ03Qr4UGsHExgRAXNOxJRNUFOFzouA=") 
})

db.users.insert({ 
    "netID" : "def123456", 
    "email" : "student2@utdallas.edu", 
    "role" : "student", 
    "status" : "current", 
    "course" : "CS 4485.001", 
    "lastName" : "last2",
    "firstName" : "first2", 
    "projectNumbers" : [845],
    "password" : BinData(0,"LB334CiGuSIEpWpUJewb1ykHOkiqWEX7xIYeg9KN7yE="), 
    "salt" : BinData(0,"uh2SlTzR1UhYzJ03Qr4UGsHExgRAXNOxJRNUFOFzouA=") 
})

db.users.insert({ 
    "netID" : "ghi123456", 
    "email" : "student3@utdallas.edu", 
    "role" : "student", 
    "status" : "current", 
    "course" : "CS 4485.001", 
    "lastName" : "last3",
    "firstName" : "first3", 
    "projectNumbers" : [845, 846],
    "password" : BinData(0,"LB334CiGuSIEpWpUJewb1ykHOkiqWEX7xIYeg9KN7yE="), 
    "salt" : BinData(0,"uh2SlTzR1UhYzJ03Qr4UGsHExgRAXNOxJRNUFOFzouA=") 
})

db.projects.insert({
    "projectNumber": 844,
    "sponsorName": "UTDesign",
    "projectName": "UTDesign Gettit",
    "membersEmails": ["manager@utdallas.edu", "jack@utdallas.edu", "xander@utdallas.edu", "monica@utdallas.edu", "marcus@utdallas.edu", "student1@utdallas.edu"],
    "defaultBudget": 200000,
    "availableBudget": 199100,
    "pendingBudget": 197384
})

db.projects.insert({
    "projectNumber": 845,
    "sponsorName": "sponsor1",
    "projectName": "project2",
    "membersEmails": ["manager2@utdallas.edu", "student1@utdallas.edu", "student2@utdallas.edu", "student3@utdallas.edu"],
    "defaultBudget": 150050,
    "availableBudget": 150050,
    "pendingBudget": 150050
})

db.projects.insert({
    "projectNumber": 846,
    "sponsorName": "sponsor2",
    "projectName": "project3",
    "membersEmails": ["manager2@utdallas.edu", "student3@utdallas.edu"],
    "defaultBudget": 100000,
    "availableBudget": 100000,
    "pendingBudget": 100000
})

db.sequence.insert({
    "name" : "requests",
    "number" : 3
})

db.requests.insert({
    "history" : [{
        "newState" : "pending", "actor" : "student1@utdallas.edu", "oldState" : "saved", "timestamp" : ISODate("2019-04-09T23:42:16.388Z"), "comment" : "submitted by student1@utdallas.edu"
    }],
    "requestSubtotal" : 1200,
    "projectNumber" : 844,
    "requestTotal" : 1950,
    "URL" : "vendor1.com",
    "status" : "pending",
    "vendor" : "vendor1",
    "manager" : "manager@utdallas.edu",
    "additionalInfo" : "Very important",
    "items" : [{
            "quantity" : 2,
            "totalCost" : 600,
            "partNo" : "item1",
            "itemURL" : "vendor1.com/items/item1",
            "unitCost" : 300,
            "description" : "item1"
        }, {
            "quantity" : 3,
            "totalCost" : 600,
            "partNo" : "item2",
            "itemURL" : "vendor1.com/items/item2",
            "unitCost" : 200,
            "description" : "item2"
    }],
    "justification" : "Important parts",
    "requestNumber" : 1
})

db.requests.insert({
    "history" : [{
        "newState" : "pending",
        "actor" : "student1@utdallas.edu",
        "oldState" : "saved",
        "timestamp" : new Date("2019-04-09T23:43:00.939Z"),
        "comment" : "submitted by student1@utdallas.edu"
    }],
    "requestSubtotal" : 3400,
    "projectNumber" : 844,
    "requestTotal" : 3400,
    "URL" : "vendor2.org",
    "status" : "pending",
    "vendor" : "vendor2",
    "manager" : "manager@utdallas.edu",
    "additionalInfo" : "We need them",
    "items" : [{
            "quantity" : 5,
            "totalCost" : 2500,
            "partNo" : "item1",
            "itemURL" : "item1url",
            "unitCost" : 500,
            "description" : "item1"
        }, {
            "quantity" : 3,
            "totalCost" : 900,
            "partNo" : "item2",
            "itemURL" : "item2url",
            "unitCost" : 300,
            "description" : "item2"
    }],
    "justification" : "More parts",
    "requestNumber" : 2
})
