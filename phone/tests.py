import re

from django.test import TestCase
from django.test.client import Client

import common, forums

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
