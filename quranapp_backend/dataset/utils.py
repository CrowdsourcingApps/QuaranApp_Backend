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
