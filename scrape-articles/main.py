import get_articles as g
import asyncio


# If this were a bigger project, I would spend more time
# choosing keywords.
SCIENCE_KEYWORDS = ['Scien', 'physic', 'biolog', 'geolog', 'paleontolog', 'archaeolog', 'chemist', 'astronom', 'cosmolog', 'ecolog', 'oceanograph', 'meteorolog', 'biochem', 'botan', 'zoolog']
MUSIC_KEYWORDS = ['music', 'sing', 'guitar', 'bass', 'brass', 'flaut', 'flute', 'string', 'instrument', 'ophone', 'pian', 'keyboard', 'funk', 'jazz', 'country', 'bluegrass', 'pop']


def main():
    scientist_pages = asyncio.run(g.list_all_pages(
        'Scientists',
        SCIENCE_KEYWORDS
    ))
    musician_pages = asyncio.run(g.list_all_pages(
        'Musicians',
        MUSIC_KEYWORDS
    ))


if __name__ == '__main__':
    main()
