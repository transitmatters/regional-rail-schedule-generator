def get_triples(some_list):
    for index in range(len(some_list) - 2):
        yield some_list[index], some_list[index + 1], some_list[index + 2]


def get_pairs(some_list):
    for index in range(len(some_list) - 1):
        yield some_list[index], some_list[index + 1]
