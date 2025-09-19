// ZmartyChat Backend Server
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const nodemailer = require('nodemailer');

const app = express();
const PORT = 5000;
const JWT_SECRET = 'zmarty-secret-key-2024';

// Middleware
app.use(cors());
app.use(express.json());

// Create Database
const db = new sqlite3.Database('./zmarty.db');

// Create Users Table
db.run(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT,
    name TEXT,
    country TEXT,
    tier TEXT DEFAULT 'free',
    provider TEXT,
    email_verified INTEGER DEFAULT 0,
    verification_code TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`);

// Store verification codes in memory (for demo)
const verificationCodes = {};

// Email transporter (for demo, just console log)
const sendEmail = (to, code) => {
  console.log(`
    ================================================
    EMAIL SENT TO: ${to}
    VERIFICATION CODE: ${code}
    ================================================
  `);
  return true;
};

// Routes

// Register
app.post('/api/register', async (req, res) => {
  const { email, provider } = req.body;

  try {
    // Check if user exists
    db.get('SELECT * FROM users WHERE email = ?', [email], async (err, user) => {
      if (user) {
        return res.status(400).json({ error: 'User already exists' });
      }

      // Generate verification code
      const code = Math.floor(100000 + Math.random() * 900000).toString();
      verificationCodes[email] = code;

      // Insert user
      db.run(
        'INSERT INTO users (email, provider, verification_code) VALUES (?, ?, ?)',
        [email, provider, code],
        function(err) {
          if (err) {
            return res.status(500).json({ error: 'Failed to create user' });
          }

          // Send verification email
          sendEmail(email, code);

          res.json({
            message: 'User created. Check email for verification code.',
            userId: this.lastID,
            code: code // For demo purposes
          });
        }
      );
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Verify Email
app.post('/api/verify-email', (req, res) => {
  const { email, code } = req.body;

  db.get(
    'SELECT * FROM users WHERE email = ? AND verification_code = ?',
    [email, code],
    (err, user) => {
      if (!user) {
        return res.status(400).json({ error: 'Invalid verification code' });
      }

      // Update user as verified
      db.run(
        'UPDATE users SET email_verified = 1, verification_code = NULL WHERE id = ?',
        [user.id],
        (err) => {
          if (err) {
            return res.status(500).json({ error: 'Failed to verify email' });
          }

          // Generate JWT token
          const token = jwt.sign(
            { userId: user.id, email: user.email },
            JWT_SECRET,
            { expiresIn: '30d' }
          );

          res.json({
            message: 'Email verified successfully',
            token,
            user: {
              id: user.id,
              email: user.email,
              tier: user.tier
            }
          });
        }
      );
    }
  );
});

// Update Profile
app.post('/api/update-profile', (req, res) => {
  const { email, name, country, tier } = req.body;

  db.run(
    'UPDATE users SET name = ?, country = ?, tier = ? WHERE email = ?',
    [name, country, tier, email],
    function(err) {
      if (err) {
        return res.status(500).json({ error: 'Failed to update profile' });
      }

      if (this.changes === 0) {
        return res.status(404).json({ error: 'User not found' });
      }

      res.json({ message: 'Profile updated successfully' });
    }
  );
});

// Social Login
app.post('/api/social-login', (req, res) => {
  const { email, provider, name } = req.body;

  // Check if user exists
  db.get('SELECT * FROM users WHERE email = ?', [email], (err, user) => {
    if (user) {
      // User exists, just login
      const token = jwt.sign(
        { userId: user.id, email: user.email },
        JWT_SECRET,
        { expiresIn: '30d' }
      );

      return res.json({
        message: 'Login successful',
        token,
        user: {
          id: user.id,
          email: user.email,
          name: user.name,
          tier: user.tier
        }
      });
    }

    // Create new user
    db.run(
      'INSERT INTO users (email, provider, name, email_verified) VALUES (?, ?, ?, 1)',
      [email, provider, name],
      function(err) {
        if (err) {
          return res.status(500).json({ error: 'Failed to create user' });
        }

        const token = jwt.sign(
          { userId: this.lastID, email: email },
          JWT_SECRET,
          { expiresIn: '30d' }
        );

        res.json({
          message: 'Account created successfully',
          token,
          user: {
            id: this.lastID,
            email: email,
            name: name,
            tier: 'free'
          }
        });
      }
    );
  });
});

// Get User
app.get('/api/user/:email', (req, res) => {
  const { email } = req.params;

  db.get('SELECT * FROM users WHERE email = ?', [email], (err, user) => {
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({
      id: user.id,
      email: user.email,
      name: user.name,
      country: user.country,
      tier: user.tier,
      provider: user.provider,
      email_verified: user.email_verified,
      created_at: user.created_at
    });
  });
});

// Get All Users (Admin)
app.get('/api/users', (req, res) => {
  db.all('SELECT id, email, name, country, tier, provider, email_verified, created_at FROM users', (err, users) => {
    if (err) {
      return res.status(500).json({ error: 'Failed to fetch users' });
    }
    res.json({ users, count: users.length });
  });
});

// Resend Code
app.post('/api/resend-code', (req, res) => {
  const { email } = req.body;

  // Generate new code
  const code = Math.floor(100000 + Math.random() * 900000).toString();

  db.run(
    'UPDATE users SET verification_code = ? WHERE email = ?',
    [code, email],
    (err) => {
      if (err) {
        return res.status(500).json({ error: 'Failed to resend code' });
      }

      sendEmail(email, code);
      res.json({
        message: 'New code sent',
        code: code // For demo
      });
    }
  );
});

// Start server
app.listen(PORT, () => {
  console.log(`
  =========================================
  ZmartyChat Backend Server Running!
  =========================================

  URL: http://localhost:${PORT}

  Endpoints:
  - POST /api/register
  - POST /api/verify-email
  - POST /api/update-profile
  - POST /api/social-login
  - POST /api/resend-code
  - GET  /api/user/:email
  - GET  /api/users

  Database: SQLite (./zmarty.db)
  =========================================
  `);
});