# Zmart Trading Professional Dashboard

This is the OFFICIAL dashboard for the ZmartBot platform.

## Structure

```
professional_dashboard/
├── src/                 # React source code
│   ├── components/      # React components
│   ├── services/        # API services
│   └── App.tsx         # Main app component
├── dist/               # Built production app
├── package.json        # Dependencies
└── vite.config.ts      # Vite configuration
```

## How to Build

```bash
# Install dependencies
npm install

# Build for production
npm run build

# Development (if needed)
npm run dev
```

## How to Start

The dashboard is served by the Python server on port 3400:

```bash
# From backend/zmart-api directory
python professional_dashboard_server.py
```

## Access Points

- Dashboard: http://localhost:3400
- Backend API: http://localhost:8000

## Important Notes

- This dashboard is served by Python, NOT by Vite dev server
- Port 3400 is EXCLUSIVELY for this dashboard
- The Python server proxies API requests to port 8000
- Always build before deploying: `npm run build`
