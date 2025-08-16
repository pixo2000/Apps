#!/usr/bin/env python3
"""
Example script showing how to use the Lanis Stundenplan Rechner programmatically
"""

import os
import sys
from main import LanisPortalScraper, ScheduleCalculator

def example_usage():
    """Example of how to use the application programmatically"""
    
    print("Lanis Stundenplan Rechner - Programmatic Usage Example")
    print("=" * 60)
    
    # Create scraper and calculator instances
    scraper = LanisPortalScraper()
    calculator = ScheduleCalculator()
    
    # Example 1: Login (you would use real credentials)
    print("\n1. Login Process:")
    print("   scraper.login('username', 'password', 'school_id')")
    print("   Note: For actual usage, put credentials in .env file")
    
    # Example 2: Data fetching
    print("\n2. Data Fetching:")
    print("   vertretungsplan = scraper.get_vertretungsplan()")
    print("   regular_schedule = scraper.get_regular_schedule()")
    
    # Example 3: Calculation with sample data
    print("\n3. Schedule Calculation with Sample Data:")
    
    # Sample data structure
    sample_schedule = {
        "9A": [
            {"Zeit": "1", "Fach": "Deutsch", "Lehrer": "Fr. Müller", "Raum": "A101"},
            {"Zeit": "2", "Fach": "Mathematik", "Lehrer": "Hr. Schmidt", "Raum": "A102"},
            {"Zeit": "3", "Fach": "Englisch", "Lehrer": "Ms. Johnson", "Raum": "B201"},
            {"Zeit": "4", "Fach": "Geschichte", "Lehrer": "Hr. Weber", "Raum": "C301"}
        ],
        "9B": [
            {"Zeit": "1", "Fach": "Biologie", "Lehrer": "Dr. Fischer", "Raum": "NW1"},
            {"Zeit": "2", "Fach": "Physik", "Lehrer": "Hr. Klein", "Raum": "NW2"},
            {"Zeit": "3", "Fach": "Chemie", "Lehrer": "Fr. Groß", "Raum": "NW3"},
            {"Zeit": "4", "Fach": "Sport", "Lehrer": "Hr. Stark", "Raum": "TH1"}
        ],
        "10A": [
            {"Zeit": "1", "Fach": "Französisch", "Lehrer": "Mme. Dubois", "Raum": "B101"},
            {"Zeit": "2", "Fach": "Latein", "Lehrer": "Hr. Römisch", "Raum": "B102"},
            {"Zeit": "3", "Fach": "Kunst", "Lehrer": "Fr. Kreativ", "Raum": "K1"},
            {"Zeit": "4", "Fach": "Musik", "Lehrer": "Hr. Melodie", "Raum": "MU1"}
        ]
    }
    
    sample_vertretungsplan = [
        {
            "date": "16.08.2025",
            "Stunde": "1",
            "Klasse": "9A",
            "Fach": "Deutsch",
            "Lehrer": "Hr. Vertretung",
            "Raum": "A103",
            "Bemerkung": "Fr. Müller erkrankt"
        },
        {
            "date": "16.08.2025",
            "Stunde": "2",
            "Klasse": "9B",
            "Fach": "Physik",
            "Lehrer": "Hr. Klein",
            "Raum": "A201",
            "Bemerkung": "Raumwechsel wegen Renovierung"
        },
        {
            "date": "16.08.2025",
            "Stunde": "5",
            "Klasse": "10A",
            "Fach": "Informatik",
            "Lehrer": "Hr. Digital",
            "Raum": "IT1",
            "Bemerkung": "Zusatzstunde"
        }
    ]
    
    # Load and calculate
    calculator.load_data(sample_schedule, sample_vertretungsplan)
    calculated_schedules = calculator.calculate_daily_schedules()
    
    print(f"   ✓ Calculated schedules for {len(calculated_schedules)} classes")
    
    # Display results
    print("\n4. Results Overview:")
    for class_name, dates in calculated_schedules.items():
        print(f"\n   Klasse {class_name}:")
        for date, lessons in dates.items():
            print(f"     {date}:")
            for lesson in lessons:
                status = f" ({lesson.get('substitution_info', 'Normal')})" if lesson.get('substitution_info') else ""
                print(f"       {lesson.get('Zeit', 'N/A')}. Stunde: {lesson.get('Fach', 'N/A')} - {lesson.get('Lehrer', 'N/A')} - {lesson.get('Raum', 'N/A')}{status}")
    
    # Example 4: Export
    print("\n5. Export to CSV:")
    output_file = "example_schedule.csv"
    calculator.export_to_csv(output_file)
    
    if os.path.exists(output_file):
        print(f"   ✓ Schedule exported to {output_file}")
        
        # Show first few lines of CSV
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:6]  # First 6 lines
            print("   Preview:")
            for line in lines:
                print(f"     {line.strip()}")
        
        # Clean up
        os.remove(output_file)
        print(f"   (Example file {output_file} removed)")
    
    # Cleanup
    scraper.close()
    
    print("\n6. Integration with GUI:")
    print("   To use the GUI version, simply run:")
    print("   python main.py")
    print("\n   The GUI provides:")
    print("   - Easy credential management")
    print("   - Visual data display")
    print("   - Interactive schedule viewing")
    print("   - Export functionality")
    
    print("\n✅ Example completed successfully!")

if __name__ == "__main__":
    example_usage()
