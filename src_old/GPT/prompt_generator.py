from src_old.utils.evaluate_load_data import data_loader


def prompt_generator(data_path):
    loader = data_loader(data_path)
    while True:
        try:
            label_to_idx = dict()
            queries, targets, candidates, candidate_labels = next(loader)
            prompt_prefix = 'There are multiple figure/table captions from a scientific paper:\n\n'

            assert len(candidates) == len(candidate_labels)
            N = len(candidates)
            for idx in range(N):
                prompt_prefix = prompt_prefix + "{}: {}\n".format(idx, candidates[idx])
                label_to_idx[candidate_labels[idx]] = idx

            prompt_prefix = prompt_prefix + ('\nThe following is a referencing sentence that referenced one '
                                             'figure/table above: \n\n')
            prompt_postfix = ('Your task is to select one caption from the captions given above that best matching'
                              'the referencing sentence.\n'
                              'Make sure you only generate the index of the caption without any additional text.\n')

            for query, target in zip(queries, targets):
                if target != 'None':
                    prompt = prompt_prefix + query + '\n' + prompt_postfix
                    target_idx = label_to_idx[target]
                    yield prompt, target_idx
        except StopIteration:
            break


def main():
    DATA_PATH = '../../output/PMCOA_out.json'
    generator = prompt_generator(DATA_PATH)

    while True:
        prompt, target_idx = next(generator)
        print(prompt)
        print(target_idx)
        input("Press Enter to continue...\n\n")


if __name__ == "__main__":
    main()
