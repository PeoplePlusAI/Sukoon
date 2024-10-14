import pytest
from unittest.mock import Mock, patch
from sukoon import route_query, run_conversational_agent, run_suicide_prevention_agent, chat, State
from langchain_core.messages import HumanMessage, AIMessage

@pytest.fixture
def mock_openai():
    with patch('sukoon.ChatOpenAI') as mock:
        yield mock

@pytest.fixture
def mock_state():
    return State(messages=[HumanMessage(content="Test message")])

def test_route_query(mock_openai, mock_state):
    mock_openai.return_value.with_structured_output.return_value.invoke.return_value.route = "conversational"
    result = route_query(mock_state)
    assert result == "conversational"

    mock_openai.return_value.with_structured_output.return_value.invoke.return_value.route = "suicide_prevention"
    result = route_query(mock_state)
    assert result == "suicide_prevention"

def test_run_conversational_agent(mock_openai, mock_state):
    mock_openai.return_value.invoke.return_value = AIMessage(content="Conversational response")
    result = run_conversational_agent(mock_state)
    assert "messages" in result
    assert result["messages"].content == "Conversational response"

def test_run_suicide_prevention_agent(mock_openai, mock_state):
    mock_openai.return_value.invoke.return_value = AIMessage(content="Suicide prevention response")
    result = run_suicide_prevention_agent(mock_state)
    assert "messages" in result
    assert result["messages"].content == "Suicide prevention response"

@pytest.mark.parametrize("input_message,expected_route", [
    ("I'm feeling happy today", "conversational"),
    ("I'm thinking about ending it all", "suicide_prevention"),
])
def test_chat_routing(mock_openai, input_message, expected_route):
    mock_openai.return_value.with_structured_output.return_value.invoke.return_value.route = expected_route
    mock_openai.return_value.invoke.return_value = AIMessage(content=f"Response from {expected_route} agent")
    
    config = {"configurable": {"thread_id": "test"}}
    response = chat(input_message, config)
    
    assert response.content == f"Response from {expected_route} agent"

if __name__ == "__main__":
    pytest.main([__file__])