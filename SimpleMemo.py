import json
import time
from operator import itemgetter


def import_memo():
    with open('data.json') as f:
        return json.load(f)


def export_memo(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2)


def get_quality_of_response():
    prompt = '\nPlease enter the number corresponds with your recall\n' \
             '\t5 - perfect response\n' \
             '\t4 - correct response after a hesitation\n' \
             '\t3 - correct response recalled with serious difficulty\n' \
             '\t2 - incorrect response; where the correct one seemed easy to recall\n' \
             '\t1 - incorrect response; the correct one remembered\n' \
             '\t0 - complete blackout.\n\n' \
             '>>> '
    response = int(input(prompt))
    return response


def update_ef(item, q):
    if item['e-factor'] < 1.3:
        item['e-factor'] = 1.3
    if q >= 3:
        item['e-factor'] = item['e-factor'] + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    else:
        item['repetition_done'] = 0


def get_time_interval(repetition_done, ef):
    if repetition_done == 0:
        return 86400  # 1 days
    elif repetition_done == 1:
        return 518400  # 6 days
    else:
        return get_time_interval(repetition_done - 1, ef) * ef


def new_entry(data, option):
    new_item = dict()
    new_item['created'] = time.time()
    new_item['time_left'] = 0
    new_item['e-factor'] = 2.5
    new_item['repetition_done'] = 0
    if option == 1:
        new_item['event'] = input('Please describe the event\n>>> ')
    if option == 2:
        new_item['question'] = input('Please enter the question\n>>> ')
        new_item['answer'] = input('Please enter the correct answer\n>>> ')
    data += [new_item]
    export_memo(data)


def reminder(data):
    rem = ''
    i = 0
    for i in range(len(data)):
        D=data[i]
        D['time_left'] = get_time_interval(D['repetition_done'], D['e-factor']) - time.time() + D['created']
        if D['time_left'] >= 5184000: #deleted after 2 months
            with open('deleted.txt', 'a') as f:
                f.write(str(D)+'\n')
            del data[i]
    data.sort(key=itemgetter('time_left'))
    for D in data:
        if D['time_left'] <= 0:
            if 'event' in D.keys():
                rem += str(i) + '. [event] ' + D['event'] + '\n'
            elif 'question' in D.keys():
                rem += str(i) + '. [question] ' + D['question'] + '\n'
        else:
            break
        i += 1
    if rem:
        print('Select any one to memorize:\n' + rem)
        response = int(input('\nSelect an item to memorize\n>>> '))
        if 'question' in data[response].keys():
            print('Correct answer: ' + data[response]['answer'])
        update_ef(data[response], get_quality_of_response())
        data[response]['repetition_done'] += 1
    else:
        print('Nothing to memorize.')
    export_memo(data)

def print_menu():
    prompt = '\nSimple Memo Menu\n' + \
             '=================\n' + \
             '\t1 - new event\n' + \
             '\t2 - new question\n' + \
             '\t3 - reminder\n' \
             '\t4 - print data\n' + \
             '\t0 - exit\n\n' + \
             '>>> '
    response = int(input(prompt))
    return response


def main():
    flag = True
    while flag:
        response = print_menu()
        data = import_memo()
        if response == 1:
            new_entry(data, response)
        elif response == 2:
            new_entry(data, response)
        elif response == 3:
            reminder(data)
        elif response == 4:
            print(json.dumps(import_memo(),indent=2))
        elif response == 0:
            flag = False


if __name__ == "__main__":
    main()
