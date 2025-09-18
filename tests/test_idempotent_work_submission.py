import json
import os
import pytest
from app import app, db
from models import PendingRequest
from utils.work_hash import compute_work_hash, canonicalize_work_json

@pytest.fixture(scope="module")
def test_client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
    client = app.test_client()
    yield client
    with app.app_context():
        db.drop_all()


def sample_work():
    return {
        "title": {
            "title": {"value": "Exemplo de Publicação"},
            "subtitle": {"value": "Um subtítulo"}
        },
        "journal-title": {"value": "Revista X"},
        "external-ids": {
            "external-id": [
                {
                    "external-id-type": "doi",
                    "external-id-value": "10.1234/exemplo12345",
                    "external-id-url": {"value": "https://doi.org/10.1234/exemplo123"},
                    "external-id-relationship": "self"
                }
            ]
        },
        "publication-date": {
            "year": {"value": "2025"},
            "month": {"value": "02"},
            "day": {"value": "11"}
        },
        "type": "journal-article"
    }


def test_hash_determinism():
    w1 = sample_work()
    w2 = sample_work()  # structurally identical
    assert canonicalize_work_json(w1) == canonicalize_work_json(w2)
    assert compute_work_hash(w1) == compute_work_hash(w2)


def test_different_hash_on_modified_field():
    w1 = sample_work()
    w2 = sample_work()
    w2['title']['subtitle']['value'] = 'Outro subtítulo'
    assert compute_work_hash(w1) != compute_work_hash(w2)


def test_prevent_duplicate_pending_requests(test_client):
    payload = {
        "author_email": "scielo_desenv@mailinator.com",
        "author_name": "Nome do Autor",
        "orcid_id": "0009-0000-5294-7018",
        "work_data": sample_work()
    }

    resp1 = test_client.post('/works', json=payload)
    assert resp1.status_code == 202
    data1 = resp1.get_json()
    assert data1['success'] is True
    first_request_id = data1['request_id']

    resp2 = test_client.post('/works', json=payload)
    assert resp2.status_code == 202
    data2 = resp2.get_json()
    assert data2['request_id'] == first_request_id
    assert 'Nenhuma nova autorização' in data2['message']

    with app.app_context():
        all_pending = PendingRequest.query.all()
        assert len(all_pending) == 1, "Somente uma pendência deve existir para payload idêntico"


def test_new_pending_when_work_changes(test_client):
    base = sample_work()
    payload1 = {
        "author_email": "autor2@mailinator.com",
        "author_name": "Autor 2",
        "orcid_id": "0009-0000-5294-7019",
        "work_data": base
    }
    resp1 = test_client.post('/works', json=payload1)
    assert resp1.status_code == 202
    r1 = resp1.get_json()['request_id']

    modified = sample_work()
    modified['title']['title']['value'] = 'Título Alterado'
    payload2 = {
        "author_email": "autor2@mailinator.com",
        "author_name": "Autor 2",
        "orcid_id": "0009-0000-5294-7019",
        "work_data": modified
    }
    resp2 = test_client.post('/works', json=payload2)
    assert resp2.status_code == 202
    r2 = resp2.get_json()['request_id']
    assert r1 != r2, "Uma nova pendência deve ser criada quando o trabalho muda"

    with app.app_context():
        pending_for_author = PendingRequest.query.filter_by(author_email='autor2@mailinator.com').all()
        assert len(pending_for_author) == 2
