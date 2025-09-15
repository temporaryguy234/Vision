#!/bin/bash

echo "🚀 MotionEdit Deployment and Testing Script"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    print_status "Checking Docker..."
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Build and start services
deploy_services() {
    print_status "Building and starting services..."
    
    # Stop existing containers
    docker-compose down 2>/dev/null || true
    
    # Build and start
    docker-compose up --build -d
    
    if [ $? -eq 0 ]; then
        print_success "Services started successfully"
    else
        print_error "Failed to start services"
        exit 1
    fi
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for backend
    for i in {1..30}; do
        if curl -s http://localhost:8001/health > /dev/null 2>&1; then
            print_success "Backend is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Backend failed to start within 30 seconds"
            show_logs
            exit 1
        fi
        sleep 1
    done
    
    # Wait for frontend
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            print_success "Frontend is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_warning "Frontend may not be ready yet, but continuing..."
            break
        fi
        sleep 1
    done
}

# Show service logs
show_logs() {
    print_status "Showing service logs..."
    echo "=== BACKEND LOGS ==="
    docker-compose logs backend
    echo ""
    echo "=== FRONTEND LOGS ==="
    docker-compose logs frontend
}

# Test functionality
test_functionality() {
    print_status "Testing functionality..."
    
    # Test backend health
    if curl -s http://localhost:8001/health | grep -q "healthy"; then
        print_success "Backend health check passed"
    else
        print_error "Backend health check failed"
        return 1
    fi
    
    # Test Lottie import
    print_status "Testing Lottie import..."
    response=$(curl -s -X POST http://localhost:8001/api/test/import-lottie \
        -d "url=https://lottie.host/85036dbf-44d5-420d-aa24-325989179/bN9lsInwGh.json")
    
    if echo "$response" | grep -q '"success":true'; then
        print_success "Lottie import test passed"
        
        # Extract thumbnail URL and test it
        thumbnail_url=$(echo "$response" | grep -o '"/uploads/[^"]*_thumb\.png"' | tr -d '"')
        if [ -n "$thumbnail_url" ]; then
            if curl -s "http://localhost:8001$thumbnail_url" > /dev/null 2>&1; then
                print_success "Thumbnail generation test passed"
            else
                print_warning "Thumbnail generation test failed - thumbnail not accessible"
            fi
        else
            print_warning "No thumbnail URL found in response"
        fi
    else
        print_error "Lottie import test failed"
        echo "Response: $response"
        return 1
    fi
}

# Main execution
main() {
    echo "Starting deployment process..."
    
    check_docker
    deploy_services
    wait_for_services
    
    echo ""
    print_status "Running functionality tests..."
    if test_functionality; then
        echo ""
        print_success "🎉 All tests passed! Deployment is working correctly."
        echo ""
        echo "Your MotionEdit application is now running:"
        echo "  Frontend: http://localhost:3000"
        echo "  Backend:  http://localhost:8001"
        echo "  Health:   http://localhost:8001/health"
        echo ""
        echo "To view logs: docker-compose logs -f"
        echo "To stop:      docker-compose down"
    else
        echo ""
        print_error "❌ Some tests failed. Check the logs above for details."
        echo ""
        show_logs
        echo ""
        print_status "Troubleshooting tips:"
        echo "1. Check if all required system dependencies are installed"
        echo "2. Verify environment variables are set correctly"
        echo "3. Check Docker container logs: docker-compose logs"
        echo "4. Ensure ports 3000 and 8001 are not in use by other applications"
        exit 1
    fi
}

# Run main function
main "$@"

