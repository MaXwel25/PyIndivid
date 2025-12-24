import xmltodict
import math

def analyze_benches_in_osm(file_path):
    # Чтение и парсинг файла
    with open(file_path, 'r', encoding='utf-8') as fin:
        dct = xmltodict.parse(fin.read())
    # счетчики
    total_benches = 0
    bench_types = {}
    benches_near_pharmacies = 0
    
    # списки для координат
    benches = []
    pharmacies = []
    # функция расчета расстояния
    def distance(lat1, lon1, lat2, lon2):
        return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)
    # анализ каждого узла
    for node in dct['osm']['node']:
        # получаем теги узла
        tags = []
        if 'tag' in node:
            if isinstance(node['tag'], list):
                tags = node['tag']
            else:
                tags = [node['tag']]
        # проверяем на скамейку
        is_bench = False
        bench_type = None
        
        for tag in tags:
            if tag['@k'] == 'bench' and tag['@v'] == 'yes':
                is_bench = True
                total_benches += 1
                
                # Определяем тип
                for t in tags:
                    if t['@k'] == 'highway' and t['@v'] == 'bus_stop':
                        bench_type = 'Автобусная остановка'
                        break
                    elif t['@k'] == 'railway' and t['@v'] == 'tram_stop':
                        bench_type = 'Трамвайная остановка'
                        break
                
                if not bench_type:
                    bench_type = 'Прочая скамейка'
                
                # Сохраняем скамейку
                benches.append({
                    'id': node['@id'],
                    'lat': float(node['@lat']),
                    'lon': float(node['@lon']),
                    'type': bench_type
                })
                
                # Обновляем счетчик типов
                bench_types[bench_type] = bench_types.get(bench_type, 0) + 1
                break
        
        # Проверяем на аптеку
        for tag in tags:
            if tag['@k'] == 'amenity' and tag['@v'] == 'pharmacy':
                pharmacies.append({
                    'id': node['@id'],
                    'lat': float(node['@lat']),
                    'lon': float(node['@lon'])
                })
    
    # Проверяем скамейки рядом с аптеками
    for bench in benches:
        has_pharmacy = False
        for pharmacy in pharmacies:
            if distance(bench['lat'], bench['lon'], 
                       pharmacy['lat'], pharmacy['lon']) <= 0.001:
                has_pharmacy = True
                break
        
        if has_pharmacy:
            benches_near_pharmacies += 1
    
    # Вывод результатов
    print(f"Общее количество скамеек: {total_benches}")
    print(f"Количество скамеек каждого типа:")
    for bench_type, count in bench_types.items():
        print(f"  {bench_type}: {count}")
    print(f"Количество скамеек рядом с аптеками: {benches_near_pharmacies}")
    
    return {
        'total_benches': total_benches,
        'bench_types': bench_types,
        'benches_near_pharmacies': benches_near_pharmacies,
        'total_pharmacies': len(pharmacies)
    }

results = analyze_benches_in_osm('2.osm')
print(f"Всего аптек найдено: {results['total_pharmacies']}")
print("")
results = analyze_benches_in_osm('2 - 2.osm')
print(f"Всего аптек найдено: {results['total_pharmacies']}")
