#!/usr/bin/env python3
import os
import json
import glob


def count_tests(results_dir):
    passed = failed = skipped = broken = 0

    pattern = os.path.join(results_dir, "**", "*.json")
    for json_file in glob.glob(pattern, recursive=True):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                status = data.get('status', '')
                if status == 'passed':
                    passed += 1
                elif status == 'failed':
                    failed += 1
                elif status == 'skipped':
                    skipped += 1
                elif status == 'broken':
                    broken += 1
        except Exception as e:
            continue

    return passed, failed, skipped, broken


def create_bar(percent):
    bars = percent // 10
    spaces = 10 - bars
    bar = "[" + "█" * bars + "-" * spaces + f"] {percent}%"
    return bar


def main():
    # Указываем путь к allure results (стандартный для Python)
    results_dir = "allure-results"

    # Если нет результатов, создаем пустые значения
    if not os.path.exists(results_dir):
        print("PASSED=0")
        print("FAILED=0")
        print("SKIPPED=0")
        print("BROKEN=0")
        print("TOTAL=0")
        print("PASSED_PERCENT=0")
        print("FAILED_PERCENT=0")
        print("SKIPPED_PERCENT=0")
        print("PASSED_BAR=[----------] 0%")
        print("FAILED_BAR=[----------] 0%")
        print("SKIPPED_BAR=[----------] 0%")
        return

    passed, failed, skipped, broken = count_tests(results_dir)
    total = passed + failed + skipped + broken

    # Расчет процентов
    if total > 0:
        passed_percent = (passed * 100) // total
        failed_percent = (failed * 100) // total
        skipped_percent = (skipped * 100) // total
    else:
        passed_percent = failed_percent = skipped_percent = 0

    # Вывод в формате для Jenkins
    print(f"PASSED={passed}")
    print(f"FAILED={failed}")
    print(f"SKIPPED={skipped}")
    print(f"BROKEN={broken}")
    print(f"TOTAL={total}")
    print(f"PASSED_PERCENT={passed_percent}")
    print(f"FAILED_PERCENT={failed_percent}")
    print(f"SKIPPED_PERCENT={skipped_percent}")
    print(f"PASSED_BAR={create_bar(passed_percent)}")
    print(f"FAILED_BAR={create_bar(failed_percent)}")
    print(f"SKIPPED_BAR={create_bar(skipped_percent)}")


if __name__ == "__main__":
    main()