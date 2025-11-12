from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import csv
from main import Student, Course, assign_students_to_courses, export_results, export_summary_txt
import io
from collections import Counter

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Globale Variable für aktuelle Daten (nur im RAM)
current_data = {
    'students': None,
    'courses': None,
    'filename': None
}

def load_data_from_csv_content(file_content):
    """Lädt CSV-Daten direkt aus dem Speicher (ohne Disk I/O)"""
    students = []
    all_courses = set()
    
    # Dekodiere Bytes zu String falls nötig
    if isinstance(file_content, bytes):
        file_content = file_content.decode('utf-8')
    
    # Verwende StringIO für In-Memory CSV-Parsing
    csv_file = io.StringIO(file_content)
    reader = csv.DictReader(csv_file)
    
    for row in reader:
        wishes = []
        for i in range(1, 5):
            wish_col = f'Wahlangebote Methodentag E-Phase - {i}. Wunsch'
            if wish_col in row and row[wish_col]:
                wishes.append(row[wish_col])
                all_courses.add(row[wish_col])
        
        student = Student(
            row['Nachname'],
            row['Vorname'],
            row['Klasse'],
            wishes
        )
        students.append(student)
    
    # Erstelle Course-Objekte
    courses = {name: Course(name) for name in all_courses}
    
    return students, courses

def load_data_from_file(filepath):
    """Lädt die CSV-Datei von Disk (Fallback für daten.csv)"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return load_data_from_csv_content(content)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Lädt eine CSV-Datei hoch und speichert sie temporär im RAM"""
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'Keine Datei ausgewählt'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'Keine Datei ausgewählt'
        }), 400
    
    # Prüfe Dateiendung
    if not file.filename.lower().endswith('.csv'):
        return jsonify({
            'success': False,
            'error': 'Ungültiger Dateityp. Nur CSV-Dateien sind erlaubt.'
        }), 400
    
    try:
        # Lese Datei direkt in den Speicher (keine Disk I/O)
        file_content = file.read()
        
        # Versuche die Daten zu laden und zu validieren
        students, courses = load_data_from_csv_content(file_content)
        
        # Speichere in globaler Variable (nur RAM, nicht auf Disk!)
        current_data['students'] = students
        current_data['courses'] = courses
        current_data['filename'] = file.filename
        
        return jsonify({
            'success': True,
            'filename': file.filename,
            'studentCount': len(students),
            'courseCount': len(courses)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Fehler beim Laden der Datei: {str(e)}'
        }), 400

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analysiert die Daten ohne Zuteilung durchzuführen"""
    try:
        # Nutze hochgeladene Daten oder fallback auf daten.csv
        if current_data['students'] is None or current_data['courses'] is None:
            # Fallback: Versuche daten.csv zu laden
            default_file = os.path.join(SCRIPT_DIR, 'daten.csv')
            if os.path.exists(default_file):
                students, courses = load_data_from_file(default_file)
                current_data['students'] = students
                current_data['courses'] = courses
                current_data['filename'] = 'daten.csv'
            else:
                return jsonify({
                    'success': False,
                    'error': 'Bitte laden Sie zuerst eine CSV-Datei hoch.'
                }), 400
        
        students = current_data['students']
        courses = current_data['courses']
        
        # Sammle Kursstatistiken
        course_list = []
        for name in sorted(courses.keys()):
            # Zähle wie oft dieser Kurs gewünscht wurde
            wish_count = 0
            wish_priorities = {1: 0, 2: 0, 3: 0, 4: 0}
            for student in students:
                for i, wish in enumerate(student.wishes, 1):
                    if wish == name:
                        wish_count += 1
                        wish_priorities[i] += 1
            
            course_list.append({
                'name': name,
                'wishCount': wish_count,
                'priorities': wish_priorities
            })
        
        return jsonify({
            'success': True,
            'studentCount': len(students),
            'courseCount': len(courses),
            'courses': course_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/assign', methods=['POST'])
def assign():
    """Führt die Zuteilung durch"""
    try:
        data = request.get_json()
        max_students = data.get('maxStudents')
        equal_distribution = data.get('equalDistribution', False)
        course_limits = data.get('courseLimits', {})  # Individuelle Limits pro Kurs
        
        # Konvertiere max_students (globales Limit)
        if max_students is not None and max_students != '':
            max_students = int(max_students)
        else:
            max_students = None
        
        # Nutze hochgeladene Daten oder fallback auf daten.csv
        if current_data['students'] is None or current_data['courses'] is None:
            # Fallback: Versuche daten.csv zu laden
            default_file = os.path.join(SCRIPT_DIR, 'daten.csv')
            if os.path.exists(default_file):
                students, courses = load_data_from_file(default_file)
                current_data['students'] = students
                current_data['courses'] = courses
                current_data['filename'] = 'daten.csv'
            else:
                return jsonify({
                    'success': False,
                    'error': 'Bitte laden Sie zuerst eine CSV-Datei hoch.'
                }), 400
        
        # Erstelle neue Course-Objekte für die Zuteilung (Deep Copy)
        students = current_data['students']
        courses = {name: Course(name) for name in current_data['courses'].keys()}
        
        # Setze alle Zuweisungen zurück
        for student in students:
            student.assigned_courses = []
            student.fulfilled_wish_numbers = []
        
        fulfilled_wishes, unfulfilled_students, total_wishes = assign_students_to_courses(
            students, courses, max_students, equal_distribution, course_limits
        )
        
        # Exportiere Ergebnisse
        export_results(students, courses)
        export_summary_txt(students, courses, fulfilled_wishes, unfulfilled_students, total_wishes, max_students)
        
        # Berechne Statistiken
        total_fulfilled = sum(fulfilled_wishes.values())
        fulfillment_rate = (total_fulfilled / total_wishes * 100) if total_wishes > 0 else 0
        
        wishes_per_student = Counter()
        for student in students:
            num_fulfilled = len(student.fulfilled_wish_numbers)
            wishes_per_student[num_fulfilled] += 1
        
        students_without_wishes = [s for s in students if not s.fulfilled_wish_numbers]
        
        # Kursgrößen
        course_stats = []
        for course_name, course in sorted(courses.items()):
            total = course.get_total_students()
            t0 = course.get_students_in_timeslot(0)
            t1 = course.get_students_in_timeslot(1)
            t2 = course.get_students_in_timeslot(2)
            course_stats.append({
                'name': course_name,
                'total': total,
                'timeslot1': t0,
                'timeslot2': t1,
                'timeslot3': t2
            })
        
        course_stats.sort(key=lambda x: x['total'], reverse=True)
        avg_students = sum(c['total'] for c in course_stats) / len(course_stats) if course_stats else 0
        
        return jsonify({
            'success': True,
            'stats': {
                'studentCount': len(students),
                'courseCount': len(courses),
                'totalWishes': total_wishes,
                'fulfilledWishes': total_fulfilled,
                'fulfillmentRate': round(fulfillment_rate, 1),
                'wishPriorities': {str(k): v for k, v in fulfilled_wishes.items()},
                'wishesPerStudent': {str(k): v for k, v in wishes_per_student.items()},
                'studentsWithoutWishes': len(students_without_wishes),
                'averageCourseSize': round(avg_students, 1),
                'courseStats': course_stats[:10]  # Top 10 Kurse
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/download/<filename>')
def download(filename):
    """Download generierter Dateien"""
    allowed_files = ['zuteilung_schueler.csv', 'zuteilung_kurse.csv', 'zusammenfassung.txt']
    
    if filename not in allowed_files:
        return jsonify({'error': 'File not found'}), 404
    
    file_path = os.path.join(SCRIPT_DIR, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not generated yet'}), 404
    
    return send_file(file_path, as_attachment=True)

@app.route('/api/clear', methods=['POST'])
def clear_data():
    """Löscht die temporären Daten aus dem RAM"""
    current_data['students'] = None
    current_data['courses'] = None
    current_data['filename'] = None
    
    return jsonify({
        'success': True,
        'message': 'Daten wurden aus dem Speicher gelöscht'
    })

if __name__ == '__main__':
    print("="*80)
    print("🚀 Methodentag Kurszuteilung - Web Interface")
    print("="*80)
    print("\n📊 Datenverarbeitung: Alle hochgeladenen Daten werden NUR im RAM gespeichert")
    print("🔒 Sicherheit: Keine persistente Speicherung auf der Festplatte")
    print("🌐 Server läuft auf: http://localhost:5000")
    print("\n" + "="*80 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
