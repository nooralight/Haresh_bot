def is_sublist(sub, lst):
    """Check if sub is a sublist of lst."""
    n = len(sub)
    for i in range(len(lst) - n + 1):
        if lst[i:i+n] == sub:
            return i
    return -1

def split_list(main_list, sub_list):
    """Split main_list at the point where sub_list ends."""
    index = is_sublist(sub_list, main_list)
    if index != -1:
        new_list1 = main_list[:index]
        new_list2 = main_list[index + len(sub_list):]
        return new_list1 + sub_list, new_list2
    return main_list, []

def update_list(list1, list2):
    """Update list2 by checking for sublists from list1."""
    updated_list2 = []
    for item2 in list2:
        for item1 in list1:
            if is_sublist(item1, item2) != -1:
                part1, part2 = split_list(item2, item1)
                if part1:
                    updated_list2.append(part1)
                if part2:
                    updated_list2.append(part2)
                break
        else:
            updated_list2.append(item2)
    return updated_list2

# Example usage
list1 = [['21-02-2024', '22-02-2024', '23-02-2024'], ['01-03-2024', '02-03-2024', '03-03-2024'], ['12-04-2024', '13-04-2024', '14-04-2024']]
list2 = [['21-02-2024', '22-02-2024', '23-02-2024'], ['01-03-2024', '02-03-2024', '03-03-2024', '04-03-2024', '05-03-2024'], ['12-04-2024', '13-04-2024', '14-04-2024']]

updated_list2 = update_list(list1, list2)
print(updated_list2)
