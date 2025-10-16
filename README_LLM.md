# LLM Solver + Universal Adapter

Этот репозиторий расширен LLM‑солвером, который использует функции из `CallLLM.py`
для генерации поля `moves` и интегрируется с универсальным адаптером (`src/universal_adapter.py`).

## Установка

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Аутентификация Kaggle

```bash
export KAGGLE_USERNAME=ваш_логин
export KAGGLE_KEY=ваш_api_key
# либо файл ~/.kaggle/kaggle.json с правами 600
```

## Запуск: сборка сабмишна LLM‑солвером

```bash
python run_comp.py --competition cayley-py-444-cube \
  --puzzles /path/to/puzzles.csv --out submission.csv \
  --solver examples.llm_solver.solver:solve_row
```

### Отправка на Kaggle

```bash
python run_comp.py --competition cayley-py-444-cube \
  --puzzles /path/to/puzzles.csv --out submission.csv \
  --solver examples.llm_solver.solver:solve_row \
  --submit --message "llm universal"
```

## Как это работает

* `examples/llm_solver/solver.py` — функция `solve_row(row, cfg)` строит промпт на основе входной строки пазла
  и вызывает LLM через `CallLLM.py` (`llm_query`, `get_models_list`, `CONFIG`). Возвращает строку moves.
* Если LLM недоступен, можно установить `LLM_OFFLINE=1`, тогда солвер будет возвращать пустые строки.
* `src/comp_registry.py` определяет заголовки сабмишна и формат. Если конкурс требует другой столбец или joiner —
  обновите профиль в реестре, LLM‑солвер автоматически подхватит `cfg.move_joiner`.

## Тонкости
* Солвер принудительно просит модель выводить **только** строку с ходами.
* Любые кодовые блоки/объяснения очищаются парсером.
* В `requirements.txt` добавлены `g4f` и `kaggle`. Для Windows при необходимости установите системные зависимости.

## Отладка
* Чтобы быстро проверить сценарий без сети, создайте минимальный `puzzles.csv` c заголовками из нужного конкурса
  и запустите сборку с `LLM_OFFLINE=1` — получится валидный `submission.csv` с пустыми `moves`.
```bash
export LLM_OFFLINE=1
python run_comp.py --competition cayley-py-444-cube \
  --puzzles puzzles.csv --out submission.csv \
  --solver examples.llm_solver.solver:solve_row
```