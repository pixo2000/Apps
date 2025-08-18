#!/usr/bin/env python3
"""
Test script for Lanis Stundenplan Rechner
Tests basic functionality without actual login
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import LanisPortalScraper, ScheduleCalculator

def test_scraper_initialization():
    """Test if scraper initializes correctly"""
    try:
        scraper = LanisPortalScraper()
        print("✓ LanisPortalScraper initialized successfully")
        return True
    except Exception as e:
        print(f"✗ LanisPortalScraper initialization failed: {e}")
        return False

def test_calculator_initialization():
    """Test if calculator initializes correctly"""
    try:
        calculator = ScheduleCalculator()
        print("✓ ScheduleCalculator initialized successfully")
        return True
    except Exception as e:
        print(f"✗ ScheduleCalculator initialization failed: {e}")
        return False

def test_calculator_with_sample_data():
    """Test calculator with sample data"""
    try:
        calculator = ScheduleCalculator()
        
        # Sample regular schedule
        sample_schedule = {
            "5A": [
                {"Zeit": "1", "Fach": "Deutsch", "Lehrer": "Müller", "Raum": "101"},
                {"Zeit": "2", "Fach": "Mathe", "Lehrer": "Schmidt", "Raum": "102"}
            ],
            "5B": [
                {"Zeit": "1", "Fach": "Englisch", "Lehrer": "Johnson", "Raum": "103"},
                {"Zeit": "2", "Fach": "Geschichte", "Lehrer": "Weber", "Raum": "104"}
            ]
        }
        
        # Sample vertretungsplan
        sample_vertretungsplan = [
            {
                "date": "16.08.2025",
                "Stunde": "1",
                "Klasse": "5A",
                "Fach": "Deutsch",
                "Lehrer": "Vertretung_Müller",
                "Raum": "201",
                "Bemerkung": "Vertretung"
            }
        ]
        
        calculator.load_data(sample_schedule, sample_vertretungsplan)
        result = calculator.calculate_daily_schedules()
        
        if result and "5A" in result:
            print("✓ ScheduleCalculator processes sample data correctly")
            print(f"  - Calculated schedules for {len(result)} classes")
            return True
        else:
            print("✗ ScheduleCalculator failed to process sample data")
            return False
            
    except Exception as e:
        print(f"✗ ScheduleCalculator test failed: {e}")
        return False

def test_gui_import():
    """Test if GUI components can be imported"""
    try:
        from main import StundenplanGUI
        print("✓ GUI components import successfully")
        return True
    except Exception as e:
        print(f"✗ GUI import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Lanis Stundenplan Rechner - Test Suite")
    print("=" * 50)
    
    tests = [
        test_scraper_initialization,
        test_calculator_initialization,
        test_calculator_with_sample_data,
        test_gui_import
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application should work correctly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
