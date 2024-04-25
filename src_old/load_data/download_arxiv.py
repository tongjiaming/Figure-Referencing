import json
import urllib, urllib.request
import xmltodict
import requests
import os
import time


def encode_query(title):
    # encode query for arxiv api search
    # https://info.arxiv.org/help/api/user-manual.html#51-details-of-query-construction
    title = title.replace(' ', '+')
    title = title.replace('(', '%28')
    title = title.replace(')', '%29')
    title = '%22' + title + '%22'
    return title


def download_and_save(url, folder_path):
    time.sleep(2)
    response = requests.get(url)

    if response.status_code == 200:
        content = response.content
        filename = url.split('/')[-1] + '.tar'
        file_path = os.path.join(folder_path, filename)

        with open(file_path, 'wb') as f:
            f.write(content)
    else:
        print("Failed to download content. Status code:", response.status_code)


def main():
    S2ORC_PATH = '../../output/S2ORC/s2orc_out.json'
    ARXIV_SAVE_PATH = '../../output/arxiv/'
    with open(S2ORC_PATH, encoding='utf-8') as file:
        for line in file:
            json_obj = json.loads(line)
            title = ascii(json_obj['paper_title'])
            title = encode_query(title)
            query_url = 'http://export.arxiv.org/api/query?search_query=ti:{}'.format(title)
            data = urllib.request.urlopen(query_url)
            response_dict = xmltodict.parse(data.read().decode('utf-8'))
            if 'entry' in response_dict['feed'] and not isinstance(response_dict['feed']['entry'], list):
                print('Downloading {}.'.format(json_obj['paper_title']))
                download_url = response_dict['feed']['entry']['id'].replace('abs', 'src_old')
                download_and_save(download_url, ARXIV_SAVE_PATH)


if __name__ == '__main__':
    main()
