const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const { spawn } = require('child_process');

const app = express();
app.use(cors());
app.use(bodyParser.json());

const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID;
const GOOGLE_CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET;

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'mcp-gdrive' });
});

app.post('/mcp/upload', async (req, res) => {
  const { filename, content, mimeType, folderId } = req.body;

  try {
    const mcp = spawn('npx', [
      '-y',
      '@modelcontextprotocol/server-gdrive'
    ], {
      env: {
        ...process.env,
        GOOGLE_CLIENT_ID,
        GOOGLE_CLIENT_SECRET
      }
    });

    const request = {
      jsonrpc: '2.0',
      method: 'tools/call',
      params: {
        name: 'upload_file',
        arguments: {
          filename,
          content,
          mimeType: mimeType || 'application/octet-stream',
          folderId: folderId || null
        }
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

app.post('/mcp/list', async (req, res) => {
  const { folderId, query } = req.body;

  try {
    const mcp = spawn('npx', [
      '-y',
      '@modelcontextprotocol/server-gdrive'
    ], {
      env: {
        ...process.env,
        GOOGLE_CLIENT_ID,
        GOOGLE_CLIENT_SECRET
      }
    });

    const request = {
      jsonrpc: '2.0',
      method: 'tools/call',
      params: {
        name: 'list_files',
        arguments: {
          folderId: folderId || null,
          query: query || null
        }
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
  console.log(`MCP Google Drive HTTP server listening on port ${PORT}`);
});
