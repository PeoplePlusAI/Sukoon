import pytest
from fastapi.testclient import TestClient
from sukoon_api import app
import logging
from datetime import datetime
import os
import json

# Set up logging
def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f'logs/test_api_{timestamp}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# Create a test client
client = TestClient(app)

def log_test_result(test_name: str, request_data: dict = None, response_data: dict = None):
    """Helper function to log test results"""
    log_data = {
        "test_name": test_name,
        "timestamp": datetime.now().isoformat(),
    }
    if request_data:
        log_data["request"] = request_data
    if response_data:
        log_data["response"] = response_data
    
    logger.info(json.dumps(log_data, indent=2))

@pytest.mark.api
def test_root_endpoint():
    """Test the root endpoint (/)"""
    response = client.get("/")
    
    log_test_result(
        "test_root_endpoint",
        response_data=response.json()
    )
    
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Welcome to the Sukoon API" in response.json()["message"]

@pytest.mark.api
def test_query_endpoint_success():
    """Test the query endpoint with valid input"""
    test_input = "Hello, how are you?"
    
    response = client.post(
        "/query",
        json={"input": test_input}
    )
    
    log_test_result(
        "test_query_endpoint_success",
        request_data={"input": test_input},
        response_data=response.json()
    )
    
    assert response.status_code == 200
    assert "output" in response.json()
    assert isinstance(response.json()["output"], str)
    assert len(response.json()["output"]) > 0

@pytest.mark.api
def test_query_endpoint_empty_input():
    """Test the query endpoint with empty input"""
    response = client.post(
        "/query",
        json={"input": ""}
    )
    
    log_test_result(
        "test_query_endpoint_empty_input",
        request_data={"input": ""},
        response_data=response.json()
    )
    
    assert response.status_code == 200
    assert "output" in response.json()

@pytest.mark.api
def test_query_endpoint_invalid_request():
    """Test the query endpoint with invalid request format"""
    response = client.post(
        "/query",
        json={"wrong_field": "Hello"}
    )
    
    log_test_result(
        "test_query_endpoint_invalid_request",
        request_data={"wrong_field": "Hello"},
        response_data=response.json()
    )
    
    assert response.status_code == 422  # Unprocessable Entity

@pytest.mark.api
def test_query_endpoint_missing_input():
    """Test the query endpoint with missing input field"""
    response = client.post(
        "/query",
        json={}
    )
    
    log_test_result(
        "test_query_endpoint_missing_input",
        request_data={},
        response_data=response.json()
    )
    
    assert response.status_code == 422  # Unprocessable Entity

if __name__ == "__main__":
    pytest.main(["-v", __file__])