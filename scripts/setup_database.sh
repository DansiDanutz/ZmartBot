#!/bin/bash

echo "🗄️  ZmartBot Database Setup"
echo "=========================="

# Check if PostgreSQL is running
echo "📋 Checking PostgreSQL status..."
if ! pg_isready -h localhost >/dev/null 2>&1; then
    echo "❌ PostgreSQL is not running. Starting it..."
    brew services start postgresql@15 || {
        echo "❌ Failed to start PostgreSQL. Please start it manually:"
        echo "   brew services start postgresql@15"
        exit 1
    }
    sleep 3
fi

echo "✅ PostgreSQL is running"

# Create user
echo "👤 Creating database user..."
psql -h localhost -U postgres -c "CREATE USER zmart_user WITH PASSWORD 'zmart_password_dev';" 2>/dev/null || {
    echo "ℹ️  User zmart_user may already exist"
    psql -h localhost -U postgres -c "ALTER USER zmart_user PASSWORD 'zmart_password_dev';" || {
        echo "❌ Failed to set user password"
        exit 1
    }
}

# Create database
echo "🗃️  Creating database..."
createdb -h localhost -U postgres -O zmart_user zmart_platform 2>/dev/null || {
    echo "ℹ️  Database zmart_platform may already exist"
}

# Grant privileges
echo "🔐 Granting privileges..."
psql -h localhost -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE zmart_platform TO zmart_user;" || {
    echo "❌ Failed to grant privileges"
    exit 1
}

# Initialize schema
echo "📊 Initializing database schema..."
psql -h localhost -U zmart_user -d zmart_platform -f database_init.sql || {
    echo "❌ Failed to initialize database schema"
    exit 1
}

# Test connection
echo "🧪 Testing database connection..."
psql -h localhost -U zmart_user -d zmart_platform -c "SELECT COUNT(*) FROM users;" >/dev/null || {
    echo "❌ Database connection test failed"
    exit 1
}

echo "✅ Database setup completed successfully!"
echo ""
echo "📋 Database Details:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: zmart_platform"
echo "   User: zmart_user"
echo "   Password: zmart_password_dev"
echo ""
echo "🚀 You can now start the backend server!"