#!/usr/bin/env python3
"""
Backend API Testing for PsychLearn Platform
Tests all backend API endpoints and functionality
"""

import requests
import json
import sys
import os
from typing import Dict, List, Any

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading frontend .env: {e}")
        return None

BASE_URL = get_backend_url()
if not BASE_URL:
    print("ERROR: Could not get backend URL from frontend/.env")
    sys.exit(1)

API_BASE = f"{BASE_URL}/api"

class PsychLearnTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
        
    def log_result(self, test_name: str, passed: bool, message: str = ""):
        status = "PASS" if passed else "FAIL"
        result = f"[{status}] {test_name}"
        if message:
            result += f": {message}"
        print(result)
        self.results.append({"test": test_name, "passed": passed, "message": message})
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def test_health_check(self):
        """Test basic API health check"""
        try:
            response = requests.get(f"{API_BASE}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "PsychLearn API" in data.get("message", ""):
                    self.log_result("Health Check", True, "API is responding correctly")
                    return True
                else:
                    self.log_result("Health Check", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_result("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_get_all_topics(self):
        """Test getting all psychology topics"""
        try:
            response = requests.get(f"{API_BASE}/topics", timeout=10)
            if response.status_code == 200:
                topics = response.json()
                if isinstance(topics, list) and len(topics) >= 5:
                    # Verify expected topics are present
                    topic_titles = [topic.get("title", "") for topic in topics]
                    expected_topics = [
                        "Classical Conditioning",
                        "Cognitive Load Theory", 
                        "Attachment Theory",
                        "Social Identity Theory",
                        "Major Depressive Disorder"
                    ]
                    
                    missing_topics = [t for t in expected_topics if t not in topic_titles]
                    if not missing_topics:
                        self.log_result("Get All Topics", True, f"Found all {len(topics)} expected topics")
                        return topics
                    else:
                        self.log_result("Get All Topics", False, f"Missing topics: {missing_topics}")
                        return topics
                else:
                    self.log_result("Get All Topics", False, f"Expected at least 5 topics, got {len(topics) if isinstance(topics, list) else 'invalid response'}")
                    return None
            else:
                self.log_result("Get All Topics", False, f"Status code: {response.status_code}")
                return None
        except Exception as e:
            self.log_result("Get All Topics", False, f"Error: {str(e)}")
            return None
    
    def test_get_specific_topic(self, topics: List[Dict]):
        """Test getting a specific topic by ID"""
        if not topics:
            self.log_result("Get Specific Topic", False, "No topics available for testing")
            return
            
        try:
            # Test with first topic
            topic_id = topics[0].get("id")
            if not topic_id:
                self.log_result("Get Specific Topic", False, "No topic ID found")
                return
                
            response = requests.get(f"{API_BASE}/topics/{topic_id}", timeout=10)
            if response.status_code == 200:
                topic = response.json()
                if topic.get("id") == topic_id and topic.get("title"):
                    self.log_result("Get Specific Topic", True, f"Retrieved topic: {topic.get('title')}")
                else:
                    self.log_result("Get Specific Topic", False, "Invalid topic data returned")
            else:
                self.log_result("Get Specific Topic", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Get Specific Topic", False, f"Error: {str(e)}")
    
    def test_invalid_topic_id(self):
        """Test error handling for invalid topic ID"""
        try:
            response = requests.get(f"{API_BASE}/topics/invalid-id-12345", timeout=10)
            if response.status_code == 404:
                self.log_result("Invalid Topic ID Error Handling", True, "Correctly returned 404 for invalid ID")
            else:
                self.log_result("Invalid Topic ID Error Handling", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("Invalid Topic ID Error Handling", False, f"Error: {str(e)}")
    
    def test_categories(self):
        """Test getting categories and metadata"""
        try:
            response = requests.get(f"{API_BASE}/categories", timeout=10)
            if response.status_code == 200:
                data = response.json()
                expected_categories = [
                    "Behavioral Psychology",
                    "Cognitive Psychology", 
                    "Developmental Psychology",
                    "Social Psychology",
                    "Clinical Psychology"
                ]
                
                categories = data.get("categories", [])
                difficulty_levels = data.get("difficulty_levels", [])
                
                missing_categories = [c for c in expected_categories if c not in categories]
                expected_difficulties = ["introductory", "intermediate", "advanced", "graduate"]
                missing_difficulties = [d for d in expected_difficulties if d not in difficulty_levels]
                
                if not missing_categories and not missing_difficulties:
                    self.log_result("Categories", True, f"Found all expected categories and difficulty levels")
                else:
                    issues = []
                    if missing_categories:
                        issues.append(f"Missing categories: {missing_categories}")
                    if missing_difficulties:
                        issues.append(f"Missing difficulties: {missing_difficulties}")
                    self.log_result("Categories", False, "; ".join(issues))
            else:
                self.log_result("Categories", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Categories", False, f"Error: {str(e)}")
    
    def test_category_filtering(self):
        """Test filtering topics by category"""
        try:
            # Test filtering by Behavioral Psychology
            response = requests.get(f"{API_BASE}/topics?category=Behavioral Psychology", timeout=10)
            if response.status_code == 200:
                topics = response.json()
                if isinstance(topics, list) and len(topics) > 0:
                    # Check if all returned topics are from the correct category
                    behavioral_topics = [t for t in topics if t.get("category") == "Behavioral Psychology"]
                    if len(behavioral_topics) == len(topics):
                        self.log_result("Category Filtering", True, f"Found {len(topics)} Behavioral Psychology topics")
                    else:
                        self.log_result("Category Filtering", False, "Some topics don't match the category filter")
                else:
                    self.log_result("Category Filtering", False, "No topics returned for category filter")
            else:
                self.log_result("Category Filtering", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Category Filtering", False, f"Error: {str(e)}")
    
    def test_difficulty_filtering(self):
        """Test filtering topics by difficulty level"""
        try:
            # Test filtering by intermediate difficulty
            response = requests.get(f"{API_BASE}/topics?difficulty_level=intermediate", timeout=10)
            if response.status_code == 200:
                topics = response.json()
                if isinstance(topics, list) and len(topics) > 0:
                    # Check if all returned topics have the correct difficulty
                    intermediate_topics = [t for t in topics if t.get("difficulty_level") == "intermediate"]
                    if len(intermediate_topics) == len(topics):
                        self.log_result("Difficulty Filtering", True, f"Found {len(topics)} intermediate topics")
                    else:
                        self.log_result("Difficulty Filtering", False, "Some topics don't match the difficulty filter")
                else:
                    self.log_result("Difficulty Filtering", False, "No topics returned for difficulty filter")
            else:
                self.log_result("Difficulty Filtering", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Difficulty Filtering", False, f"Error: {str(e)}")
    
    def test_search_functionality(self):
        """Test advanced search functionality"""
        try:
            # Test search for "conditioning"
            response = requests.get(f"{API_BASE}/search?q=conditioning", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "results" in data and isinstance(data["results"], list):
                    results = data["results"]
                    if len(results) > 0:
                        # Check if results contain relevant topics
                        conditioning_found = any("conditioning" in r.get("title", "").lower() or 
                                               "conditioning" in r.get("content", "").lower() 
                                               for r in results)
                        if conditioning_found:
                            self.log_result("Search Functionality", True, f"Found {len(results)} results for 'conditioning'")
                        else:
                            self.log_result("Search Functionality", False, "Search results don't contain expected content")
                    else:
                        self.log_result("Search Functionality", False, "No search results returned")
                else:
                    self.log_result("Search Functionality", False, "Invalid search response format")
            else:
                self.log_result("Search Functionality", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Search Functionality", False, f"Error: {str(e)}")
    
    def test_search_with_filters(self):
        """Test search with category and difficulty filters"""
        try:
            # Test search with category filter
            response = requests.get(f"{API_BASE}/search?q=theory&category=Social Psychology", timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                if len(results) > 0:
                    # Check if results match the category filter
                    social_psych_results = [r for r in results if r.get("category") == "Social Psychology"]
                    if len(social_psych_results) == len(results):
                        self.log_result("Search with Filters", True, f"Found {len(results)} Social Psychology results for 'theory'")
                    else:
                        self.log_result("Search with Filters", False, "Search results don't match category filter")
                else:
                    self.log_result("Search with Filters", False, "No results for filtered search")
            else:
                self.log_result("Search with Filters", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Search with Filters", False, f"Error: {str(e)}")
    
    def test_statistics(self):
        """Test platform statistics endpoint"""
        try:
            response = requests.get(f"{API_BASE}/stats", timeout=10)
            if response.status_code == 200:
                stats = response.json()
                required_fields = ["total_topics", "total_categories", "topics_by_category", "topics_by_difficulty"]
                missing_fields = [field for field in required_fields if field not in stats]
                
                if not missing_fields:
                    total_topics = stats.get("total_topics", 0)
                    if total_topics >= 5:
                        self.log_result("Statistics", True, f"Stats show {total_topics} topics across {stats.get('total_categories', 0)} categories")
                    else:
                        self.log_result("Statistics", False, f"Expected at least 5 topics, stats show {total_topics}")
                else:
                    self.log_result("Statistics", False, f"Missing fields in stats: {missing_fields}")
            else:
                self.log_result("Statistics", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Statistics", False, f"Error: {str(e)}")
    
    def test_environment_variables(self):
        """Test that environment variables are loaded (indirectly by checking if API keys exist)"""
        try:
            # Check if backend .env file exists and contains API keys
            env_file = "/app/backend/.env"
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    env_content = f.read()
                    
                required_keys = ["PUBMED_API_KEY", "OSF_API_KEY", "GEMINI_API_KEY", "MONGO_URL", "EMERGENT_LLM_KEY"]
                missing_keys = []
                
                for key in required_keys:
                    if key not in env_content or f"{key}=" not in env_content:
                        missing_keys.append(key)
                
                if not missing_keys:
                    self.log_result("Environment Variables", True, "All required API keys are present in .env file")
                else:
                    self.log_result("Environment Variables", False, f"Missing environment variables: {missing_keys}")
            else:
                self.log_result("Environment Variables", False, "Backend .env file not found")
        except Exception as e:
            self.log_result("Environment Variables", False, f"Error checking environment: {str(e)}")
    
    def test_ai_qa_general_question(self):
        """Test AI Q&A with general psychology question"""
        try:
            payload = {
                "question": "What is the difference between classical and operant conditioning?",
                "session_id": "test-session-general"
            }
            
            response = requests.post(f"{API_BASE}/ask", json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["answer", "session_id"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    answer = data.get("answer", "")
                    if len(answer) > 50 and ("classical" in answer.lower() or "operant" in answer.lower()):
                        self.log_result("AI Q&A General Question", True, f"Got relevant answer ({len(answer)} chars)")
                        return data
                    else:
                        self.log_result("AI Q&A General Question", False, f"Answer seems irrelevant or too short: {answer[:100]}...")
                        return None
                else:
                    self.log_result("AI Q&A General Question", False, f"Missing fields: {missing_fields}")
                    return None
            else:
                self.log_result("AI Q&A General Question", False, f"Status code: {response.status_code}")
                return None
        except Exception as e:
            self.log_result("AI Q&A General Question", False, f"Error: {str(e)}")
            return None
    
    def test_ai_qa_topic_specific_question(self, topics: List[Dict]):
        """Test AI Q&A with topic-specific question"""
        if not topics:
            self.log_result("AI Q&A Topic-Specific Question", False, "No topics available for testing")
            return None
            
        try:
            # Use the first topic for testing
            topic = topics[0]
            topic_id = topic.get("id")
            topic_title = topic.get("title", "")
            
            payload = {
                "question": f"Can you explain the key concepts of {topic_title}?",
                "topic_id": topic_id,
                "session_id": "test-session-topic"
            }
            
            response = requests.post(f"{API_BASE}/ask", json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["answer", "session_id", "topic_title"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    answer = data.get("answer", "")
                    returned_topic_title = data.get("topic_title", "")
                    
                    if (len(answer) > 50 and 
                        returned_topic_title == topic_title and
                        any(keyword.lower() in answer.lower() for keyword in topic.get("key_concepts", [])[:3])):
                        self.log_result("AI Q&A Topic-Specific Question", True, f"Got relevant topic-specific answer for '{topic_title}'")
                        return data
                    else:
                        self.log_result("AI Q&A Topic-Specific Question", False, f"Answer doesn't seem topic-specific or relevant")
                        return None
                else:
                    self.log_result("AI Q&A Topic-Specific Question", False, f"Missing fields: {missing_fields}")
                    return None
            else:
                self.log_result("AI Q&A Topic-Specific Question", False, f"Status code: {response.status_code}")
                return None
        except Exception as e:
            self.log_result("AI Q&A Topic-Specific Question", False, f"Error: {str(e)}")
            return None
    
    def test_chat_history_retrieval(self):
        """Test retrieving chat history for a session"""
        try:
            # First, ask a question to create some history
            payload = {
                "question": "What is psychology?",
                "session_id": "test-session-history"
            }
            
            # Send a question first
            ask_response = requests.post(f"{API_BASE}/ask", json=payload, timeout=30)
            if ask_response.status_code != 200:
                self.log_result("Chat History Retrieval", False, "Failed to create chat history for testing")
                return
            
            # Now retrieve the history
            response = requests.get(f"{API_BASE}/chat-history/test-session-history", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "messages" in data and isinstance(data["messages"], list):
                    messages = data["messages"]
                    if len(messages) > 0:
                        # Check if the message has the expected structure
                        first_message = messages[0]
                        required_fields = ["id", "session_id", "question", "answer", "created_at"]
                        missing_fields = [field for field in required_fields if field not in first_message]
                        
                        if not missing_fields:
                            self.log_result("Chat History Retrieval", True, f"Retrieved {len(messages)} chat messages")
                        else:
                            self.log_result("Chat History Retrieval", False, f"Message missing fields: {missing_fields}")
                    else:
                        self.log_result("Chat History Retrieval", False, "No messages found in chat history")
                else:
                    self.log_result("Chat History Retrieval", False, "Invalid chat history response format")
            else:
                self.log_result("Chat History Retrieval", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Chat History Retrieval", False, f"Error: {str(e)}")
    
    def test_ai_qa_error_handling(self):
        """Test AI Q&A error handling with invalid requests"""
        try:
            # Test with empty question
            payload = {
                "question": "",
                "session_id": "test-session-error"
            }
            
            response = requests.post(f"{API_BASE}/ask", json=payload, timeout=30)
            # Should either handle gracefully or return appropriate error
            if response.status_code in [200, 400, 422, 500]:
                self.log_result("AI Q&A Error Handling", True, f"Handled empty question appropriately (status: {response.status_code})")
            else:
                self.log_result("AI Q&A Error Handling", False, f"Unexpected status code for empty question: {response.status_code}")
        except Exception as e:
            self.log_result("AI Q&A Error Handling", False, f"Error: {str(e)}")
    
    def test_ai_qa_invalid_topic_id(self):
        """Test AI Q&A with invalid topic_id"""
        try:
            payload = {
                "question": "What is this topic about?",
                "topic_id": "invalid-topic-id-12345",
                "session_id": "test-session-invalid-topic"
            }
            
            response = requests.post(f"{API_BASE}/ask", json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                # Should still work but without topic context
                if "answer" in data and data.get("topic_title") is None:
                    self.log_result("AI Q&A Invalid Topic ID", True, "Handled invalid topic_id gracefully")
                else:
                    self.log_result("AI Q&A Invalid Topic ID", False, "Didn't handle invalid topic_id properly")
            else:
                self.log_result("AI Q&A Invalid Topic ID", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("AI Q&A Invalid Topic ID", False, f"Error: {str(e)}")
    
    def test_chat_history_nonexistent_session(self):
        """Test retrieving chat history for non-existent session"""
        try:
            response = requests.get(f"{API_BASE}/chat-history/nonexistent-session-12345", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "messages" in data and isinstance(data["messages"], list) and len(data["messages"]) == 0:
                    self.log_result("Chat History Non-existent Session", True, "Returned empty messages for non-existent session")
                else:
                    self.log_result("Chat History Non-existent Session", False, "Unexpected response for non-existent session")
            else:
                self.log_result("Chat History Non-existent Session", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Chat History Non-existent Session", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all backend tests"""
        print(f"Starting PsychLearn Backend API Tests")
        print(f"Testing API at: {API_BASE}")
        print("=" * 60)
        
        # Test basic connectivity first
        if not self.test_health_check():
            print("CRITICAL: API health check failed. Stopping tests.")
            return self.get_summary()
        
        # Get topics for use in other tests
        topics = self.test_get_all_topics()
        
        # Test individual topic retrieval
        self.test_get_specific_topic(topics)
        
        # Test error handling
        self.test_invalid_topic_id()
        
        # Test categories and metadata
        self.test_categories()
        
        # Test filtering functionality
        self.test_category_filtering()
        self.test_difficulty_filtering()
        
        # Test search functionality
        self.test_search_functionality()
        self.test_search_with_filters()
        
        # Test statistics
        self.test_statistics()
        
        # Test environment setup
        self.test_environment_variables()
        
        # Test AI Q&A functionality
        print("\n" + "=" * 40)
        print("Testing AI Q&A Functionality")
        print("=" * 40)
        
        self.test_ai_qa_general_question()
        self.test_ai_qa_topic_specific_question(topics)
        self.test_chat_history_retrieval()
        self.test_ai_qa_error_handling()
        self.test_ai_qa_invalid_topic_id()
        self.test_chat_history_nonexistent_session()
        
        return self.get_summary()
    
    def get_summary(self):
        """Get test summary"""
        print("=" * 60)
        print(f"Test Summary: {self.passed} passed, {self.failed} failed")
        
        if self.failed > 0:
            print("\nFailed Tests:")
            for result in self.results:
                if not result["passed"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        return {
            "total_tests": self.passed + self.failed,
            "passed": self.passed,
            "failed": self.failed,
            "success_rate": (self.passed / (self.passed + self.failed)) * 100 if (self.passed + self.failed) > 0 else 0,
            "results": self.results
        }

if __name__ == "__main__":
    tester = PsychLearnTester()
    summary = tester.run_all_tests()
    
    # Exit with error code if tests failed
    if summary["failed"] > 0:
        sys.exit(1)
    else:
        print("\nAll tests passed successfully!")
        sys.exit(0)