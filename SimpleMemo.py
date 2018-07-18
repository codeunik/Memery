import json
import time
from operator import itemgetter

title = None
data = None
fields = []


def import_data():
    with open('data.json') as f:
        return json.load(f)


def export_data(data):
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


def card_title(*args):
    global title, data
    if title is None:
        title = input('Enter the title of the card(mandatory)\n>>> ')
        data = import_data()
        if title in data['cards']:
            print('This title already exists.\n')
            title = None
            card_title()
        else:
            print('Every card has a default field named "prompt".')
    else:
        print('You have already entered the card title')


def add_field(*args):
    global fields
    card_title()
    fields += [(input('Enter the new field\n>>> '))]


def delete_field(*args):
    global fields
    card_title()
    if len(fields) > 0:
        for i in range(len(fields)):
            print(str(i + 1) + '. ' + fields[i])
        del fields[int(input('Enter the field to delete\n>>> ')) - 1]
    else:
        print('Nothing to delete.')


def save_card(*args):
    global data, title, fields
    if title != None:
        data['cards'][title] = list(set(fields))
        data['memos'][title] = []
        export_data(data)
    title = None
    call_function(menu)

def show_cards(*args):
    global data
    data=import_data()
    i=1
    for k in data['cards'].keys():
        fields=''
        for field in data['cards'][k]:
            fields+=field+', '
        print(str(i)+'. Card Title: '+k+'\n '+' '*len(str(i))+'  Fields: prompt, '+fields+'\n')

def delete_card(*args):
    global data
    data = import_data()
    card_types = list(data['cards'].keys())
    if len(card_types) > 0:
        for i in range(len(card_types)):
            print(str(i + 1) + '. ' + card_types[i])
        chosen_type = int(input('Please chose a card type\n>>> ')) - 1
        del data['cards'][card_types[chosen_type]]
        export_data(data)
        data = import_data()
    else:
        print('Nothing to delete.')


def create_memo(*args):
    global data
    data = import_data()
    cards = list(data['cards'].keys())
    if len(cards)>0:
        for i in range(len(cards)):
            print(str(i + 1) + '. ' + cards[i])
        chosen_card = int(input('Please chose a card\n>>> ')) - 1
        title = cards[chosen_card]
        new_memo = dict()
        new_memo['created'] = time.time()
        new_memo['time_left'] = 0
        new_memo['e-factor'] = 2.5
        new_memo['repetition_done'] = 0
        new_memo['prompt'] = input('Please describe what is to be prompted\n>>> ')
        if len(data['cards'][title])>0:
            new_memo['custom'] = dict()
            for field in data['cards'][title]:
                new_memo['custom'][field] = input('Please write the ' + field + '\n>>> ')
        data['memos'][title] += [new_memo]
        export_data(data)
        data = import_data()
    else:
        print("There is no card. Please create a card first.")

def delete_memo(option):
    option1, option2 = 4,5
    global data
    data = import_data()
    memo_types = list(data['memos'].keys())
    if len(memo_types) > 0:
        for i in range(len(memo_types)):
            print(str(i + 1) + '. ' + memo_types[i])
        chosen_type = int(input('Please chose a type\n>>> ')) - 1
        if option == option1:
            memos = data['memos'][memo_types[chosen_type]]
            if len(memos) > 0:
                for i in range(len(memos)):
                    print(str(i + 1) + '. ' + memos[i]['prompt'])
                chosen_memo = int(input('Please chose a memo\n>>> ')) - 1
                del memos[chosen_memo]
                export_data(data)
                data = import_data()
            else:
                print('Nothing to delete.')
        elif option == option2:
            del data['memos'][memo_types[chosen_type]]
            export_data(data)
            data = import_data()
    else:
        print('Nothing to delete.')


def reminder(*args):
    global data
    data = import_data()

    memo_types = list(data['memos'].keys())
    for i in range(len(memo_types)):
        print(str(i + 1) + '. ' + memo_types[i])
    chosen_type = int(input('Please chose a type\n>>> ')) - 1
    memos = data['memos'][memo_types[chosen_type]]
    rem = ''
    for i in range(len(memos)):
        D = memos[i]
        D['time_left'] = get_time_interval(D['repetition_done'], D['e-factor']) - time.time() + D['created']
        if D['time_left'] >= 5184000:  # deleted after 2 months
            with open('deleted.txt', 'a') as f:
                f.write(str(D) + '\n')
            del memos[i]
    memos.sort(key=itemgetter('time_left'))
    i=0
    for D in memos:
        if D['time_left'] <= 0:
            rem += str(i + 1) + '. ' + D['prompt'] + '\n'
        else:
            break
        i += 1
    if rem:
        print('Select any one to memorize:\n' + rem)
        response = int(input('Select an item to memorize\n>>> ')) - 1
        if 'custom' in memos[response]:
            headings = memos[response]['custom']
            print('Please recall the fields: ', end='')
            for heading in headings:
                print(heading, end=', ')
            input()
            for heading in headings:
                print('\nCorrect ' + heading + ': ' + headings[heading])
        update_ef(memos[response], get_quality_of_response())
        memos[response]['repetition_done'] += 1
    else:
        print('Nothing to memorize.')
    export_data(data)


def call_function(menu):
    print('==============================')
    for i in range(len(menu)):
        print(str(i + 1) + '. ' + menu[i][0])
    print('==============================')
    response = int(input('>>> ')) - 1
    if type(menu[response][1]) == tuple:
        call_function(menu[response][1])
    else:
        menu[response][1](response)
        call_function(menu)


menu = (('create a memo', create_memo),
        ('reminder', reminder),
        ('create a new card', (('enter the card title', card_title),
                               ('add a new field', add_field),
                               ('delete a field', delete_field),
                               ('save', save_card))),
        ('show all cards',show_cards),
        ('delete a memo', delete_memo),
        ('delete all memos of a type', delete_memo),
        ('delete a card', delete_card),
        ('exit', exit))

if __name__ == "__main__":
    call_function(menu)
