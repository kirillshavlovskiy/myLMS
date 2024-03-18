const serve = require('serve');
const http = require('http');

const server = serve('build', {
    host: 'localhost',
    port: 5000,
});

server.use((req, res, next) => {
    if (req.url.endsWith('.js')) {
        res.setHeader('Content-Type', 'application/javascript');
    }
    next();
});