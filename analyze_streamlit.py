#!/usr/bin/env python3
"""
Streamlit App Analysis Script using Playwright
Analyzes the Telegram Claude Agent Streamlit application for errors and issues
"""

from playwright.sync_api import sync_playwright
import json
import time
import sys

def analyze_streamlit_app():
    """Comprehensive analysis of the Streamlit application"""
    results = {
        'page_load': {},
        'errors_found': [],
        'api_connectivity': {},
        'console_logs': [],
        'network_errors': [],
        'section_navigation': {},
        'screenshots': []
    }
    
    with sync_playwright() as p:
        # Launch browser with error handling
        try:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            # Collect console logs and network errors
            console_logs = []
            network_errors = []
            
            def handle_console(msg):
                console_logs.append({
                    'type': msg.type,
                    'text': msg.text,
                    'location': str(msg.location) if msg.location else None
                })
            
            def handle_response(response):
                if response.status >= 400:
                    network_errors.append({
                        'url': response.url,
                        'status': response.status,
                        'status_text': response.status_text,
                        'method': response.request.method
                    })
            
            def handle_request_failed(request):
                network_errors.append({
                    'url': request.url,
                    'status': 'FAILED',
                    'status_text': 'Request Failed',
                    'method': request.method,
                    'failure': request.failure
                })
            
            page.on('console', handle_console)
            page.on('response', handle_response)
            page.on('requestfailed', handle_request_failed)
            
            print("🔍 Starting Streamlit app analysis...")
            
            # Navigate to Streamlit app
            try:
                print("📂 Navigating to http://localhost:8501...")
                response = page.goto('http://localhost:8501', wait_until='networkidle', timeout=30000)
                
                results['page_load'] = {
                    'status': response.status,
                    'status_text': response.status_text,
                    'url': response.url,
                    'loaded_successfully': response.status == 200
                }
                
                print(f"✅ Page loaded with status: {response.status}")
                
                # Wait for Streamlit to fully initialize
                print("⏳ Waiting for Streamlit to initialize...")
                time.sleep(8)
                
                # Take initial screenshot
                screenshot_path = '/home/coder/1claude_ANSWER/telegram_claude_agent/streamlit_initial.png'
                page.screenshot(path=screenshot_path, full_page=True)
                results['screenshots'].append(screenshot_path)
                print(f"📷 Initial screenshot saved: {screenshot_path}")
                
                # Get page title
                title = page.title()
                results['page_load']['title'] = title
                print(f"📄 Page title: {title}")
                
                # Check for error messages and alerts
                print("🔍 Scanning for error messages...")
                
                # Check for Streamlit error elements
                error_selectors = [
                    '.stAlert[data-baseweb="notification"]',
                    '.stException',
                    '.element-container .stAlert',
                    '[data-testid="stAlert"]',
                    'div[role="alert"]'
                ]
                
                for selector in error_selectors:
                    elements = page.query_selector_all(selector)
                    for element in elements:
                        try:
                            text = element.inner_text()
                            if text and text.strip():
                                results['errors_found'].append({
                                    'type': 'ui_error',
                                    'selector': selector,
                                    'text': text.strip()
                                })
                        except Exception as e:
                            print(f"Warning: Could not read element text: {e}")
                
                # Check for specific error indicators
                specific_errors = [
                    'Backend недоступен',
                    'API Error',
                    'Connection Error',
                    'Не удается подключиться',
                    'Ошибка подключения',
                    'Failed to load',
                    '404',
                    '500',
                    'Network Error'
                ]
                
                for error_text in specific_errors:
                    elements = page.get_by_text(error_text, exact=False)
                    count = elements.count()
                    if count > 0:
                        results['errors_found'].append({
                            'type': 'specific_error',
                            'text': error_text,
                            'count': count
                        })
                
                # Test API connectivity status display
                print("🔗 Checking API connectivity status...")
                try:
                    # Look for status indicators
                    status_elements = page.query_selector_all('.metric-value, [data-testid="metric-value"]')
                    for element in status_elements:
                        text = element.inner_text()
                        if any(keyword in text.lower() for keyword in ['сервер', 'telegram', 'база данных', 'server', 'database']):
                            results['api_connectivity'][text] = 'displayed'
                except Exception as e:
                    print(f"Warning: Could not check status indicators: {e}")
                
                # Test navigation through different sections
                print("🧭 Testing section navigation...")
                sections_to_test = [
                    ('🏢 Компания', 'company'),
                    ('📋 Кампании', 'campaigns'),
                    ('💬 Чаты', 'chats'),
                    ('📊 Статистика', 'statistics'),
                    ('📈 Аналитика чатов', 'analytics'),
                    ('📝 Логи активности', 'logs'),
                    ('⚙️ Настройки', 'settings')
                ]
                
                for section_name, section_key in sections_to_test:
                    try:
                        print(f"  📂 Testing {section_name}...")
                        
                        # Try to click on the section
                        section_element = page.get_by_text(section_name, exact=False).first
                        if section_element.is_visible():
                            section_element.click()
                            time.sleep(3)  # Wait for content to load
                            
                            # Take screenshot of the section
                            section_screenshot = f'/home/coder/1claude_ANSWER/telegram_claude_agent/streamlit_{section_key}.png'
                            page.screenshot(path=section_screenshot, full_page=True)
                            results['screenshots'].append(section_screenshot)
                            
                            # Check for errors in this section
                            section_errors = []
                            for selector in error_selectors:
                                elements = page.query_selector_all(selector)
                                for element in elements:
                                    try:
                                        text = element.inner_text()
                                        if text and text.strip():
                                            section_errors.append(text.strip())
                                    except:
                                        pass
                            
                            results['section_navigation'][section_key] = {
                                'accessible': True,
                                'errors': section_errors,
                                'screenshot': section_screenshot
                            }
                            
                            print(f"    ✅ {section_name} accessible, {len(section_errors)} errors found")
                        else:
                            results['section_navigation'][section_key] = {
                                'accessible': False,
                                'error': 'Element not visible'
                            }
                            print(f"    ❌ {section_name} not accessible (not visible)")
                            
                    except Exception as e:
                        results['section_navigation'][section_key] = {
                            'accessible': False,
                            'error': str(e)
                        }
                        print(f"    ❌ {section_name} error: {e}")
                
                # Final screenshot
                final_screenshot = '/home/coder/1claude_ANSWER/telegram_claude_agent/streamlit_final.png'
                page.screenshot(path=final_screenshot, full_page=True)
                results['screenshots'].append(final_screenshot)
                
                # Collect final logs and network errors
                results['console_logs'] = console_logs
                results['network_errors'] = network_errors
                
                print("✅ Analysis completed successfully!")
                
            except Exception as e:
                print(f"❌ Error during page navigation: {e}")
                results['page_load']['error'] = str(e)
                return results
            
        except Exception as e:
            print(f"❌ Error launching browser: {e}")
            results['browser_error'] = str(e)
            return results
        
        finally:
            try:
                browser.close()
            except:
                pass
    
    return results

def print_analysis_report(results):
    """Print a detailed analysis report"""
    print("\n" + "="*60)
    print("🤖 TELEGRAM CLAUDE AGENT - STREAMLIT ANALYSIS REPORT")
    print("="*60)
    
    # Page Load Status
    print("\n📄 PAGE LOAD STATUS:")
    page_load = results.get('page_load', {})
    if page_load.get('loaded_successfully'):
        print(f"✅ Status: {page_load.get('status')} - {page_load.get('status_text')}")
        print(f"🌐 URL: {page_load.get('url')}")
        print(f"📋 Title: {page_load.get('title')}")
    else:
        print(f"❌ Failed to load: {page_load.get('error', 'Unknown error')}")
    
    # Errors Found
    print(f"\n❌ ERRORS FOUND: {len(results.get('errors_found', []))}")
    for i, error in enumerate(results.get('errors_found', []), 1):
        print(f"  {i}. [{error.get('type', 'unknown')}] {error.get('text', 'No details')}")
        if error.get('count', 0) > 1:
            print(f"     (Found {error['count']} times)")
    
    # Network Errors
    network_errors = results.get('network_errors', [])
    print(f"\n🌐 NETWORK ERRORS: {len(network_errors)}")
    for error in network_errors:
        print(f"  • {error.get('method', 'GET')} {error.get('url', 'Unknown URL')}")
        print(f"    Status: {error.get('status', 'Unknown')} - {error.get('status_text', 'No details')}")
    
    # API Connectivity
    api_status = results.get('api_connectivity', {})
    print(f"\n🔗 API CONNECTIVITY: {len(api_status)} status indicators found")
    for status, value in api_status.items():
        print(f"  • {status}: {value}")
    
    # Section Navigation
    print(f"\n🧭 SECTION NAVIGATION:")
    sections = results.get('section_navigation', {})
    for section, data in sections.items():
        if data.get('accessible'):
            error_count = len(data.get('errors', []))
            status = "✅" if error_count == 0 else f"⚠️ ({error_count} errors)"
            print(f"  {status} {section.title()}")
            for error in data.get('errors', []):
                print(f"      - {error}")
        else:
            print(f"  ❌ {section.title()}: {data.get('error', 'Not accessible')}")
    
    # Console Logs Summary
    console_logs = results.get('console_logs', [])
    print(f"\n📝 CONSOLE LOGS: {len(console_logs)} messages")
    error_logs = [log for log in console_logs if log.get('type') == 'error']
    warning_logs = [log for log in console_logs if log.get('type') == 'warning']
    
    if error_logs:
        print(f"  🔴 Errors: {len(error_logs)}")
        for log in error_logs[-5:]:  # Show last 5 errors
            print(f"    - {log.get('text', 'No message')}")
    
    if warning_logs:
        print(f"  🟡 Warnings: {len(warning_logs)}")
        for log in warning_logs[-3:]:  # Show last 3 warnings
            print(f"    - {log.get('text', 'No message')}")
    
    # Screenshots
    screenshots = results.get('screenshots', [])
    print(f"\n📷 SCREENSHOTS CAPTURED: {len(screenshots)}")
    for screenshot in screenshots:
        print(f"  • {screenshot}")
    
    # Overall Assessment
    print(f"\n🎯 OVERALL ASSESSMENT:")
    total_errors = len(results.get('errors_found', [])) + len(results.get('network_errors', []))
    accessible_sections = sum(1 for s in sections.values() if s.get('accessible'))
    total_sections = len(sections)
    
    if total_errors == 0 and page_load.get('loaded_successfully'):
        print("✅ Application appears to be functioning normally")
    elif total_errors <= 2:
        print("⚠️ Minor issues detected, but generally functional")
    else:
        print("❌ Significant issues detected, requires attention")
    
    print(f"📊 Section Accessibility: {accessible_sections}/{total_sections}")
    print(f"🐛 Total Issues: {total_errors}")


if __name__ == "__main__":
    try:
        results = analyze_streamlit_app()
        print_analysis_report(results)
        
        # Save detailed results to JSON file
        output_file = '/home/coder/1claude_ANSWER/telegram_claude_agent/streamlit_analysis_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Detailed results saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Analysis failed with error: {e}")
        sys.exit(1)