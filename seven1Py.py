import xmltodict
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # радиус Земли в метрах
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    lon1_rad = math.radians(lon1)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Формула гаверсинусов
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def get_bench_type(tags):
    """Определить тип скамейки на основе тегов"""
    if not isinstance(tags, list):
        if isinstance(tags, dict):
            tags = [tags]
        else:
            return 'обычная'
    
    tags_dict = {}
    for tag in tags:
        if isinstance(tag, dict):
            tags_dict[tag.get('@k', '')] = tag.get('@v', '')
    
    if 'backrest' in tags_dict:
        if tags_dict['backrest'] == 'yes':
            return 'со спинкой'
        else:
            return 'без спинки'
    elif 'material' in tags_dict:
        return f"материал: {tags_dict['material']}"
    elif 'covered' in tags_dict and tags_dict['covered'] == 'yes':
        return 'под навесом'
    else:
        return 'обычная'

def analyze_osm_file(file_path):
    """Анализирует один OSM файл и возвращает статистику"""
    with open(file_path, 'r', encoding='utf-8') as file:
        xml_content = file.read()
    
    data = xmltodict.parse(xml_content)
    
    if 'osm' not in data:
        print(f"Неверный формат OSM файла: {file_path}")
        return None
    
    nodes = data['osm'].get('node', [])
    
    # Преобразуем в список, если это не список
    if isinstance(nodes, dict):
        nodes = [nodes]
    
    # Списки для хранения данных
    benches = []
    pharmacies = []
    bench_types = {}
    
    # 1. Собираем все скамейки и аптеки
    for node in nodes:
        tags = node.get('tag', [])
        
        # Проверяем, есть ли у узла теги
        if tags:
            # Скамейки
            bench_found = False
            bench_type = 'обычная'
            
            if isinstance(tags, dict):
                tags_list = [tags]
            else:
                tags_list = tags
            
            for tag in tags_list:
                # Ищем скамейки
                if tag.get('@k') == 'bench' and tag.get('@v') == 'yes':
                    bench_found = True
                    bench_type = get_bench_type(tags_list)
                
                # Ищем аптеки
                if tag.get('@k') == 'amenity' and tag.get('@v') == 'pharmacy':
                    pharmacies.append({
                        'id': node['@id'],
                        'lat': float(node['@lat']),
                        'lon': float(node['@lon'])
                    })
            
            if bench_found:
                benches.append({
                    'id': node['@id'],
                    'lat': float(node['@lat']),
                    'lon': float(node['@lon']),
                    'type': bench_type
                })
    
    # 2. Определяем типы скамеек и считаем их количество
    for bench in benches:
        bench_type = bench['type']
        bench_types[bench_type] = bench_types.get(bench_type, 0) + 1
    
    # 3. Ищем скамейки рядом с аптеками (в радиусе 100 метров)
    benches_near_pharmacies = 0
    for bench in benches:
        for pharmacy in pharmacies:
            distance = calculate_distance(
                bench['lat'], bench['lon'],
                pharmacy['lat'], pharmacy['lon']
            )
            if distance <= 100:  # 100 метров
                benches_near_pharmacies += 1
                break  # достаточно найти одну аптеку рядом
    
    return {
        'total_benches': len(benches),
        'bench_types': bench_types,
        'benches_near_pharmacies': benches_near_pharmacies,
        'total_pharmacies': len(pharmacies)
    }

def print_statistics(file_name, stats):
    """Выводит статистику для одного файла"""
    print(f"Файл: {file_name}")
    print(f"Общее количество скамеек: {stats['total_benches']}")
    print(f"Количество аптек: {stats['total_pharmacies']}")
    if stats['bench_types']:
        print("\nКоличество скамеек по типам:")
        for bench_type, count in stats['bench_types'].items():
            print(f"  {bench_type}: {count}")
    else:
        print("\nТипы скамеек не определены")
    
    print(f"\nСкамейки рядом с аптеками (в радиусе 100м): {stats['benches_near_pharmacies']}")
file_paths = ['2.osm', '2 - 2.osm']
    
all_stats = {}
    
for file_path in file_paths:
    try:
        print(f"\nАнализируем файл: {file_path}")
        stats = analyze_osm_file(file_path)
        if stats is not None:
            all_stats[file_path] = stats
            print_statistics(file_path, stats)
        else:
            print(f"Не удалось проанализировать файл: {file_path}")
    except FileNotFoundError:
        print(f"Файл не найден: {file_path}")
    except Exception as e:
        print(f"Ошибка при анализе файла {file_path}: {e}")
    
if len(all_stats) >= 2:
    print("Сравнение:")
    file1 = list(all_stats.keys())[0]
    file2 = list(all_stats.keys())[1]
    stats1 = all_stats[file1]
    stats2 = all_stats[file2] 
    print(f"\nОбщее количество скамеек:")
    print(f"  {file1}: {stats1['total_benches']}")
    print(f"  {file2}: {stats2['total_benches']}")
    print(f"  Разница: {abs(stats1['total_benches'] - stats2['total_benches'])}")

    print(f"\nСкамейки рядом с аптеками:")
    print(f"  {file1}: {stats1['benches_near_pharmacies']}")
    print(f"  {file2}: {stats2['benches_near_pharmacies']}")
    print(f"  Разница: {abs(stats1['benches_near_pharmacies'] - stats2['benches_near_pharmacies'])}")

