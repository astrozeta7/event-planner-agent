const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const { spawn } = require('child_process');

const app = express();
app.use(cors());
app.use(bodyParser.json());

const DATABASE_URL = process.env.DATABASE_URL || 'postgresql://postgres:postgres@postgres:5432/event_planner_db';

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'mcp-postgres' });
});

app.post('/mcp/query', async (req, res) => {
  const { query, params } = req.body;

  try {
    const mcp = spawn('npx', [
      '-y',
      '@modelcontextprotocol/server-postgres',
      DATABASE_URL
    ]);

    const request = {
      jsonrpc: '2.0',
      method: 'tools/call',
      params: {
        name: 'query',
        arguments: { sql: query, params: params || [] }
      },
      id: Date.now()
    };

    mcp.stdin.write(JSON.stringify(request) + '\n');
    mcp.stdin.end();

    let output = '';
    let errorOutput = '';

    mcp.stdout.on('data', (data) => {
      output += data.toString();
    });

    mcp.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    mcp.on('close', (code) => {
      if (code !== 0) {
        console.error('MCP Error:', errorOutput);
        return res.status(500).json({
          error: 'MCP server error',
          details: errorOutput
        });
      }

      try {
        const lines = output.trim().split('\n');
        const response = JSON.parse(lines[lines.length - 1]);
        res.json(response);
      } catch (error) {
        console.error('Parse error:', error.message);
        console.error('Output:', output);
        res.status(500).json({
          error: 'Failed to parse MCP response',
          details: error.message
        });
      }
    });
  } catch (error) {
    console.error('Request error:', error);
    res.status(500).json({
      error: 'Internal server error',
      details: error.message
    });
  }
});

app.post('/mcp/execute', async (req, res) => {
  const { query, params } = req.body;

  try {
    const mcp = spawn('npx', [
      '-y',
      '@modelcontextprotocol/server-postgres',
      DATABASE_URL
    ]);

    const request = {
      jsonrpc: '2.0',
      method: 'tools/call',
      params: {
        name: 'execute',
        arguments: { sql: query, params: params || [] }
      },
      id: Date.now()
    };

    mcp.stdin.write(JSON.stringify(request) + '\n');
    mcp.stdin.end();

    let output = '';
    let errorOutput = '';

    mcp.stdout.on('data', (data) => {
      output += data.toString();
    });

    mcp.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    mcp.on('close', (code) => {
      if (code !== 0) {
        console.error('MCP Error:', errorOutput);
        return res.status(500).json({
          error: 'MCP server error',
          details: errorOutput
        });
      }

      try {
        const lines = output.trim().split('\n');
        const response = JSON.parse(lines[lines.length - 1]);
        res.json(response);
      } catch (error) {
        console.error('Parse error:', error.message);
        res.status(500).json({
          error: 'Failed to parse MCP response',
          details: error.message
        });
      }
    });
  } catch (error) {
    console.error('Request error:', error);
    res.status(500).json({
      error: 'Internal server error',
      details: error.message
    });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`MCP PostgreSQL HTTP server listening on port ${PORT}`);
  console.log(`Database: ${DATABASE_URL}`);
});
