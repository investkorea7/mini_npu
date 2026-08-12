# main.py
import json
import time

# --- [Step 1] MAC 연산 함수 ---
def calculate_mac(pattern, filter_grid, size):
    total_score = 0.0
    for row in range(size):
        for col in range(size):
            total_score += pattern[row][col] * filter_grid[row][col]
    return total_score


# --- [Step 2] 라벨 정규화 함수 ---
def normalize_label(label):
    clean_label = str(label).strip().lower()
    if clean_label in ['+', 'cross']:
        return 'Cross'
    elif clean_label in ['x']:
        return 'X'
    return label

def validate_matrix(matrix, expected_size):
    if not isinstance(matrix, list):
        return False

    if len(matrix) != expected_size:
        return False

    for row in matrix:
        if not isinstance(row, list):
            return False

        if len(row) != expected_size:
            return False

    return True

# --- [Step 3] 점수 비교 및 판정 함수 (Epsilon 정책) ---
def judge_pattern(score_cross, score_x):
    EPSILON = 1e-9
    diff = abs(score_cross - score_x)
    if diff < EPSILON:
        return "UNDECIDED"
    elif score_cross > score_x:
        return "Cross"
    else:
        return "X"


# --- [Step 4] 사용자 입력 받기 (모드 1) ---
def get_matrix_input(name, size=3):
    print(f"\n{name} ({size}줄 입력, 공백 구분)")
    while True:
        matrix = []
        error = False
        for i in range(size):
            line = input().strip()
            parts = line.split()
            if len(parts) != size:
                error = True
                break
            try:
                row = [float(x) for x in parts]
                matrix.append(row)
            except ValueError:
                error = True
                break
        
        if not error and len(matrix) == size:
            return matrix
        
        print(f"입력 형식 오류: 각 줄에 {size}개의 숫자를 공백으로 구분해 입력하세요. 다시 입력해 주세요.")


# --- [모드 1 실행] ---
def run_mode_1():
    print("\n#----------------------------------")
    print("# [1] 필터 입력")
    print("#----------------------------------")
    filter_a = get_matrix_input("필터 A", 3)
    filter_b = get_matrix_input("필터 B", 3)
    
    print("\n#----------------------------------")
    print("# [2] 패턴 입력")
    print("#----------------------------------")
    pattern = get_matrix_input("패턴", 3)
    
    # 10회 반복 측정
    start_time = time.perf_counter()
    for _ in range(10):
        score_a = calculate_mac(pattern, filter_a, 3)
        score_b = calculate_mac(pattern, filter_b, 3)
    end_time = time.perf_counter()
    
    avg_time_ms = ((end_time - start_time) / 10) * 1000
    
    diff = abs(score_a - score_b)
    if diff < 1e-9:
        judgment = "UNDECIDED"
    else:
        judgment = "A" if score_a > score_b else "B"
    
    print("\n#----------------------------------")
    print("# [3] MAC 결과")
    print("#----------------------------------")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(평균/10회): {avg_time_ms:.3f} ms")
    if judgment == "UNDECIDED":
        print("판정: 판정 불가 (|A-B| < 1e-9)")
    else:
        print(f"판정: {judgment}")


# --- [모드 2 실행] ---
def run_mode_2():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

    except FileNotFoundError:
        print("오류: data.json 파일을 찾을 수 없습니다.")
        return

    except json.JSONDecodeError:
        print("오류: data.json의 JSON 형식이 올바르지 않습니다.")
        return

    filters_data = data.get("filters", {})
    patterns_data = data.get("patterns", {})

    if not isinstance(filters_data, dict):
        print("오류: filters 데이터 형식이 올바르지 않습니다.")
        return

    if not isinstance(patterns_data, dict):
        print("오류: patterns 데이터 형식이 올바르지 않습니다.")
        return

    print("\n#----------------------------------")
    print("# [1] 필터 로드")
    print("#----------------------------------")
    loaded_filters = {}
    for size_key, f_dict in filters_data.items():
        if not isinstance(size_key, str) or not size_key.startswith("size_"):
            print(f"⚠ 필터 키 형식 오류: {size_key}")
            continue

        try:
            size_num = int(size_key.split("_")[1])
        except (IndexError, ValueError):
            print(f"⚠ 필터 크기 해석 실패: {size_key}")
            continue

        if not isinstance(f_dict, dict):
            print(f"⚠ {size_key} 필터 데이터 형식 오류")
            continue

        cross_f = f_dict.get("cross") or f_dict.get("Cross") or f_dict.get("+")
        x_f = f_dict.get("x") or f_dict.get("X")

        if cross_f is None or x_f is None:
            print(f"⚠ {size_key} 필터에 Cross 또는 X 데이터가 없습니다.")
            continue

        loaded_filters[size_num] = {
            "Cross": cross_f,
            "X": x_f
        }

        print(f"✓ {size_key} 필터 로드 완료 (Cross, X)")

    print("\n#----------------------------------")
    print("# [2] 패턴 분석 (라벨 정규화 적용)")
    print("#----------------------------------")
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    fail_details = []

    # 성능 측정용 자료구조
    time_records = {3: [], 5: [], 13: [], 25: []}

    for pat_key, pat_info in patterns_data.items():
        total_tests += 1

        if not isinstance(pat_key, str) or not pat_key.startswith("size_"):
            failed_tests += 1
            fail_details.append(f"- {pat_key}: 패턴 키 형식 오류로 FAIL")
            print(f"--- {pat_key}")
            print("판정: FAIL (패턴 키 형식 오류)")
            continue

        try:
            size_num = int(pat_key.split("_")[1])
        except (IndexError, ValueError):
            failed_tests += 1
            fail_details.append(f"- {pat_key}: 패턴 크기 해석 실패로 FAIL")
            print(f"--- {pat_key}")
            print("판정: FAIL (패턴 크기 해석 오류)")
            continue

        if not isinstance(pat_info, dict):
            failed_tests += 1
            fail_details.append(f"- {pat_key}: 패턴 데이터 형식 오류로 FAIL")
            print(f"--- {pat_key}")
            print("판정: FAIL (패턴 데이터 형식 오류)")
            continue

        pattern_grid = pat_info.get("input")
        raw_expected = pat_info.get("expected")
        expected_label = normalize_label(raw_expected)

        if expected_label not in ("Cross", "X"):
            failed_tests += 1
            fail_details.append(f"- {pat_key}: expected 라벨 오류로 FAIL")
            print(f"--- {pat_key}")
            print("판정: FAIL (expected 라벨 오류)")
            continue

                # 크기 및 데이터 검증
        if size_num not in loaded_filters:
            failed_tests += 1
            fail_details.append(f"- {pat_key}: 해당 크기의 필터가 없어 FAIL")
            print(f"--- {pat_key}")
            print("판정: FAIL (필터 없음)")
            continue

        cross_filter = loaded_filters[size_num]["Cross"]
        x_filter = loaded_filters[size_num]["X"]

        if not validate_matrix(pattern_grid, size_num):
            failed_tests += 1
            fail_details.append(
                f"- {pat_key}: 패턴 크기가 {size_num}x{size_num} 형식이 아니어서 FAIL"
            )
            print(f"--- {pat_key}")
            print(f"판정: FAIL (패턴 크기 오류: {size_num}x{size_num} 필요)")
            continue

        if not validate_matrix(cross_filter, size_num):
            failed_tests += 1
            fail_details.append(f"- {pat_key}: Cross 필터 크기 오류로 FAIL")
            print(f"--- {pat_key}")
            print("판정: FAIL (Cross 필터 크기 오류)")
            continue

        if not validate_matrix(x_filter, size_num):
            failed_tests += 1
            fail_details.append(f"- {pat_key}: X 필터 크기 오류로 FAIL")
            print(f"--- {pat_key}")
            print("판정: FAIL (X 필터 크기 오류)")
            continue
       
        # 연산 시간 측정 (MAC 1회 기준, 10회 평균)
        start_t = time.perf_counter()
        for _ in range(10):
            calculate_mac(pattern_grid, cross_filter, size_num)
        end_t = time.perf_counter()

        avg_ms = ((end_t - start_t) / 10) * 1000
        time_records[size_num].append(avg_ms)

        # 실제 판정용 점수 계산
        score_cross = calculate_mac(pattern_grid, cross_filter, size_num)
        score_x = calculate_mac(pattern_grid, x_filter, size_num)

        judgment = judge_pattern(score_cross, score_x)

        is_pass = (judgment == expected_label)
        if is_pass:
            passed_tests += 1
            status = "PASS"
        else:
            failed_tests += 1
            status = "FAIL"
            if judgment == "UNDECIDED":
                fail_details.append(f"- {pat_key}: 동점(UNDECIDED) 처리 규칙에 따라 FAIL")
            else:
                fail_details.append(f"- {pat_key}: 예상값({expected_label})과 판정값({judgment}) 불일치로 FAIL")

        print(f"--- {pat_key}")
        print(f"Cross 점수: {score_cross}")
        print(f"X 점수: {score_x}")
        print(f"판정: {judgment} | expected: {expected_label} | {status}")

    # Dummy 3x3 성능 측정 (성능 표 완성을 위함)
    dummy_3 = [[1]*3 for _ in range(3)]
    t0 = time.perf_counter()
    for _ in range(10):
        calculate_mac(dummy_3, dummy_3, 3)
    t1 = time.perf_counter()
    time_records[3].append(((t1 - t0) / 10) * 1000)

    print("\n#----------------------------------")
    print("# [3] 성능 분석 (평균/10회)")
    print("#----------------------------------")
    print(f"{'크기':<10} {'평균 시간(ms)':<15} {'연산 횟수(N^2)':<15}")
    for sz in [3, 5, 13, 25]:
        times = time_records[sz]
        avg_time = sum(times) / len(times) if times else 0.0
        n_sq = sz * sz
        print(f"{sz:<10} {avg_time:<15.3f} {n_sq:<15}")

    print("\n#----------------------------------")
    print("# [4] 결과 요약")
    print("#----------------------------------")
    print(f"총 테스트: {total_tests}개")
    print(f"통과: {passed_tests}개")
    print(f"실패: {failed_tests}개")
    if failed_tests > 0:
        print("실패 케이스:")
        for fd in fail_details:
            print(fd)


# --- 메인 메뉴 ---
if __name__ == "__main__":
    print("=== Mini NPU Simulator ===")
    print("[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    
    choice = input("선택: ").strip()
    if choice == "1":
        run_mode_1()
    elif choice == "2":
        run_mode_2()
    else:
        print("잘못된 입력입니다.")