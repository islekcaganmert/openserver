from bs4 import BeautifulSoup
from openserver.Helpers.Report import report, DirectoryEscalation
from flask import Response


async def main(_, request) -> (Response, dict):
    if '/' in request.json['id']:
        report(DirectoryEscalation)
        return Response(status=403)
    content = open(f'./Feed/{request.json['id']}.html', encoding='UTF-8').read()
    f = BeautifulSoup(content, 'html.parser')
    try:
        return {
            'title': f.title.get_text(),
            'datetime': f.find_all('datetime')[0].get_text(),
            'id': request.json['id'],
            'content': content.split('<body>')[1].split('</body>')[0]
        }
    except IndexError:
        return {'title': '', 'datetime': '2000-01-01 12:00', 'id': '', 'content': ''}
