import re

from django.test import TestCase
from django.test.client import Client

import common, forums, news

class testForum(TestCase):
    def testIndex(self):
        response = forums._index(None)
        self.assertIsInstance(response, dict)
        self.assertIn('categories', response)
        categories = response['categories']
        self.assertGreater(len(categories), 5)
        self.assertLess(len(categories), 100)

        for category in categories:
            for name in 'id name subCategories'.split():
                self.assertIn(name, category.__dict__)
            self.assertTrue(re.match('[0-9]+', category.id))
            for subCategory in category.subCategories:
                for name in 'id name description'.split():
                    self.assertIn(name, subCategory.__dict__)
                self.assertTrue(re.match('[0-9]+', subCategory.id))

        self.assertEqual(categories[0].name, 'Site Web')
        self.assertEqual(categories[0].subCategories[0].name, 'XHTML / CSS')

    def testCategory(self):
        response = forums._category(None, '122')
        self.assertIsInstance(response, dict)
        for name in 'topics page_ids page_id title'.split():
            self.assertIn(name, response)
        self.assertNotEqual(response['page_id'], None)
        self.assertIn(response['page_id'], response['page_ids'])
        self.assertEqual(len(response['page_id']), 4)

        topics = response['topics']
        self.assertIsInstance(topics, list)
        for topic in topics:
            for name in 'id title subtitle'.split():
                self.assertIn(name, topic.__dict__)
            self.assertNotEqual(topic.title, '')
            self.assertTrue(re.match('[0-9]+', topic.id))

    def testTopic(self):
        response = forums._topic(None, '632690')
        self.assertIsInstance(response, dict)
        for name in 'messages page_ids page_id topic_title'.split():
            self.assertIn(name, response)
        self.assertNotEqual(response['page_id'], None)
        self.assertIn(response['page_id'], response['page_ids'])
        self.assertEqual(response['page_id'], '1')
        messages = response['messages']
        self.assertIsInstance(messages, list)

        for message in messages:
            for name in 'author content'.split():
                self.assertIn(name, message.__dict__)
                self.assertIsInstance(message.author, common.Member)
                self.assertNotEqual(message.content, '')

class TestNews(TestCase):
    def testIndex(self):
        response = news._index(None)
        self.assertIsInstance(response, dict)
        self.assertIn('news_list', response)
        news_list = response['news_list']
        self.assertIsInstance(news_list, list)

        for news_item in news_list:
            for name in 'logo short id title'.split():
                self.assertIn(name, news_item.__dict__)
            self.assertTrue(re.match('[0-9]+', news_item.id))

            self.assertTrue(news_item.logo.startswith('http://uploads.siteduzero.com/'),
                            '\'%s\' does not start with http://uploads.siteduzero.com/' %
                            news_item.logo)

    def testShow(self):
        response = news._show(None, '37914')
        self.assertIsInstance(response, dict)
        for name in 'title contributors content'.split():
            self.assertIn(name, response)
        self.assertIsInstance(response['contributors'], list)
        for contributor in response['contributors']:
            self.assertIsInstance(contributor, common.Member)
        self.assertNotEqual(response['content'], '')

    def testShowComments(self):
        response = news._show_comments(None, '37914', '1')
        self.assertIsInstance(response, dict)
        for name in 'title page_id page_ids comments'.split():
            self.assertIn(name, response)
        self.assertIsInstance(response['comments'], list)
        for comment in response['comments']:
            for name in 'author posted_on content'.split():
                self.assertIn(name, response.__dict__)
            self.assertIsInstance(comment.author, common.Member)
            self.assertNotEqual(comment.content, '')
