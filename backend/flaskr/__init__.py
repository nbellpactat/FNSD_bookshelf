import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Book

BOOKS_PER_SHELF = 8


#     If you do not update the endpoints, the lab will not work - of no fault of your API code! 
#   - Make sure for each route that you're thinking through when to abort and with which kind of error 
#   - If you change any of the response body keys, make sure you update the frontend to correspond. 

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/books')
    def get_books():
        books = Book.query.order_by(Book.id).all()
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 8
        end = start + 8

        formatted_books = [book.format() for book in books]

        return jsonify(
            {
                'success': True,
                'books': formatted_books[start:end],
                'total_books': len(books)
            }
        )

    @app.route('/books/<int:book_id>', methods=['DELETE', 'PATCH'])
    def alter_book(book_id):
        book = Book.query.filter(Book.id == book_id).one_or_none()
        if book is None:
            abort(404)
        else:
            if request.method == 'PATCH':
                book.rating = request.get_json()['rating']
                book.update()
                return jsonify(
                    {
                        'success': True
                    }
                )
            elif request.method == 'DELETE':
                book.delete()
                books = Book.query.all()
                formatted_books = [book.format() for book in books]
                return jsonify(
                    {
                        'success': True,
                        'deleted': book_id,
                        'books': formatted_books,
                        'total_books': len(formatted_books)
                    }
                )

    @app.route('/books', methods=['POST'])
    def create_book():
        book = Book(
            title=request.get_json()['title'],
            author=request.get_json()['author'],
            rating=request.get_json()['rating']
        )
        book.insert()
        books = Book.query.all()
        formatted_books = [book.format() for book in books]
        return jsonify(
            {
                'success': True,
                'created': book.id,
                'books': formatted_books,
                'total_books': len(formatted_books)
            }
        )

    return app
