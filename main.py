from bs4 import BeautifulSoup
import requests
import re
import optparse
import os 
from tqdm import tqdm

extensions = {
    'images': ['jpg', 'jpeg', 'png', 'gif', 'svg'],
    'videos': ['mp4', 'webm', 'mkv', 'flv', 'avi', 'mov'],
    'audio': ['mp3', 'wav', 'ogg', 'flac', 'aac'],
    'documents': ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'md'],
    'archives': ['zip', 'tar', 'tar.gz', 'rar', '7z', 'gz'],
    'executable': ['exe', 'msi'],
    'code': ['html', 'css', 'js', 'py', 'php', 'cpp', 'c', 'h', 'java', 'cs', 'go', 'rb', 'swift', 'sql', 'json']
}

def get_html(url):
    return requests.get(url).text

def get_soup(html):
    return BeautifulSoup(html, 'lxml')

def get_links(html: str):
    href = re.findall(r'href="(.+?)"', html)
    src = re.findall(r'src="(.+?)"', html)
    links = href + src
    return links

def filter_links(url: str, links: list):
    result = []
    for link in links:
        if link.startswith('/'):
            link = url + link
        for category in extensions:
           for ext in extensions[category]:
               if link.endswith(ext):
                   result.append({
                          'link': link,
                            'category': category
                   })
    return result 

def create_dir(path):
    paths = path.split('/')
    for i in range(1, len(paths)):
        if not os.path.exists('/'.join(paths[:i])):
            os.mkdir('/'.join(paths[:i])) 

def download_file(url, base_path, category):
    path = f'{base_path}/{category}/{url.split("/")[-1]}'
    if os.path.exists(path):
        return
    r = requests.get(url, stream=True)
    create_dir(path)
    if r.status_code == 200:
        with open(path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)

def main():
    parser = optparse.OptionParser('usage %prog -u <target url>')
    parser.add_option('-u', dest='url', type='string', help='specify target url')
    parser.add_option('-d', dest='depth', type='int', help='specify depth of crawling')
    parser.add_option('-o', dest='output', type='string', help='specify output folder')
    (options, args) = parser.parse_args()
    url = options.url
    base_url = '/'.join(url.split('/')[:3])
    print(f"Target url: {url}")

    html = get_html(url)
    links = get_links(html)
    len_before = len(links)
    links = filter_links(base_url, links)
    len_after = len(links)
    print(f"Found {len_before} links, {len_after} links after filtering")
    print(links)
    if options.output:
        base_path = options.output
    else:
        base_path = "output"
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    for link in tqdm(links):
        download_file(link['link'], base_path, link['category'])

if __name__ == '__main__':
    main()