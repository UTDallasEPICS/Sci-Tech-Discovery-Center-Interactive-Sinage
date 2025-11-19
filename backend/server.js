const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors()); // Allows your React app (port 5173) to talk to this server (port 8000)

let clients = [];

// 1. The SSE Endpoint (This is what your React App connects to)
app.get('/api/events', (req, res) => {
  // Mandatory headers for SSE
  const headers = {
    'Content-Type': 'text/event-stream',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache'
  };
  res.writeHead(200, headers);

  // Add this client to our list so we can send them messages later
  const clientId = Date.now();
  const newClient = {
    id: clientId,
    res
  };
  clients.push(newClient);

  // Send a confirmation message on connection (optional)
  // Note: The format must always be "data: <content>\n\n"
  res.write(`data: ${JSON.stringify({ status: "Connected to SSE" })}\n\n`);

  // Remove client when they close the connection
  req.on('close', () => {
    console.log(`${clientId} Connection closed`);
    clients = clients.filter(client => client.id !== clientId);
  });
});

// 2. The Trigger Endpoint (Hit this to simulate the event!)
app.get('/trigger-event', (req, res) => {
  // Create the mock data you expect in your frontend
  const mockData = { 
    action: "switch_screen", 
    videoUrl: "some_video.mp4",
    message: "The sensor was triggered!"
  };

  // Send this data to all connected clients (your React app)
  clients.forEach(client => {
    client.res.write(`data: ${JSON.stringify(mockData)}\n\n`);
  });

  console.log("Event pushed to frontend!");
  res.send("Event Triggered! Check your React window.");
});

const PORT = 8000;
app.listen(PORT, () => {
  console.log(`Mock server running at http://localhost:${PORT}`);
});