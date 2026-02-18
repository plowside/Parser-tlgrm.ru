THREADS = 5

PROXY = {
    # они не понадобились, поэтому поддержку для них не стал добавлять
    'enabled': False,
    'proxy': 'us.arxlabs.io:3010:k9tv104364-region-US:eqv79atl' # Если статичные в .txt, то указываешь .txt, а если резидентные, то просто сам прокси в одном из форматов вписываешь: ip:port:user:pass | user:pass@ip:port | ip:port
}

FILTERS = {
    "subscribers_minimum_count": 500 # Минимальное количество подписчиков (включительно)
}

SAVE_FORMATS = {
    'rewrite': True, # Удалять все предыдущие записи в .txt, если существуют

    'all_in_one': True, # Все категории в один файл
    'all_in_one_filename': 'parsed_categories.txt', # Название .txt с результатом

    'each_file_by_category': True, # Каждая категория в свой .txt записываться будет
    'each_file_by_category_directory': 'results_by_category', # Название папки с результатами
    'each_file_by_category_filename': '{category}.txt', # Название .txt с результатом
}

BY_LUCKYBANANA5894 = True