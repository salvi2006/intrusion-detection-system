const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' } });

const PORT = process.env.PORT || 5000;

// Store recent alerts in memory
const alerts = [];

app.use(cors());
app.use(express.json({ limit: '10mb' })); // Support base64 images
app.use(express.static(path.join(__dirname, 'public')));

// Alerts API
app.post('/api/alerts', (req, res) => {
    const alert = req.body;
    
    // Add server-side timestamp if missing
    if (!alert.timestamp) {
        alert.timestamp = new Date().toISOString();
    }
    
    console.log(`[ALERT] Intrusion detected from ${alert.device_id} at ${alert.timestamp}`);
    
    // Store alert
    alerts.unshift(alert);
    if (alerts.length > 50) alerts.pop(); // Keep last 50
    
    // Broadcast to dashboard
    io.emit('new_alert', alert);
    
    res.status(201).json({ message: 'Alert received', alert });
});

app.get('/api/alerts', (req, res) => {
    res.json(alerts);
});

// Setup WebSocket connection
io.on('connection', (socket) => {
    console.log('Dashboard connected:', socket.id);
    // Send history on connect
    socket.emit('alert_history', alerts);
    
    socket.on('disconnect', () => {
        console.log('Dashboard disconnected:', socket.id);
    });
});

server.listen(PORT, () => {
    console.log(`Backend server running on http://localhost:${PORT}`);
});
