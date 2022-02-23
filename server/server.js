/*
    Dependencies:

    express:                Web Server Framework for nodejs
    http:                   Used to create a server
    path:                   Used to combine relative paths and show our app where its static files are, etc.
    mongoose:               Used as a wrapper for mongodb, we use it to connect to the database
    express-session:        Allows sessions which are basically how users log in to their account and stay logged in during their session
    connect-mongo:          Used for storing sessions in our database
    axios:                  Used to make requests to routes from inside socket.io, so that we can save our conversation in
                            our database
    body-parser:            Used to parse information from forms mainly, probably won't use but just in case
    socket.io:              Create a socket connection with server and client, how we send messages without reloading

    Other:

    PORT:           The default port number that the server will run on if there is no environmental
                    variable configured (which would happen when deployed on heroku)
*/

let express = require("express"),
    http    = require("http"),
    path    = require("path");
let mongoose = require("mongoose");
let session = require("express-session");
let mongoStore = require("connect-mongo");
let bodyParser = require("body-parser");
const PORT = 8000;
const app = express();
const server = http.createServer(app);
const cors = require('cors');

// initializing socket.io
const io = require("socket.io")(server);


// Example database object that we save message from client into database
const SimpleObject = require('./models/simple');


// Access to environmental variables
require('dotenv').config();


// For using c.o.r.s (Cross Origin Resource Sharing)
// So we can make request across different urls,
// which will happen when deploying live version
app.use(cors());


// Setting up conventional stuff for server
//probably won't need since likely won't be making conventional api calls to server,
// mainly realtime socket stuff
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
let routes = require('./routes/routes');
app.use('/api/', routes);


/////////////// DB initialization
let URI; // will be updated once deployed
// Connect to database
mongoose.connect(process.env.DBLOCALURI || URI,
    {
        useNewUrlParser: true,
        useUnifiedTopology: true
    })

let db = mongoose.connection;
db.on('error', console.error.bind(console, 'Error connecting to mongodb'));

db.on('connected', function() {
    console.log("Database has connected!")
});

let sessionData = session({
    secret: 'Server initialized',
    resave: true,
    saveUninitialized: true,
    store: mongoStore.create({
        mongoUrl: process.env.DBLOCALURI
    })
})
app.use(sessionData);


/////////////// SOCKET FUNCTIONS
//Listeners
const listenForDisconnected = (socket) => {
    socket.on('disconnect', () => {
        console.log(`Client with the following id has disconnected: ${socket.id}`);
    });
};

const listenForUpdatingCoordinates = (socket) => {
    socket.on('updateMyCoordinates', request => {
        const {roomID} = request;
        const {xCoord} = request;
        const {yCoord} = request;
        socket.broadcast.to(roomID).emit('updateOpponentCoordinates', {
            xCoord: xCoord,
            yCoord: yCoord
        })
    });
};

const listenForLaser = (socket) => {
    socket.on('laserShot', request => {
        const {roomID} = request;
        if (!!roomID){
            console.log(request, 'the best')
            socket.broadcast.to(roomID).emit('opponentLasered')
        }
    });
};

const listenForNewRoomJoining = (socket) => {
    socket.on('joinRoom', request => {
        const {roomID} = request;
        console.log( "socketID:", socket.id, "joining roomID:", roomID,)
        socket.join(roomID)


        // socket.broadcast.to: send to all in room except person who sent it
        socket.broadcast.to(roomID).emit("newRoomMemberJoined", {
            message: "New member has joined!"
        });
    });
};

const listenForMessageToRoom = (socket) => {
    socket.on('sendMessageToRoom', request => {
        const {roomID} = request;
        const {message} = request;
        if(!!roomID){
            socket.broadcast.to(roomID).emit('messageFromRoomMember', {
                message: message
            })
        }
    });
}

// this one will likely be deleted or changed
const listenForMessageToDB = (socket) => {
    socket.on("clientMessageToDatabase", request => {
        if (!request.username || !request.message) {
            console.log("User didn't specify both username and message! Rip to the B.I.G.");
            return;
        }

        let newDBObject = {
            username: request.username,
            message: request.message
        };

        SimpleObject.create(newDBObject).then(createdDBObject => {
            console.log("New object created! Here it is: ", createdDBObject);
        });
    });
};

const emitWelcome = (socket) => {
    socket.emit("WelcomeClient", {
        message: "Welcome to sky danger ranger! we're glad to have you here. It's gonna be a ride!"
    })
};



// main socket.io stuff
io.on('connection', socket => {

    // When client joins, emit message
    emitWelcome(socket);

    // New Client wants to join room
    listenForNewRoomJoining(socket);

    // Send message to room
    listenForMessageToRoom(socket);

    // Updating coordinates on other's end
    listenForUpdatingCoordinates(socket);

    // When a user shoots the laser
    listenForLaser(socket);

    // Client sends message to be stored in DB
    listenForMessageToDB(socket);

    // Client disconnects
    listenForDisconnected(socket)
});


/*
 * Create Server
 */
server.listen((process.env.PORT || PORT), () => {
    console.log("Sky Danger Ranger is running in port " + PORT);
});