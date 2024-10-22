import os
from bs4 import BeautifulSoup


async def main(_) -> dict:
    feed = []
    for i in os.listdir('./Feed/'):
        content = open(f'./Feed/{i}', encoding='UTF-8').read()
        f = BeautifulSoup(content, 'html.parser')
        try:
            feed += [{
                'title': f.title.get_text(),
                'datetime': f.find_all('datetime')[0].get_text(),
                'id': i.removesuffix('.html'),
                'content': content.split('<body>')[1].split('</body>')[0]
            }]
        except IndexError:
            pass
    return {'feed': feed}
