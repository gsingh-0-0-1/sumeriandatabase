const express = require('express')
var fs = require('fs');

const app = express()
const port = 8080

app.use(express.static('public'));

app.get("/", (req, res) => {
	res.sendFile("public/templates/main.html", {root: __dirname})
})

app.listen(port, '0.0.0.0')