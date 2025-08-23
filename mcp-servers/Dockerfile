# MCP Servers Dockerfile for Cloud Run
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Set environment variables for Cloud Run
ENV PORT=8080
ENV NODE_ENV=production

# Expose port
EXPOSE 8080

# Run the HTTP wrapper
CMD ["node", "http-wrapper.js"]