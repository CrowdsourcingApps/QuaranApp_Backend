def find_two_largest_values_and_indexes(input_values_list: list[float]):
    if len(input_values_list) == 1:
        return 0, 0, input_values_list[0], input_values_list[0]

    largest_index = -1
    second_largest_index = -1
    largest = float('-inf')
    second_largest = float('-inf')

    for i, num in enumerate(input_values_list):
        if num > largest:
            second_largest = largest
            second_largest_index = largest_index

            largest = num
            largest_index = i
        elif num > second_largest:
            second_largest = num
            second_largest_index = i

    return largest_index, second_largest_index, largest, second_largest


def check_if_chunk_considered_incorrect(errors_by_reviewer_info: list[tuple]) -> bool:
    reviewers_considered_incorrect = 0
    for errors_by_reviewer in errors_by_reviewer_info:
        # errors dict is not empty
        if errors_by_reviewer[1]:
            reviewers_considered_incorrect += 1

    return reviewers_considered_incorrect / len(errors_by_reviewer_info) >= 0.5


def get_formatted_chunks_by_surah_count(
        surah_number_to_title_mapping: dict, chunks_by_surah_count: dict[str, dict]
) -> dict:
    chunks_by_surah_count = {
        surah_number_to_title_mapping[k]: {"count_by_riwayah": dict(v), "surah_number": k}
        for k, v in chunks_by_surah_count.items()
    }
    sorted_chunks_by_surah_counter = {
        k: chunks_by_surah_count[k]
        for k in sorted(
            chunks_by_surah_count,
            key=lambda x: sum(chunks_by_surah_count[x]["count_by_riwayah"].values()),
            reverse=True
        )
    }
    return sorted_chunks_by_surah_counter

