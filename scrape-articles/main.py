import get_articles as g
import asyncio
import re

def main():
    pages = asyncio.run(g.list_all_pages(
        'Scientists',
        ['Scien', 'physic', 'biolog', 'geolog', 'paleontolog', 'archaeolog', 'chemist', 'astronom', 'cosmolog', 'ecolog', 'oceanograph', 'meteorolog', 'biochem', 'botan', 'zoolog']
        ))
    print(pages)
    print(len(pages))

    for page in pages:
        if re.search('Florence_Peebles', page):
            print('success!')


if __name__ == '__main__':
    main()
