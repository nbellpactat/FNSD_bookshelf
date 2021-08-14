import unittest
import os
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import db, cleanup_db, setup_db, Book


class BookshelfTestCase(unittest.TestCase):
    """
    This class represents the Bookshelf API test case
    """

    def setUp(self):
        """
        Executed before each test. Define test variables and initialize app here.
        :return: None
        """
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "bookshelf_test"  # Make sure this is different than 'production'
        self.database_path = "postgresql://postgres:postgres@localhost:5432/bookshelf_test"
        setup_db(self.app, self.database_path)

        # Create test data to use during the tests
        test_data = [
            {
                'title': 'The Fellowship of the Ring',
                'author': 'J.R.R. Tolkien',
                'rating': 3
            },
            {
                'title': 'The Two Towers',
                'author': 'J.R.R. Tolkien',
                'rating': 4
            },
            {
                'title': 'The Return of the King',
                'author': 'J.R.R. Tolkien',
                'rating': 5
            }
        ]

        self.new_book = {
            'title': 'The Road',
            'author': 'Cormac McCarthy',
            'rating': 5
        }

        self.bad_book = {
            'title': 'The War of Art'
        }

        # Add the test data to the database
        for i, book in enumerate(test_data):
            self.client().post('/books', json=test_data[i])

    def tearDown(self):
        """
        Executed after each test.
        :return: None
        """
        # Drop the database after each test to use the specific test data from setup
        cleanup_db(self.app, self.database_path)

    # GET method tests for /books endpoint
    def test_get_books(self):
        response = self.client().get('/books')
        data = json.loads(response.data)

        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['books']))
        self.assertTrue(data['total_books'])

    def test_get_books_404(self):
        # Reset the DB prior to running the test
        cleanup_db(self.app, self.database_path)
        setup_db(self.app, self.database_path)

        response = self.client().get('/books')

        # Tests
        self.assertEqual(response.status_code, 404)

    # POST method tests for /books endpoint
    def test_post_books(self):
        # Add the new book to the database
        response = self.client().post('/books', json=self.new_book)
        data = json.loads(response.data)

        # Validate the API response fields
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['books']))
        self.assertTrue(data['total_books'])

        # Validate the database
        db.session.close()
        book = Book.query.filter(Book.id == '4').one_or_none()
        # MAKE SURE YOU CLOSE THE DB SESSION AFTER ACCESSING THE DB OR IT'LL HANG FOREVERRRRRRRRR
        db.session.close()
        self.assertTrue(book.id, 4)

    def test_post_books_422(self):
        # Attempt adding an improper entry to the database
        response = self.client().post('/books', json=self.bad_book)

        self.assertEqual(response.status_code, 422)

    # PATCH method tests for /books/<int:book_id> endpoint
    def test_patch_book(self):
        # Modify the rating of id=1 to be 5
        response = self.client().patch('/books/1', json={'rating': 5})
        data = json.loads(response.data)

        # Validate the API response fields
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # Validate the update in the database
        book = Book.query.filter(Book.id == 1).one_or_none()
        # MAKE SURE YOU CLOSE THE DB SESSION AFTER ACCESSING THE DB OR IT'LL HANG FOREVERRRRRRRRR
        db.session.close()

        self.assertEqual(book.rating, 5)

    def test_patch_book_400(self):
        # Modify the wrong field of id=1 to trigger a 400
        response = self.client().patch('/books/1', json={'title': 5})

        self.assertEqual(response.status_code, 400)

    # DELETE method tests for /books/<int:book_id> endpoint
    def test_delete_book(self):
        # Delete book id=1
        response = self.client().delete('/book/1')
        data = json.loads(response.data)

        # Validate the API response fields
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['books']))
        self.assertTrue(data['total_books'])

        # Validate the database
        book = Book.query.filter(Book.id == data['deleted']).one_or_none()
        print(book)
        db.session.close()
        self.assertEqual(book, None)


if __name__ == "__main__":
    unittest.main()
