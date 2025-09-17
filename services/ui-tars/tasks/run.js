// Simple task runner placeholder that exposes a /health endpoint via Node http
const http = require('http');
const port = 8308;

http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, {'Content-Type': 'application/json'});
    res.end(JSON.stringify({status: 'ok'}));
  } else {
    res.writeHead(200);
    res.end('ui-tars running');
  }
}).listen(port, () => {
  console.log('UI-TARS health server listening on', port);
});
