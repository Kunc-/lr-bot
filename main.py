import time
import shelve
import xml.etree.ElementTree as etree
import urllib.request as url

import praw


def checkFeed(podcast):
    podcastXML = etree.fromstring(url.urlopen(podcast).read())
    item = podcastXML.findall('.//item')[0]
    returnList = {}
    for tagName in ["pubDate", "title", 'category']:
        try:
            returnList[tagName] = str(item.find(tagName).text.encode('utf-8'),'utf-8')
        except:
            returnList[tagName] = ""
    return returnList

'''
def cleanTags(text):
    try:
        toReturn = text.split('<p>', 1)[1].split('</p>')[0]
    except:
        toReturn = text.strip('<p>').strip('<\p>')
    return html.unescape(toReturn)
'''



bot = praw.Reddit("Ajani_vengeant's Limited Resources Podcast Scraper.")
bot.login('Bot_LR', 'MarshallBrianTom')

__waitTime__ = 300
previous = shelve.open("lastPosted")
rssFeeds = {'blog': "http://www.lrcast.com/feed/", 'lr': "http://limitedresources.libsyn.com/rss",
            'cr': 'http://constructedresources.libsyn.com/rss', '141': 'http://the1for1.libsyn.com/rss'}
sites = {'lr': "http://www.lrcast.com/", 'cr': 'http://www.crcast.com/', '141': 'http://www.the1for1.com/',
         'blog': "http://www.lrcast.com/"}
first = True

for x in rssFeeds:
    if not x in previous:
        previous[x] = ""

while True:
    if int(time.time()) % __waitTime__ == 0:
        for x in rssFeeds:
            last = checkFeed(rssFeeds[x])
            print(last)
            exception = False
            if x == 'blog' and 'podcasts' in last['category'].lower():
                exception = True
            if last['pubDate'] != previous[x] and not exception:
                urlConstruct = last['title'].split(' ')
                itConstruct = urlConstruct
                for y in itConstruct:
                    if y in ['-']:
                        urlConstruct.remove(y)
                try:
                    sub = bot.get_subreddit('lrcast')
                    post = sub.submit(last['title'], url=str(sites[x] + '-'.join(urlConstruct)))
                    post.set_flair('Episode')
                    if x == 'blog':
                        post.set_flair('Blog Post')
                    post.save()
                except praw.errors.AlreadySubmitted:
                    print("alreadySubmittedError")
                previous[x] = last['pubDate']
            else:
                print("No new updates.")
