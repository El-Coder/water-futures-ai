"""
End-to-End Tests for Water Futures AI Platform
Tests complete user flows across the entire application
"""

import pytest
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import subprocess
import os


class TestE2EUserFlows:
    """End-to-end tests for complete user workflows"""
    
    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        # Start services if not running
        cls.ensure_services_running()
        
        # Setup Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode for CI
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
        except:
            # Fallback to Firefox if Chrome not available
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            firefox_options = FirefoxOptions()
            firefox_options.add_argument("--headless")
            cls.driver = webdriver.Firefox(options=firefox_options)
        
        cls.wait = WebDriverWait(cls.driver, 10)
        cls.base_url = "http://localhost:5173"
    
    @classmethod
    def teardown_class(cls):
        """Cleanup after tests"""
        if hasattr(cls, 'driver'):
            cls.driver.quit()
    
    @classmethod
    def ensure_services_running(cls):
        """Ensure all required services are running"""
        services = [
            ("http://localhost:8000/health", "Backend"),
            ("http://localhost:8001/health", "Chat Service"),
            ("http://localhost:8080/health", "MCP Wrapper"),
            ("http://localhost:5173", "Frontend")
        ]
        
        for url, name in services:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    print(f"✅ {name} is running")
                else:
                    print(f"⚠️ {name} returned status {response.status_code}")
            except:
                print(f"❌ {name} is not running at {url}")
                print(f"Please run ./start-local.sh to start all services")
    
    # ==================== Dashboard Tests ====================
    
    def test_user_views_dashboard(self):
        """Test user can view dashboard with portfolio information"""
        self.driver.get(self.base_url)
        
        # Wait for dashboard to load
        dashboard_element = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Portfolio')]"))
        )
        
        assert dashboard_element is not None
        
        # Check for key metrics
        assert self.driver.find_element(By.XPATH, "//*[contains(text(), 'Portfolio Value')]")
        assert self.driver.find_element(By.XPATH, "//*[contains(text(), 'Cash Balance')]")
        
        # Verify water futures prices are displayed
        price_elements = self.driver.find_elements(By.CLASS_NAME, "price-display")
        assert len(price_elements) > 0
    
    # ==================== Trading Flow Tests ====================
    
    def test_user_places_trade_order(self):
        """Test complete trading workflow"""
        # Navigate to trading page
        self.driver.get(f"{self.base_url}/trading")
        
        # Wait for trading form
        self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Trading')]"))
        )
        
        # Select contract
        contract_select = self.driver.find_element(By.NAME, "contract")
        contract_select.send_keys("NQH25")
        
        # Enter quantity
        quantity_input = self.driver.find_element(By.NAME, "quantity")
        quantity_input.clear()
        quantity_input.send_keys("5")
        
        # Select BUY
        buy_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Buy')]")
        buy_button.click()
        
        # Wait for cost calculation
        time.sleep(1)
        cost_element = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Estimated Cost')]"))
        )
        
        assert cost_element is not None
        
        # Submit order
        submit_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Place Order')]")
        submit_button.click()
        
        # Wait for confirmation
        confirmation = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Order') and contains(text(), 'Success')]"))
        )
        
        assert confirmation is not None
    
    # ==================== Chat Interaction Tests ====================
    
    def test_user_interacts_with_chatbot(self):
        """Test chatbot interaction flow"""
        self.driver.get(self.base_url)
        
        # Open chatbot
        chat_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='chat']"))
        )
        chat_button.click()
        
        # Wait for chat window
        chat_window = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Water Futures')]"))
        )
        
        # Send message
        chat_input = self.driver.find_element(By.XPATH, "//input[@placeholder[contains(., 'Ask about water futures')]]")
        chat_input.send_keys("What are current water prices?")
        chat_input.send_keys(Keys.RETURN)
        
        # Wait for response
        time.sleep(2)
        response_elements = self.driver.find_elements(By.CLASS_NAME, "message-bubble")
        assert len(response_elements) >= 2  # User message and bot response
    
    def test_user_enables_agent_mode(self):
        """Test enabling agent mode with warning"""
        self.driver.get(self.base_url)
        
        # Open chatbot
        chat_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='chat']"))
        )
        chat_button.click()
        
        # Find agent mode toggle
        agent_toggle = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='checkbox']"))
        )
        agent_toggle.click()
        
        # Verify warning dialog appears
        warning_dialog = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'REAL MONEY')]"))
        )
        
        assert warning_dialog is not None
        
        # Cancel for safety
        cancel_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Cancel')]")
        cancel_button.click()
    
    # ==================== News & Analysis Tests ====================
    
    def test_user_views_news_and_sentiment(self):
        """Test news viewing and sentiment analysis"""
        self.driver.get(f"{self.base_url}/news")
        
        # Wait for news to load
        news_container = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'news-container')]"))
        )
        
        # Check for articles
        articles = self.driver.find_elements(By.CLASS_NAME, "news-article")
        assert len(articles) > 0
        
        # Verify sentiment indicators
        sentiment_badges = self.driver.find_elements(By.CLASS_NAME, "sentiment-badge")
        assert len(sentiment_badges) > 0
        
        # Check for drought-related news
        drought_news = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'drought') or contains(text(), 'Drought')]")
        assert len(drought_news) > 0
    
    # ==================== Forecast Tests ====================
    
    def test_user_generates_price_forecast(self):
        """Test price forecast generation"""
        self.driver.get(f"{self.base_url}/forecast")
        
        # Wait for forecast page
        self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Forecast')]"))
        )
        
        # Select contract
        contract_select = self.driver.find_element(By.NAME, "forecast_contract")
        contract_select.send_keys("NQH25")
        
        # Select forecast period
        period_select = self.driver.find_element(By.NAME, "forecast_period")
        period_select.send_keys("7")
        
        # Generate forecast
        generate_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Generate Forecast')]")
        generate_button.click()
        
        # Wait for results
        forecast_results = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'forecast-results')]"))
        )
        
        # Verify prediction data
        assert self.driver.find_element(By.XPATH, "//*[contains(text(), 'Current Price')]")
        assert self.driver.find_element(By.XPATH, "//*[contains(text(), 'Predicted')]")
        assert self.driver.find_element(By.XPATH, "//*[contains(text(), 'Confidence')]")
    
    # ==================== Complete User Journey ====================
    
    def test_complete_user_journey(self):
        """Test complete user journey from login to trade execution"""
        # 1. Visit homepage
        self.driver.get(self.base_url)
        time.sleep(2)
        
        # 2. Check dashboard metrics
        portfolio_value = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Portfolio Value')]"))
        )
        assert portfolio_value is not None
        
        # 3. Open chat for market info
        chat_button = self.driver.find_element(By.XPATH, "//button[@aria-label='chat']")
        chat_button.click()
        
        chat_input = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Ask about')]"))
        )
        chat_input.send_keys("Should I buy water futures today?")
        chat_input.send_keys(Keys.RETURN)
        
        time.sleep(2)
        
        # 4. Close chat and navigate to news
        close_chat = self.driver.find_element(By.XPATH, "//button[@aria-label='close']")
        close_chat.click()
        
        self.driver.get(f"{self.base_url}/news")
        
        # 5. Check news sentiment
        self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "news-article"))
        )
        
        # 6. Navigate to forecast
        self.driver.get(f"{self.base_url}/forecast")
        
        # 7. Generate forecast
        generate_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Generate')]"))
        )
        generate_button.click()
        
        time.sleep(2)
        
        # 8. Make trading decision
        self.driver.get(f"{self.base_url}/trading")
        
        # 9. Place order
        quantity_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, "quantity"))
        )
        quantity_input.clear()
        quantity_input.send_keys("3")
        
        # 10. Verify complete flow
        assert self.driver.current_url.startswith(self.base_url)


class TestAPIEndToEnd:
    """End-to-end API tests"""
    
    def test_complete_api_flow(self):
        """Test complete API flow from data to trade"""
        base_url = "http://localhost:8000"
        
        # 1. Check system health
        health = requests.get(f"{base_url}/health")
        assert health.status_code == 200
        
        # 2. Get current prices
        prices = requests.get(f"{base_url}/api/v1/water-futures/current")
        assert prices.status_code == 200
        price_data = prices.json()
        current_price = price_data[0]["price"]
        
        # 3. Get news sentiment
        news = requests.get(f"{base_url}/api/v1/news/latest?limit=5")
        assert news.status_code == 200
        news_data = news.json()
        
        # 4. Generate forecast
        forecast = requests.post(
            f"{base_url}/api/v1/forecasts/predict",
            json={"contract_code": "NQH25", "horizon_days": 7}
        )
        assert forecast.status_code == 200
        forecast_data = forecast.json()
        
        # 5. Make trading decision based on data
        predicted_price = forecast_data["predicted_prices"][0]["price"]
        should_buy = predicted_price > current_price
        
        # 6. Validate order
        validation = requests.post(
            f"{base_url}/api/v1/trading/validate",
            json={
                "contract_code": "NQH25",
                "side": "BUY" if should_buy else "SELL",
                "quantity": 5
            }
        )
        assert validation.status_code == 200
        
        # 7. Place order
        order = requests.post(
            f"{base_url}/api/v1/trading/order",
            json={
                "contract_code": "NQH25",
                "side": "BUY" if should_buy else "SELL",
                "quantity": 5
            }
        )
        assert order.status_code == 200
        order_data = order.json()
        assert "order_id" in order_data
        
        # 8. Check portfolio
        portfolio = requests.get(f"{base_url}/api/v1/trading/portfolio")
        assert portfolio.status_code == 200
        
        print(f"✅ Complete E2E flow successful!")
        print(f"   - Current Price: ${current_price}")
        print(f"   - Predicted Price: ${predicted_price}")
        print(f"   - Decision: {'BUY' if should_buy else 'SELL'}")
        print(f"   - Order ID: {order_data['order_id']}")


def run_e2e_tests():
    """Run all end-to-end tests"""
    # Run API tests first (faster)
    print("Running API E2E Tests...")
    api_test = TestAPIEndToEnd()
    api_test.test_complete_api_flow()
    
    # Run UI tests if Selenium is available
    try:
        print("\nRunning UI E2E Tests...")
        pytest.main([__file__, '-v', '-k', 'TestE2EUserFlows'])
    except Exception as e:
        print(f"UI tests skipped: {e}")
        print("Install Selenium and ChromeDriver to run UI tests")


if __name__ == '__main__':
    run_e2e_tests()