-- Create mydatabase
CREATE DATABASE IF NOT EXISTS mydatabase;

-- Create myuser
CREATE USER IF NOT EXISTS 'myuser'@'%' IDENTIFIED BY 'insecure';

-- Let myuser use mydatabase
GRANT ALL PRIVILEGES ON mydatabase.* TO 'myuser'@'%';

-- Apply permissions
FLUSH PRIVILEGES;
