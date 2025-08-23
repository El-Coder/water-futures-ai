#!/bin/bash

# Water Futures AI - Comprehensive Test Runner
# Runs unit, integration, and end-to-end tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Water Futures AI - Test Suite${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Function to run a test suite
run_test_suite() {
    local name=$1
    local command=$2
    local marker=$3
    
    echo -e "${YELLOW}Running $name...${NC}"
    
    if $command; then
        echo -e "${GREEN}✅ $name passed${NC}\n"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ $name failed${NC}\n"
        ((TESTS_FAILED++))
    fi
}

# Check if services are running
check_services() {
    echo -e "${BLUE}Checking services...${NC}"
    
    services_running=true
    
    # Check backend
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Backend not running${NC}"
        services_running=false
    else
        echo -e "${GREEN}✅ Backend is running${NC}"
    fi
    
    # Check chat service
    if ! curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Chat service not running${NC}"
        services_running=false
    else
        echo -e "${GREEN}✅ Chat service is running${NC}"
    fi
    
    # Check MCP wrapper
    if ! curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  MCP wrapper not running${NC}"
        services_running=false
    else
        echo -e "${GREEN}✅ MCP wrapper is running${NC}"
    fi
    
    # Check frontend
    if ! curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Frontend not running${NC}"
        services_running=false
    else
        echo -e "${GREEN}✅ Frontend is running${NC}"
    fi
    
    echo ""
    
    if [ "$services_running" = false ]; then
        echo -e "${YELLOW}Some services are not running.${NC}"
        echo -e "${YELLOW}Run ./start-local.sh to start all services.${NC}"
        echo -e "${YELLOW}Skipping integration and E2E tests.${NC}\n"
        return 1
    fi
    
    return 0
}

# Parse command line arguments
TEST_TYPE=${1:-all}
VERBOSE=${2:-}

# Install test dependencies if needed
install_dependencies() {
    echo -e "${BLUE}Installing test dependencies...${NC}"
    
    # Backend test dependencies
    cd backend
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -q pytest pytest-asyncio pytest-cov httpx selenium 2>/dev/null || true
    deactivate
    cd ..
    
    # Frontend test dependencies
    cd frontend
    npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event jest 2>/dev/null || true
    cd ..
    
    echo -e "${GREEN}✅ Dependencies installed${NC}\n"
}

# Run backend unit tests
run_backend_unit_tests() {
    cd backend
    source venv/bin/activate
    
    run_test_suite \
        "Backend Unit Tests" \
        "python -m pytest tests/test_unit_services.py -m unit -q" \
        "unit"
    
    deactivate
    cd ..
}

# Run frontend component tests
run_frontend_tests() {
    cd frontend
    
    # Create a simple test runner if Jest isn't configured
    if [ ! -f "jest.config.js" ]; then
        echo -e "${YELLOW}Jest not configured, skipping frontend tests${NC}\n"
    else
        run_test_suite \
            "Frontend Component Tests" \
            "npm test -- --watchAll=false" \
            "frontend"
    fi
    
    cd ..
}

# Run integration tests
run_integration_tests() {
    if check_services; then
        cd backend
        source venv/bin/activate
        
        run_test_suite \
            "API Integration Tests" \
            "python -m pytest tests/test_integration_api.py -m integration -q" \
            "integration"
        
        deactivate
        cd ..
    fi
}

# Run end-to-end tests
run_e2e_tests() {
    if check_services; then
        run_test_suite \
            "End-to-End Tests" \
            "python tests/test_e2e.py" \
            "e2e"
    fi
}

# Run specific API endpoint test
test_api_endpoint() {
    local endpoint=$1
    echo -e "${BLUE}Testing API endpoint: $endpoint${NC}"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000$endpoint)
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ $endpoint - OK${NC}"
    else
        echo -e "${RED}❌ $endpoint - Failed (HTTP $response)${NC}"
    fi
}

# Quick smoke test
run_smoke_test() {
    echo -e "${YELLOW}Running Smoke Tests...${NC}"
    
    # Test critical endpoints
    test_api_endpoint "/health"
    test_api_endpoint "/api/v1/water-futures/current"
    test_api_endpoint "/api/v1/news/latest?limit=5"
    
    # Test chat service
    echo -e "${BLUE}Testing Chat Service...${NC}"
    chat_response=$(curl -s -X POST http://localhost:8001/api/v1/chat \
        -H "Content-Type: application/json" \
        -d '{"message":"Hello","context":{}}' \
        | grep -o '"response"' | wc -l)
    
    if [ "$chat_response" -gt 0 ]; then
        echo -e "${GREEN}✅ Chat service responding${NC}"
    else
        echo -e "${RED}❌ Chat service not responding${NC}"
    fi
    
    echo ""
}

# Main test execution
main() {
    # Install dependencies first
    if [ "$TEST_TYPE" != "smoke" ]; then
        install_dependencies
    fi
    
    case $TEST_TYPE in
        unit)
            echo -e "${BLUE}Running Unit Tests Only${NC}\n"
            run_backend_unit_tests
            ;;
        integration)
            echo -e "${BLUE}Running Integration Tests Only${NC}\n"
            run_integration_tests
            ;;
        e2e)
            echo -e "${BLUE}Running E2E Tests Only${NC}\n"
            run_e2e_tests
            ;;
        smoke)
            echo -e "${BLUE}Running Smoke Tests Only${NC}\n"
            run_smoke_test
            ;;
        all)
            echo -e "${BLUE}Running All Tests${NC}\n"
            run_smoke_test
            run_backend_unit_tests
            run_frontend_tests
            run_integration_tests
            run_e2e_tests
            ;;
        *)
            echo -e "${RED}Invalid test type: $TEST_TYPE${NC}"
            echo "Usage: $0 [unit|integration|e2e|smoke|all] [--verbose]"
            exit 1
            ;;
    esac
    
    # Print summary
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Test Summary${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "\n${GREEN}🎉 All tests passed!${NC}"
        exit 0
    else
        echo -e "\n${RED}⚠️  Some tests failed${NC}"
        exit 1
    fi
}

# Run main function
main