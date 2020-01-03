# -*- encoding: utf-8

from src.models import Review


def test_can_store_and_retrieve_review(session, fake, book, user):
    review = Review(
        review_text=fake.text(), date_read=fake.date_object(), book=book, user=user,
    )
    session.add(review)

    session.commit()

    assert Review.query.get(review.id) == review


def test_default_review_date_is_empty(session, fake, book, user):
    review = Review(review_text=fake.text(), book=book, user=user)
    session.add(review)

    session.commit()

    assert review.date_read is None
    assert not review.did_not_finish
    assert not review.is_favourite


def test_can_review_a_book_multiple_times(session, fake, book, user):
    review1 = Review(review_text=fake.text(), book=book, user=user)
    review2 = Review(review_text=fake.text(), book=book, user=user)
    session.add(review1)
    session.add(review2)

    session.commit()


def test_can_create_review(session, fake, book, user):
    review = Review.create(
        review_text=fake.text(),
        date_read=fake.date_object(),
        did_not_finish=fake.boolean(),
        is_favourite=fake.boolean(),
        book=book,
        user=user,
    )

    assert Review.query.count() == 1
    assert Review.query.get(review.id) == review
