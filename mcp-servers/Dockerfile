# MCP HTTP Service for Cloud Run
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application files
COPY . .

# Expose port (Cloud Run will set PORT env variable)
EXPOSE 8080

# Start the HTTP wrapper
CMD ["node", "http-wrapper.js"]