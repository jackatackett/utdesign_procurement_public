
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

db.

db.users.insert({ 
    "netID" : "abc123456", 
    "email" : "student1@utdallas.edu", 
    "role" : "student", 
    "status" : "current", 
    "course" : "CS 4485.001", 
    "lastName" : "last1",
    "firstName" : "first1", 
    "projectNumbers" : [845],
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
    "membersEmails": ["manager@utdallas.edu", "jack@utdallas.edu", "xander@utdallas.edu", "monica@utdallas.edu", "marcus@utdallas.edu"],
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
    "defaultBudget": 150050,
    "availableBudget": 150050,
    "pendingBudget": 150050
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
        "quantity" : 2,
        "unitCost" : 642,
        "totalCost": 1284,
        "itemURL": "bunnyurl"
    }, {
        "description" : "Squirrel",
        "partNo" : "2",
        "quantity" : 1,
        "unitCost" : 432,
        "totalCost": 432,
        "itemURL": "squirrelurl"
    } ],
    "requestTotal": 1716,
    "history": []
})

db.requests.insert({
    "vendor": "vendor2",
    "URL": "requestor2URL",
    "justification": "",
    "status": "approved",
    "projectNumber": 844,
    "additionalInfo": "",
    "items": [{
        "description": "item1",
        "partNo": "part2",
        "quantity": 3,
        "unitCost": 600,
        "totalCost": 900,
        "itemURL": "item1url"
    }],
    "requestTotal": 900,
    "history": [
    {
        "actor": "manager@utdallas.edu",
        "timestamp": new Date("2019-03-01T09:00:00"),
        "comment": "approved",
        "oldState": "pending",
        "newState": "approved"
    }]
})
