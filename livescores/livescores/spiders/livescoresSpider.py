import scrapy
import itertools # used to remove lists of lists
from livescores.items import LivescoresItem
from scrapy.crawler import CrawlerProcess

# url for the main flashscores website (we're not scraping directly from this)
# links can be pasted to the end of this to pull out further info on the game in a web browser
fs_url = 'https://www.flashscore.co.uk'

# specify the leagues you want to scrape from
leagues_to_scrape = [
     'AFRICA: CAF Champions League',
     'BRAZIL: Campeonato Potiguar - First stage',
     'ENGLAND: Premier League',
     'GERMANY: 2. Bundesliga',
    'MOROCCO: Botola Pro'
]

class flashscoreSpider(scrapy.Spider):
    name = "flashscore"
    start_urls = ['https://m.flashscore.co.uk/?s=2']

    def parse(self, response):
        items = LivescoresItem()
        scores_xpath = "//div[@id = 'score-data']"
        core_xpath = response.xpath('//*[@id="score-data"]')

        scores = {}
        for cnt, h4 in enumerate(core_xpath.xpath('h4'), start=1):
            # pull our h4 tags (these contain the names of each league)
            key = h4.xpath('normalize-space()').get().strip()
            # if our league is in our list of leagues to scrape, pull data
            if key in leagues_to_scrape:
                # pull info on each team playing
                # to do this, we're using the knowledge that each team name is bounded by a span tag (which contains the match time)
                # if we pull all text between span tags, we can avoid having spaces (which are used when there has been a red card)
                # calculate how many span tags we've had so far (for the entire page)
                span_total_len = len(
                    response.xpath('//div[@id = "score-data"]/h4[$count]//preceding-sibling::span', count=cnt).getall()
                )
                # calc span tags in current header section we're looking at
                span_tags = core_xpath.xpath('//span[count(preceding-sibling::h4)=$count]',
                                                                          count=cnt)

                teams = []
                # pull out team names and use string to concatenate
                for count, span in enumerate(span_tags, start=1):
                    teams.append(core_xpath.xpath(
                            'string(//text()[count(preceding-sibling::span)=$count])',
                            count=count + span_total_len).getall())
                teams = list(itertools.chain(*teams))


                # pull game time
                game_time = core_xpath.xpath('span[count(preceding-sibling::h4)=$count]',
                                                                           count=cnt).xpath('.//text()').getall()
                # pull the current score
                livescores = core_xpath.xpath('a[count(preceding-sibling::h4)=$count]',
                                                                           count=cnt).xpath('.//text()').getall()
                # extract links for each game
                links = core_xpath.xpath('a[count(preceding-sibling::h4)=$count]',
                                                                      count=cnt).xpath('.//@href').getall()
                # match urls only give the end string so append
                links[:] = ["%s%s" % (fs_url, i) for i in links]
                # add our links to "items"
                links = links

                # save data to list
                scores[key] = {
                    'teams': teams,
                    'time': game_time,
                    'scores': livescores,
                    'links': links
                }
        yield scores


# Code to make script run like normal Python script
# process = CrawlerProcess()
# process.crawl(flashscore)
# process.start() # the script will block here untill the crawling is finished