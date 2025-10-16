# perm-llm-starter

Мини-репозиторий для экспериментов по пунктам:
1) Простые задачи сортировки перестановок с набором мувов «как bubble + один циклический».  
2) «Слабый, но частый» сигнал качества: Success@N, ΔKendallTau, ΔInversions.  
3) Точка входа для human-in-the-loop — можно добавлять хинты и кандидатов.

## Быстрый старт

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# запустить baseline и пример кандидата на задаче cyclic-coxeter (n=16, r=3)
python run.py --task cyclic-coxeter-n16-r3 --splits fast --candidates baseline heuristic1
```

Вывод покажет метрики на сплите `fast`. Для `control` используйте `--splits control` или оба через `--splits fast control`.

## Структура
```
src/
  tasks.py          — Task, Moveset, спецификация мувов
  movesets.py       — реализация мувов: bubble (adjacent swap), cyclic_coxeter(r)
  baselines.py      — bubble-sort baseline (использует только adjacent swap)
  metrics.py        — Success@N, Kendall tau, inversии
  generators.py     — генерация сплитов: случайные и структурные перестановки
  evaluator.py      — прогон кандидатов, подсчёт метрик, отчёт
  registry.py       — реестр задач и кандидатов
examples/candidates/
  heuristic1.py     — пример эвристического кандидата
datasets/
  (автогенерируемые сплиты будут класться сюда при первом запуске)
tests/
  test_metrics.py
run.py              — CLI для прогонов
requirements.txt
```

## Интерфейс кандидата
Кандидат — это функция `solve(p, moveset, budget)`,
которая возвращает **список мувов** (каждый — tuple, совместимый с moveset),
которые следует применить к копии перестановки `p` (0..n-1) и не превышают `budget` по длине.
Пример см. в `examples/candidates/heuristic1.py`.

> Если хотите писать «алгоритм, который сам применяет мувы», верните пустой список и изменяйте копию `p` через `moveset.apply_inplace(...)` — но **строго** не более `budget` шагов. Evaluator проверит итог.

## Добавить свой кандидат
1) Создайте файл в `examples/candidates/my_algo.py` с функцией `solve(p, moveset, budget)`.
2) Зарегистрируйте его в `src/registry.py` (см. `register_candidate("my_algo", ...)`).
3) Запускайте: `python run.py --candidates my_algo`.

## Почему так
- Минимальные зависимости, чистый Python.
- Фиксированная модель данных и детерминированность для воспроизводимости.
- Легко вставить LLM-планировщик поверх: генерить файл-кандидат и прогонять через `evaluator`.


## Kaggle: Santa 2023 сабмишн через API

Этот репозиторий умеет собирать файл сабмишна `id,moves` и отправлять его в соревнование **Santa 2023**.

### Установка и аутентификация Kaggle API
```bash
pip install -r requirements.txt

# ЛЮБОЙ из вариантов аутентификации:
# A) Переменные окружения (до запуска Python):
export KAGGLE_USERNAME=your_username
export KAGGLE_KEY=your_key

# B) Файл ~/.kaggle/kaggle.json с содержимым:
# {"username":"your_username","key":"your_key"}
# и правами 0600
```

### Сборка сабмишна
Скачайте `puzzles.csv` из соревнования и положите куда удобно. Затем:
```bash
python run_santa.py --puzzles /path/to/puzzles.csv --out submission.csv
```

По умолчанию используется пример-«солвер», который возвращает пустую строку ходов (решит только уже решённые пазлы). 
Замените его на свой: реализуйте функцию `solve_row(row)->str` и передайте модуль:
```bash
python run_santa.py --puzzles puzzles.csv --out submission.csv \
  --solver examples.santa_solver.example_solver:solve_row
```

### Отправка на Kaggle
```bash
python run_santa.py --puzzles puzzles.csv --out submission.csv \
  --submit --message "my first API submit" --competition santa-2023
```

> Требуется установленный пакет `kaggle` и корректная аутентификация. API использует те же требования, что и CLI `kaggle competitions submit`.


## Универсальный сабмишн для CayleyPy-соревнований

Поддерживаются слаги (можете расширять `src/comp_registry.py`):
- `cayley-py-professor-tetraminx-solve-optimally`
- `cayleypy-christophers-jewel`
- `cayleypy-glushkov`
- `cayleypy-rapapport-m2`
- `cayley-py-megaminx`
- `CayleyPy-pancake`
- `cayleypy-reversals`
- `cayley-py-444-cube`
- `cayleypy-transposons`
- `cayleypy-ihes-cube`

### Формат
Большинство конкурсов этой серии принимают CSV `id,moves`. В `src/comp_registry.py` можно настроить отличия (имена колонок, разделитель токенов и т.п.).

### Сборка и отправка
```bash
# собрать сабмишн
python run_comp.py --competition cayley-py-444-cube --puzzles /path/to/puzzles.csv \
  --out submission.csv --solver examples.cayleypy_solver.baseline:solve_row

# сразу и отправить
python run_comp.py --competition cayley-py-444-cube --puzzles puzzles.csv \
  --out submission.csv --solver examples.cayleypy_solver.baseline:solve_row \
  --submit --message "first attempt"
```
Ваш солвер получает `(row, cfg)` и может возвращать:
- строку `moves`,
- список токенов (мы соединим через `cfg.move_joiner`, по умолчанию `"."`),
- словарь с ключом `cfg.moves_key` (по умолчанию `"moves"`).

Если конкретное соревнование требует другой заголовок/поля — поправьте запись в `REGISTRY` или создайте новую.
