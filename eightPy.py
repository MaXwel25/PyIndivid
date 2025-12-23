import csv
import re

def parse_score(score_str, min_score):
    if not score_str or score_str.strip() in ['-', '']:
        return None
    try:
        # Заменяем запятую на точку для корректного преобразования в float
        score_str_clean = score_str.strip().replace(',', '.')
        return float(score_str_clean)
    except ValueError:
        return None

def process_file(file_path, min_score):
    failed_attempts = []
    
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=',')
        header = next(reader)
        for row in reader:
            if row[0].startswith('Среднее по группе') or row[0].startswith('Общее среднее'):
                continue
            last_name = row[0].strip()
            first_name = row[1].strip()
            status = row[5].strip()
            score_str = row[9].strip() if len(row) > 9 else ''
            
            is_failed = False
            failure_reason = ""
            
            if status != 'Завершено':
                is_failed = True
                failure_reason = f"Тест не завершен (статус: '{status}')"
            elif status == 'Завершено':
                score = parse_score(score_str, min_score)
                if score is None:
                    pass
                elif score < min_score:
                    is_failed = True
                    failure_reason = f"Оценка {score}/{min_score*10 if min_score==6 else min_score} ниже проходного балла"
            if is_failed:
                score = parse_score(score_str, min_score)
                has_valid_score = score is not None
                failed_attempts.append({
                    'last_name': last_name,
                    'first_name': first_name,
                    'email': row[4].strip() if len(row) > 4 else '',
                    'status': status,
                    'score': score,
                    'score_str': score_str,
                    'has_valid_score': has_valid_score,
                    'failure_reason': failure_reason,
                    'duration': row[8].strip() if len(row) > 8 else 'N/A',
                    'start_date': row[6].strip() if len(row) > 6 else 'N/A',
                    'end_date': row[7].strip() if len(row) > 7 else 'N/A'
                })
    return failed_attempts

file_configs = [
    {'file': '2 - 1.csv', 'min_score': 6.0, 'max_score': 10.0},
    {'file': '2 - 2.csv', 'min_score': 60.0, 'max_score': 100.0}
]  
all_failed_attempts = []
for config in file_configs:
    file_path = config['file']
    min_score = config['min_score']
    max_score = config['max_score']
    print(f"Обработка файла: {file_path}")
    print(f"Проходной балл: {min_score}/{max_score}")
        
    try:
        failed_attempts = process_file(file_path, min_score)
            
        if failed_attempts:
            not_completed = [a for a in failed_attempts if a['status'] != 'Завершено']
            low_score = [a for a in failed_attempts if a['status'] == 'Завершено' and a['has_valid_score']]
            if not_completed:
                print(f"Тестов не завершено: {len(not_completed)}")
            if low_score:
                print(f"Тестов завершено с низкой оценкой: {len(low_score)}")
                
            print(f"Всего неудачных попыток: {len(failed_attempts)}")
            print()
            print("Список не прошедших тест:")
                
            for i, attempt in enumerate(failed_attempts, 1):
                print(f"{i}. Фамилия: {attempt['last_name']}")
                print(f"   Имя: {attempt['first_name']}")
                print(f"   Email: {attempt['email']}")
                print(f"   Статус: {attempt['status']}")
                    
                if attempt['status'] == 'Завершено':
                    if attempt['has_valid_score']:
                        print(f"   Оценка: {attempt['score']}/{max_score}")
                    else:
                        print(f"   Оценка: не определена ('{attempt['score_str']}')")
                    
                print(f"   Причина провала: {attempt['failure_reason']}")
                print(f"   Дата начала: {attempt['start_date']}")
                    
                if attempt['status'] == 'Завершено':
                    print(f"   Дата завершения: {attempt['end_date']}")
                    print(f"   Затраченное время: {attempt['duration']}")
                    
                # Добавляем в общий список
                all_failed_attempts.append({
                    'file': file_path,
                    **attempt
                })
        else:
            print(f"Неудачных попыток не найдено")
            
        print()
            
    except FileNotFoundError:
        print(f"Ошибка: Файл {file_path} не найден!")
        print()
    except Exception as e:
        print(f"Ошибка при обработке файла {file_path}: {str(e)}")
        print()
    
print(f"Всего неудачных попыток: {len(all_failed_attempts)}")
    
not_completed_total = [a for a in all_failed_attempts if a['status'] != 'Завершено']
low_score_total = [a for a in all_failed_attempts if a['status'] == 'Завершено' and a['has_valid_score']]
completed_no_score = [a for a in all_failed_attempts if a['status'] == 'Завершено' and not a['has_valid_score']]
    
print(f"  - Тестов не завершено: {len(not_completed_total)}")
print(f"  - Тестов завершено с низкой оценкой: {len(low_score_total)}")
if completed_no_score:
    print(f"  - Тестов завершено без оценки: {len(completed_no_score)}")
    
print()
print("Распределение по файлам:")
for config in file_configs:
    file_path = config['file']
    file_failed = [a for a in all_failed_attempts if a['file'] == file_path]
    if file_failed:
        file_not_completed = [a for a in file_failed if a['status'] != 'Завершено']
        file_low_score = [a for a in file_failed if a['status'] == 'Завершено' and a['has_valid_score']]
        print(f"  {file_path}: {len(file_failed)} неудачных попыток")
        if file_not_completed:
            print(f"    • Не завершено: {len(file_not_completed)}")
        if file_low_score:
            print(f"    • Низкая оценка: {len(file_low_score)}")
