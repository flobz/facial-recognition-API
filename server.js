const html = __dirname + '/public';

const port = 8081;

const domain = "localhost";

// Express
const bodyParser = require('body-parser');
const compression = require('compression');
const expectCt = require('expect-ct');
const cors = require('cors');
const express = require('express');
var app = express();
const routes = require('express').Router();

app.use(function(req, res, next) {
    var err = null;
    try {
        decodeURIComponent(req.path)
    }
    catch(e) {
        err = e;
    }
    if (err){
        console.log(err, req.url);
        return res.redirect(['https://', req.get('Host'), '/login'].join(''));
    }
    next();
});

app.use(cors({
    origin:"*"
}));

app
    .use(compression())
    .use(bodyParser.json())
    // Static content
    .use(express.static(html))
    // Default route
    .use(routes)
    // Start server
    .listen(port, function () {
        console.log('Port: ' + port);
        console.log('Html: ' + html);
    });

routes.get('*', function (req, res) {
    res.sendFile(html + '/index.html');
});
