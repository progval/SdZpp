# -*- coding: utf8 -*-

import re

from django.test import TestCase
from django.test.client import Client

import common, forums, news, tutos

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
                self.assertIn(name, comment.__dict__)
            self.assertIsInstance(comment.author, common.Member)
            self.assertNotEqual(comment.content, '')

class TestTutos(TestCase):
    def testIndex(self):
        response = tutos._index(None)
        self.assertIsInstance(response, dict)
        self.assertIn('tutos', response)
        self.assertIsInstance(response['tutos'], list)

        for tuto in response['tutos']:
            for name in 'id name'.split():
                self.assertIn(name, tuto.__dict__)
            self.assertTrue(re.match('[0-9]+', tuto.id))
            self.assertNotEqual(tuto.name, '')
            for char in '<>':
                self.assertNotIn(char, tuto.name)

        self.assertEqual(response['tutos'][0].id, '361996')
        self.assertEqual(response['tutos'][0].name, 'Suivez le guide !')
        self.assertEqual(response['tutos'][1].id, '13666')
        self.assertEqual(response['tutos'][1].name, 'XHTML / CSS')

    def testListSubcategories(self):
        for id in ('3', '352', '67'):
            response = tutos._list_subcategories(None, id)
            self.assertIsInstance(response, dict)
            self.assertIn('categories', response)
            categories = response['categories']
            self.assertIsInstance(categories, list)

            for category in categories:
                for name in 'name mode id description'.split():
                    self.assertIn(name, category.__dict__)
                    self.assertIsInstance(getattr(category, name), str)

                    if id == '3' or \
                            (id == '352' and category.id not in ('141', '403', '404')) or \
                            (id == '67' and category.id == '210'):
                        self.assertEqual(category.mode, '1')
                    else:
                        self.assertEqual(category.mode, '2')

    def testListTutorials(self):
        response = tutos._list_tutorials(None, '196')
        self.assertIsInstance(response, dict)
        self.assertIn('tutorials', response)
        self.assertIsInstance(response['tutorials'], list)

        for tuto in response['tutorials']:
            for name in 'id name'.split():
                self.assertIn(name, tuto.__dict__)
            self.assertTrue(re.match('[0-9]+', tuto.id))
            self.assertNotEqual(tuto.name, '')
            for char in '<>':
                self.assertNotIn(char, tuto.name)

    def testViewMinituto(self):
        response = tutos._view(None, '33509')
        self.assertIsInstance(response, tuple)
        self.assertEqual(len(response), 2)
        mode, response = response
        self.assertEqual(mode, 'mini')
        self.assertIsInstance(response, dict)
        for name, value in {'title': 'Pratiques avanc\xc3\xa9es et m\xc3\xa9connues en Python',
                            'license': 'Creative Commons BY-SA'}.items():
            self.assertIn(name, response)
            self.assertEqual(response[name], value)
        for name, type in {'authors': common.Member,
                           'subparts': common.Empty}.items():
            self.assertIn(name, response)
            self.assertIsInstance(response[name], list)
            for item in response[name]:
                self.assertIsInstance(item, type)
        for name in 'intro content'.split():
            self.assertIn(name, response)
            self.assertIsInstance(response[name], str)
        self.assertIsInstance(response['authors'], list)
        self.assertTrue(response['intro'].startswith('Beaucoup de gens pensent maîtriser correctement le langage Python'))
        self.assertTrue(response['intro'].strip().endswith('Bonne lecture \xc3\xa0 vous.</div>'))
        content = response['content'].strip()
        self.assertTrue(content.startswith('<h2>'))
        self.assertTrue(content.endswith('<img src="http://img373.imageshack.us/img373/8651/pythonircio1.png" alt="Image utilisateur"/></a></div></div>'))
        self.assertEqual(response['subparts'][0].name, 'La fonction enumerate')

    def testViewBigtuto(self):
        response = tutos._view(None, '223267')
        self.assertIsInstance(response, tuple)
        self.assertEqual(len(response), 2)
        mode, response = response
        self.assertEqual(mode, 'big')
        self.assertIsInstance(response, dict)
        for name, value in {'title': 'Apprendre Python !',
                            'license': 'Creative Commons BY-NC-SA'}.items():
            self.assertIn(name, response)
            self.assertEqual(response[name], value)
        for name, type in {'authors': common.Member,
                           'subparts': common.Empty}.items():
            self.assertIn(name, response)
            self.assertIsInstance(response[name], list)
            for item in response[name]:
                self.assertIsInstance(item, type)
        for name in 'intro'.split():
            self.assertIn(name, response)
            self.assertIsInstance(response[name], str)
        self.assertIsInstance(response['authors'], list)
        self.assertTrue(response['intro'].startswith('Ce tutoriel a pour but de vous initier au langage de programmation Python.'))
        self.assertTrue(response['intro'].strip().endswith('<hr />'))
        self.assertEqual(response['subparts'][0].name, 'Introduction \xc3\xa0 Python')
