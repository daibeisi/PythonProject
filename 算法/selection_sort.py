def selection_sort(nums: list[int]):
    for i in range(len(nums)):
        min_index = i
        for j in range(i + 1, len(nums)):
            if nums[j] < nums[min_index]:
                min_index = j
        nums[i], nums[min_index] = nums[min_index], nums[i]


if __name__ == '__main__':
    nums = [3, 5, 1, 2, 4]
    selection_sort(nums)
    print(nums)