import requests
from urllib.parse import urlencode
from socket import gaierror
from requests.exceptions import ConnectionError, RequestException
from bs4 import BeautifulSoup
import logging
import os
import argparse
from datetime import datetime
import re

# configure logger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# configure argument parser

current_year = datetime.now().year
parser = argparse.ArgumentParser(description='command line arguments')

# parser.add_argument('command', action='store', choices=['list', 'fetch'])

subparsers = parser.add_subparsers(help='Command to execute')
parser_list = subparsers.add_parser('list', help='List forms for numbers')
parser_list.set_defaults(command='list')
parser_list.add_argument('--numbers', nargs='+', dest='numbers', action='store', help='Form numbers to list',
                         required=True)
parser_fetch = subparsers.add_parser('fetch', help='Fetch documents for form number and years range')
parser_fetch.set_defaults(command='fetch')
parser_fetch.add_argument('--number', dest='number', action='store',
                    help='Form number to fetch, required when command is `fetch`', default=None, required=True)
parser_fetch.add_argument('--min_year', dest='min_year', action='store',
                    help='Min year to fetch, default is current year ({})'.format(current_year),
                    default=current_year, type=int)
parser_fetch.add_argument('--max_year', dest='max_year', action='store',
                    help='Max year to fetch, default is current year ({})'.format(current_year),
                    default=current_year, type=int)


# form numbers comparision

re_signs =  re.compile(r'[^a-z0-9]', re.IGNORECASE)


def equal(s1: str, s2: str) -> bool:
    '''compare form numbers without any non letters and non-numbers case insesetive '''
    s1 = re_signs.sub('', s1.lower())
    s2 = re_signs.sub('', s2.lower())
    return s1 == s2


class Parser:
    '''main parser class'''
    BASE_URL = 'https://apps.irs.gov/app/picklist/list/priorFormPublication.html'
    PER_PAGE = 200

    def __init(self):
        self.__session = None

    def __enter__(self):
        self.__session = requests.session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__session.close()

    def get(self, url, ret='soup'):
        logger.debug('Entering Parser.get')
        headers = {
            'accept':                    'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding':           'gzip, deflate, br',
            'accept-language':           'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control':             'max-age=0',
            'cookie':                    'JSESSIONID=Ns-Zw3FkKJef25nKEAl9eqdh.20; _ga=GA1.2.517263558.1617879206; _ga=GA1.3.517263558.1617879206; bm_sz=9487E5404061A520DE51A4B343E19B74~YAAQhpcwFzbe0q54AQAAFMv/tws6e+LV9ZGop/c7vg6rmRpdRRvFu3iIt+vSuQSCTN+Y0f6vBrmfnlzN66U/2xP0W2xCUPgkJe8IoOEB5kFMdaK3TYS4dy5kgSuJ9HOKfjQf56Q+GYn8J6LrRaNQXRa1GLiqMSLJySJXTIjQVGsjpInR/EmqVXE93Pg=; _abck=DAF4C679C30612D8B2CC9A0996789867~-1~YAAQhpcwFzfe0q54AQAAFMv/twVsMxooRdSb9uFxJfFzOeFuyJan3dfI1PFbkRAy2qDSg35LEwKxS/ByZ7sfJwS7bq9pxS6LvbvhWDs52H+7FMo1Eg0PBkfbSm/RVsaOVqs6No67WjS/DjrsGntBr4SNOdDo8GUr547pwdnyTjeSEXvUJg2vGaRovSVQih0uzNFCmO5WAYepRw/UyE9VVNKM6f9LtlXg2laYrGk2SNPo4/hSAstjNlvQrQmv/P52vT4aYhZSFBx2drck9E2szrTH0eoXbuVEmyKJpzfDhgj6ybRsYZ/eupsWC83nMBcaRjNSNOwA+riHGQES9T3Ii+a/fRyky4o+B746ivV47I/p1iEG40uYTu+t0quBux0xOuqSdnKLuQ==~-1~-1~-1; _gid=GA1.2.106446141.1617994700; _gid=GA1.3.106446141.1617994700; AKA_A2=A; AWSALB=lxAODgV2Mv2lJ5uIYdTe2QJ/YYOTxhvxq3B5q9pCwRiPklu2m+Xde94SWAE0pnLP2bDv8W1RtK3OvjnadMCea+q4URj87pTf8l/8nxDtt1lOEspZJqrEEathR/Vvw/Lx9CnJtBkUHwHbYc3q3j13s69L4sB+u/MOuM/CvszVHq3NZApG822U/ADXMWnINw==; _gali=leftNavDiv',
            'sec-fetch-dest':            'document',
            'sec-fetch-mode':            'navigate',
            'sec-fetch-site':            'none',
            'sec-fetch-user':            '?1',
            'upgrade-insecure-requests': '1',
            'user-agent':                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
        }
        logger.debug(url)
        try:
            resp = self.__session.get(url, headers=headers)
        except [RequestException, ConnectionError, gaierror] as e:
            logger.critical('Failed with exception {}'.format(str(e)))
            exit(0)
        logger.debug(resp.status_code)
        if resp.status_code != 200:
            logger.critical('Failed with code {}'.format(resp.status_code))
            exit(0)
        if ret == 'soup':
            soup = BeautifulSoup(resp.content, 'html.parser')
            if not soup:
                logger.critical('Failed to parse')
                exit(0)
            return soup
        elif ret=='bin':
            return resp.content


    def get_page(self, search_value:str, pageid:int)->list:
        data = {
            'indexOfFirstRow': pageid * self.PER_PAGE,
            'sortColumn':      'sortOrder',
            'value':           search_value,
            'criteria':        'formNumber',
            'resultsPerPage': self.PER_PAGE,
            'isDescending':    'false',
        }
        soup = self.get(self.BASE_URL + '?' + urlencode(data))
        tag_table = soup.find('table', attrs={'class': 'picklist-dataTable'})
        if not tag_table:
            logger.debug('Failed with table.picklist-dataTable')
            return []
        page_data = []
        for tag_tr in tag_table.find_all('tr')[1:]:
            tds = tag_tr.find_all('td')
            url, number, title, date = [None]*4
            try:
                number, title, date = [tag_td.get_text(strip=True) for tag_td in tds]
                tag_a = tds[0].find('a')
                if tag_a:
                    url = tag_a.get('href')
                page_data.append((url, number, title, date))
            except (IndexError, ValueError):
                # skip "bad rows"
                continue
        return page_data

    def get_pages(self, search_value: str)->list:
        parsed_data = list()
        page_id = 0
        while True:
            page_data = self.get_page(search_value, page_id)
            if not page_data:
                break
            for x in page_data:
                if equal(x[1], search_value):
                    parsed_data.append(x)
            if len(page_data) < self.PER_PAGE:
                break
            page_id += 1
        return parsed_data

    def make_data_dict(self, parsed_data):
        data_dict = {
            'form_number':None,
            'form_title':None,
            'min_year': None,
            'max_year': None
        }
        for row in parsed_data:
            if not data_dict['form_number']:
                data_dict['form_number'] = row[1]
            if not data_dict['form_title']:
                data_dict['form_title'] = row[2]
            try:
                year = int(row[3])
            except ValueError:
                # just skip rows with invalid year
                logger.warning('Skipped bad year: {}'.format(row[3]))
                continue

            if not data_dict['min_year']:
                data_dict['min_year'] = year
            if not data_dict['max_year']:
                data_dict['max_year'] = year
            if data_dict['min_year']> year:
                data_dict['min_year'] = year
            if data_dict['max_year']< year:
                data_dict['max_year'] = year
        if not data_dict['form_number']:
            return None
        return data_dict

    def get_pages_response(self, search_values:list):
        response = []
        for search_value in search_values:
            parsed_data = p.get_pages(search_value)
            form_data = self.make_data_dict(parsed_data)
            if form_data:
                response.append(form_data)
        return response

    def get_docs(self, search_value: str, min_year:int, max_year: int):
        parsed_data = self.get_pages(search_value)
        file_counter = 0
        for row in parsed_data:
            try:
                year = int(row[3])
            except ValueError:
                # just skip rows with invalid year
                logger.warning('Skipped bad year: {}'.format(row[3]))
                continue
            if not min_year<=year<= max_year:
                continue
            logger.debug('Fetching {}'.format(row[0]))
            dir_path = os.path.join('data', search_value)
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path, 0o777)
            file_data = self.get(row[0], 'bin')
            _, ext  = os.path.splitext(row[0])
            if not ext:
                ext = '.bin'
            file_name = os.path.join(dir_path, str(year) + ext)
            with open(file_name, 'wb') as file:
                file.write(file_data)
                file_counter += 1
        if file_counter>0:
            print('{} files were fetched into "{}"'.format(file_counter, dir_path))
        else:
            print('nothing were fetched')


if __name__=='__main__':
    args = parser.parse_args()
    if args.command == 'list':
        with Parser() as p:
            response = p.get_pages_response(args.numbers)
            print(response)
    if args.command == 'fetch':
        with Parser() as p:
            p.get_docs(args.number, args.min_year, args.max_year)

