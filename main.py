from banki_ru import banki_parser
from rbc_parser import rbc_parser
from buh_ru import buh_ru_parser
from gartner_parser import gartner_parser
from lenta_ru import lenta_ru_parser
import sys
from datetime import date, datetime
import re
import os


def print_help():
    print(
        'HOW TO USE:\n'
        'first argument is for the portal you want to use, variants:\n'
        '--rbc - to use rbc.ru\n'
        '--lenta - to use lenta.ru\n'
        '--buhru - to use buh.ru\n'
        '--bankiru - to use banki.ru\n'
        '--gartner - to use gartner.com\n'
        '\nfor lenta, buhru and bankiru you also need to specify the start+end dates with -from *YYYY-mm-dd* and -to *YYYY-mm-dd*\n'
        'for gartner you also need to specify number of articles to scrap with -articles *number of articles*\n'
        'for all portals you shoud specify the output file name with -o *filename* otherwise it will be named *used portal name*.csv\n'
        'you can find all generated .csv files in data/\n'
        '\nEXAMPLE:\n'
        'python main.py --buhru -start 2022-10-01 -end 2022-10-07 -o buhru123.csv\n'
        )

def check_date_format(date_str):
    r = re.compile('20\\d{2}-\\d{2}-\\d{2}')
    if r.match(date_str) is not None:
        try:
            d = datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except:
            return False

def get_file_name_by_service(service_flag):
    file_dict = {
        '--bankiru': 'bankiru.csv',
        '--buhru': 'buhru.csv',
        '--lenta': 'lenta.csv'
    }
    return file_dict[service_flag]

def run_parser(args, file_path):
    print(f'starting {args[1][2:]} parser...')
    file_path = 'data/' + file_path
    if args[1] == '--rbc':
        rbc_parser.get_news(file_path)
    elif args[1] == '--gartner':
        gartner_parser.get_news(int(args[3]), file_path)
    else:
        from_ = datetime.strptime(args[3], '%Y-%m-%d').date()
        to_ = datetime.strptime(args[5], '%Y-%m-%d').date()
        if args[1] == '--buhru':
            buh_ru_parser.get_news(from_, to_, file_path)
        elif args[1] == '--bankiru':
            banki_parser.get_news(from_, to_, file_path)
        elif args[1] == '--lenta':
            lenta_ru_parser.get_news(from_, to_, file_path)
    print(f'done. you can look up your file at {file_path}')


def handle_input():
    if os.path.exists(os.path.join(os.getcwd(), 'data')) is False:
        os.mkdir('data')
    file_path = ''
    service = ''
    args = sys.argv
    portal_flags = ['--bankiru', '--buhru', '--lenta']
    if len(args) >= 2:
        if (args[1] == '--rbc') is True:
            file_path = 'rbc.csv'
            if (len(args) == 4 and args[2] == '-o' and args[3].endswith('.csv')) or (len(args) == 2):
                if len(args) == 4:
                    file_path = args[3]
                run_parser(args, file_path)
            else:
                print_help()
                return
        if args[1] == '--gartner':
            file_path = 'gartner.csv'
            if len(args) >= 4 and args[2] == '-articles' and args[3].isdigit():
                if len(args) == 6 and args[4] == '-o' and args[5].endswith('.csv'):
                    file_path = args[5]
                elif len(args) > 4 and (args[4] != '-o' or args[5].endswith('.csv') is not True):
                    print_help()
                    return
                run_parser(args, file_path)
            else:
                print_help()
                return
        elif args[1] in portal_flags:
            if len(args) >= 6 and args[2] == '-from' and check_date_format(args[3]) is True and args[4] == '-to' and check_date_format(args[5]) is True:
                file_path = get_file_name_by_service(args[1])
                if len(args) == 8 and args[6] == '-o' and args[7].endswith('.csv'):
                    file_path = args[7]
                elif len(args) != 6:
                    print_help()
                    return
                run_parser(args, file_path)
        else:
            print_help()
            return
        run_parser(args, file_path)
        return
    print_help()
    return

if __name__ == '__main__':
    handle_input()
                    
