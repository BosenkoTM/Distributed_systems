# parser.py - Интегрированная логика парсинга из оригинального проекта
import pandas as pd
import json
import copy
from typing import List, Dict

def process_file_to_jsonl(
    input_path: str, 
    output_path: str,
    target_level: str,
    augment: bool,
    aug_factor: int
) -> (int, int):
    """
    Читает, фильтрует, аугментирует (используя вариации) и конвертирует данные в JSONL.

    Args:
        input_path (str): Путь к входному файлу.
        output_path (str): Путь для сохранения выходного .jsonl файла.
        target_level (str): Уровень сложности для фильтрации ('Beginner', 'Автоматически', и т.д.).
        augment (bool): Флаг включения аугментации.
        aug_factor (int): Коэффициент увеличения (от 1 до 5).

    Returns:
        tuple[int, int]: (Количество исходных записей после фильтрации, Общее количество записей после аугментации)
    """
    try:
        if input_path.endswith('.xlsx'):
            df = pd.read_excel(input_path)
        elif input_path.endswith('.csv'):
            df = pd.read_csv(input_path)
        else:
            raise ValueError("Неподдерживаемый формат файла. Используйте .xlsx или .csv.")
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл не найден по пути: {input_path}")
    except Exception as e:
        raise ValueError(f"Ошибка при чтении файла: {e}")

    # Явно конвертируем колонку 'id', чтобы избежать ошибки сериализации numpy.int64.
    if 'id' in df.columns:
        df['id'] = df['id'].astype(int)
    
    # Замена NaN на пустые строки для корректной работы с данными
    df.fillna('', inplace=True)

    # Фильтрация по уровню сложности
    if target_level != "Автоматически":
        original_df = df[df['sql_complexity'].str.lower() == target_level.lower()]
    else:
        original_df = df
        
    initial_records_count = len(original_df)
    if initial_records_count == 0:
        return 0, 0

    base_records = original_df.to_dict('records')
    final_records = copy.deepcopy(base_records) # Начинаем с копии оригиналов

    # Логика осмысленной аугментации на основе вариаций
    if augment and aug_factor > 1:
        # Берем макс ID из всего исходного файла, чтобы новые ID были уникальны
        max_id = int(df['id'].max())
        new_id_counter = max_id + 1
        
        # Находим доступные вариации в файле
        variation_cols = sorted([col for col in df.columns if 'variation' in col])
        prompt_variations = sorted([p for p in variation_cols if 'prompt' in p])
        sql_variations = sorted([s for s in variation_cols if 'sql' in s])
        num_variations = min(len(prompt_variations), len(sql_variations))

        if num_variations > 0:
            augmented_records = []
            for _ in range(aug_factor - 1): # Создаем (N-1) порций новых записей
                for record in base_records:
                    # Циклически выбираем вариацию
                    variation_index = (len(augmented_records) % num_variations)
                    
                    new_prompt = record.get(prompt_variations[variation_index], "")
                    new_sql = record.get(sql_variations[variation_index], "")

                    # Создаем новую запись только если вариация не пустая
                    if new_prompt and new_sql:
                        new_record = copy.deepcopy(record)
                        new_record['id'] = new_id_counter
                        new_record['sql_prompt'] = new_prompt
                        new_record['sql'] = new_sql
                        # Добавляем пометку в объяснение для наглядности
                        new_record['sql_explanation'] += f" (Аугментация, вар. #{variation_index + 1})"
                        
                        augmented_records.append(new_record)
                        new_id_counter += 1
            
            final_records.extend(augmented_records)

    # Запись в JSONL
    with open(output_path, 'w', encoding='utf-8') as f:
        for record in final_records:
            # Убираем служебные колонки с вариациями из итогового JSON
            record_to_write = {k: v for k, v in record.items() if 'variation' not in k}
            json_string = json.dumps(record_to_write, ensure_ascii=False, separators=(',', ':'))
            f.write(json_string + '\n')
            
    total_processed_count = len(final_records)
    
    return initial_records_count, total_processed_count
