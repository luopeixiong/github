# -*- coding: utf-8 -*-
import json

from scrapy import Spider, Request, Field
import scrapy
from scrapy_redis.spiders import RedisSpider


class UserItem(scrapy.Item):
    # define the fields for your item here like:
    id = Field()
    name = Field()
    avatar_url = Field()
    headline = Field()
    description = Field()
    url = Field()
    url_token = Field()
    gender = Field()
    cover_url = Field()
    type = Field()
    badge = Field()

    answer_count = Field()
    articles_count = Field()
    commercial_question_count = Field()
    favorite_count = Field()
    favorited_count = Field()
    follower_count = Field()
    following_columns_count = Field()
    following_count = Field()
    pins_count = Field()
    question_count = Field()
    thank_from_count = Field()
    thank_to_count = Field()
    thanked_count = Field()
    vote_from_count = Field()
    vote_to_count = Field()
    voteup_count = Field()
    following_favlists_count = Field()
    following_question_count = Field()
    following_topic_count = Field()
    marked_answers_count = Field()
    mutual_followees_count = Field()
    hosted_live_count = Field()
    participated_live_count = Field()

    locations = Field()
    educations = Field()
    employments = Field()


class ZhihuSpider(RedisSpider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    follows_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}'
    start_user = 'excited-vczh'
    user_query = 'locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,following_count,cover_url,following_topic_count,following_question_count,following_favlists_count,following_columns_count,answer_count,articles_count,pins_count,question_count,commercial_question_count,favorite_count,favorited_count,logs_count,marked_answers_count,marked_answers_text,message_thread_token,account_status,is_active,is_force_renamed,is_bind_sina,sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,thanked_count,description,hosted_live_count,participated_live_count,allow_message,industry_category,org_name,org_homepage,badge[?(type=best_answerer)].topics'
    follows_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
    followers_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    def start_requests(self):
        yield Request(self.user_url.format(user=self.start_user, include=self.user_query), self.parse_user)
        yield Request(self.follows_url.format(user=self.start_user, include=self.follows_query, limit=20, offset=0),
                      self.parse_follows)
        yield Request(self.followers_url.format(user=self.start_user, include=self.followers_query, limit=20, offset=0),
                      self.parse_followers)

    def parse_user(self, response):
        result = json.loads(response.text)
        item = UserItem()

        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item

        yield Request(
            self.follows_url.format(user=result.get('url_token'), include=self.follows_query, limit=20, offset=0),
            self.parse_follows)

        yield Request(
            self.followers_url.format(user=result.get('url_token'), include=self.followers_query, limit=20, offset=0),
            self.parse_followers)

    def parse_follows(self, response):
        results = json.loads(response.text)

        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'), include=self.user_query),
                              self.parse_user)

        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield Request(next_page,
                          self.parse_follows)

    def parse_followers(self, response):
        results = json.loads(response.text)

        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'), include=self.user_query),
                              self.parse_user)

        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield Request(next_page,
                          self.parse_followers)