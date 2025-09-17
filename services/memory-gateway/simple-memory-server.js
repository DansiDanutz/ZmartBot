const express = require('express');
const fs = require('fs').promises;
const path = require('path');

const app = express();
const PORT = 8295;
const DATA_DIR = path.join(__dirname, 'data');

// Ensure data directory exists
async function ensureDataDir() {
  try {
    await fs.mkdir(DATA_DIR, { recursive: true });
  } catch (error) {
    console.error('Error creating data directory:', error);
  }
}

// Simple in-memory storage
const memory = new Map();

// Middleware
app.use(express.json());

// Health endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Store memory
app.post('/memories', async (req, res) => {
  try {
    const { id, content, tags = [], metadata = {} } = req.body;
    const memoryId = id || `mem_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const memoryEntry = {
      id: memoryId,
      content,
      tags,
      metadata,
      timestamp: new Date().toISOString()
    };
    
    memory.set(memoryId, memoryEntry);
    
    // Also save to file for persistence
    const filePath = path.join(DATA_DIR, `${memoryId}.json`);
    await fs.writeFile(filePath, JSON.stringify(memoryEntry, null, 2));
    
    res.json({ id: memoryId, status: 'stored' });
  } catch (error) {
    console.error('Error storing memory:', error);
    res.status(500).json({ error: 'Failed to store memory' });
  }
});

// Search memories
app.get('/search', async (req, res) => {
  try {
    const { q: query, tags, k = 8 } = req.query;
    
    if (!query) {
      return res.status(400).json({ error: 'Query parameter is required' });
    }
    
    const results = [];
    const queryLower = query.toLowerCase();
    
    for (const [id, memoryItem] of memory.entries()) {
      if (!memoryItem || !memoryItem.content) {
        console.log('Skipping invalid memory item:', memoryItem);
        continue;
      }
      const contentLower = memoryItem.content.toLowerCase();
      const tagsLower = (memoryItem.tags || []).map(tag => tag.toLowerCase());
      
      // Simple text matching
      if (contentLower.includes(queryLower) || 
          tagsLower.some(tag => tag.includes(queryLower))) {
        
        // Check tag filter if provided
        if (tags) {
          const filterTags = tags.split(',').map(t => t.toLowerCase());
          if (!filterTags.some(filterTag => 
            tagsLower.some(tag => tag.includes(filterTag)))) {
            continue;
          }
        }
        
        results.push({
          id: memoryItem.id,
          content: memoryItem.content,
          tags: memoryItem.tags,
          metadata: memoryItem.metadata,
          timestamp: memoryItem.timestamp,
          score: contentLower.includes(queryLower) ? 0.9 : 0.7
        });
      }
    }
    
    // Sort by score and limit results
    results.sort((a, b) => b.score - a.score);
    const limitedResults = results.slice(0, parseInt(k));
    
    res.json(limitedResults);
  } catch (error) {
    console.error('Error searching memories:', error);
    res.status(500).json({ error: 'Failed to search memories' });
  }
});

// Get all memories
app.get('/memories', (req, res) => {
  const allMemories = Array.from(memory.values());
  res.json(allMemories);
});

// Delete memory
app.delete('/memories/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    if (memory.has(id)) {
      memory.delete(id);
      
      // Also delete file
      const filePath = path.join(DATA_DIR, `${id}.json`);
      try {
        await fs.unlink(filePath);
      } catch (error) {
        // File might not exist, that's ok
      }
      
      res.json({ id, status: 'deleted' });
    } else {
      res.status(404).json({ error: 'Memory not found' });
    }
  } catch (error) {
    console.error('Error deleting memory:', error);
    res.status(500).json({ error: 'Failed to delete memory' });
  }
});

// Load existing memories on startup
async function loadExistingMemories() {
  try {
    const files = await fs.readdir(DATA_DIR);
    const jsonFiles = files.filter(file => file.endsWith('.json'));
    
    for (const file of jsonFiles) {
      try {
        const filePath = path.join(DATA_DIR, file);
        const content = await fs.readFile(filePath, 'utf8');
        const memoryEntry = JSON.parse(content);
        memory.set(memoryEntry.id, memoryEntry);
      } catch (error) {
        console.error(`Error loading memory file ${file}:`, error);
      }
    }
    
    console.log(`Loaded ${memory.size} existing memories`);
  } catch (error) {
    console.error('Error loading existing memories:', error);
  }
}

// Start server
async function startServer() {
  await ensureDataDir();
  await loadExistingMemories();
  
  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Memory server running on port ${PORT}`);
    console.log(`Health check: http://localhost:${PORT}/health`);
  });
}

startServer().catch(console.error);
