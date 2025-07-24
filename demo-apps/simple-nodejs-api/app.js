const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

// Middleware - functions that run on every request
app.use(express.json());

// Routes - different URLs the API responds to
app.get('/', (req, res) => {
  res.json({ 
    message: 'Hello from Agentic IaC Simple Node.js API!',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy',
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

app.get('/api/info', (req, res) => {
  res.json({
    app: 'simple-nodejs-api',
    description: 'Demo application for Agentic IaC system',
    endpoints: ['/', '/health', '/api/info'],
    environment: process.env.NODE_ENV || 'development'
  });
});

// Error handling - what to do when something goes wrong
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// 404 handler - what to do when URL doesn't exist
app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

// Start the server
if (require.main === module) {
  app.listen(port, () => {
    console.log(`🚀 Simple Node.js API listening at http://localhost:${port}`);
    console.log(`📊 Health check available at http://localhost:${port}/health`);
  });
}

module.exports = app;
