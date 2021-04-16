def flatten_dict(current, key, result):
    if isinstance(current, dict):
        for k in current:
            new_key = "{0}_{1}".format(key, k) if len(key) > 0 else k
            flatten_dict(current[k], new_key, result)
    else:
        result[key] = current

    return result


def flatten_seed(data):
    seed_list = []
    for key in data['keys']:
        if isinstance(key, dict):
            seed_result = flatten_dict(key, '', {})
            for key_name, key_values in seed_result.items():
                for key_value in key_values.split():
                    seed_list.append(key_name + '_' + key_value)
        else:
            seed_list.append(key)

    return seed_list


def summary_status(success_list, error_list, dry_run):
    print('\n')
    if dry_run:
        print('\n**** No changes have been made, dry-run only ****\n')
    print('Successful secrets')
    print('------------------')
    for success_item in success_list:
        print(success_item)

    print('\n\nUnsuccessful secrets')
    print('--------------------')
    for error_item in error_list:
        print(error_item)
