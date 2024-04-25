


def number_to_letter(number):
    if 1 <= number <= 26:
        return chr(ord('A') + number - 1)
    else:
        return None


def prompt_generator(data_path):
    loader = data_loader(data_path)
    while True:
        try:
            label_to_idx = dict()
            queries, targets, candidates, candidate_labels = next(loader)

            assert len(candidates) == len(candidate_labels)
            assert len(queries) == len(targets)
            N = len(candidates)
            for query, target in zip(queries, targets):
                for candidate in candidates:
                    prompt = candidate + '\n' + query
        except StopIteration:
            break


def main():
    DATA_PATH = '../output/PMCOA_out.json'
    generator = prompt_generator(DATA_PATH)

    while True:
        prompt, target_idx = next(generator)
        print(prompt)
        print(target_idx)
        input("Press Enter to continue...\n\n")


if __name__ == "__main__":
    main()
