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
    first_work = sample_work()
    second_work = sample_work()
    assert canonicalize_work_json(first_work) == canonicalize_work_json(second_work)
    assert compute_work_hash(first_work) == compute_work_hash(second_work)


def test_different_hash_on_modified_field():
    first_work = sample_work()
    second_work = sample_work()
    second_work['title']['subtitle']['value'] = 'Outro subtítulo'
    assert compute_work_hash(first_work) != compute_work_hash(second_work)


def test_prevent_duplicate_pending_requests(test_client):
    payload = {
        "author_email": "scielo_desenv@mailinator.com",
        "author_name": "Nome do Autor",
        "orcid_id": "0009-0000-5294-7018",
        "work_data": sample_work()
    }

    first_response = test_client.post('/works', json=payload)
    assert first_response.status_code == 202
    data_obtained_by_first_response = first_response.get_json()
    assert data_obtained_by_first_response['success'] is True
    first_request_id = data_obtained_by_first_response['request_id']

    second_response = test_client.post('/works', json=payload)
    assert second_response.status_code == 202
    data_obtained_by_second_response = second_response.get_json()
    assert data_obtained_by_second_response['request_id'] == first_request_id
    assert 'Nenhuma nova autorização' in data_obtained_by_second_response['message']

    with app.app_context():
        all_pending = PendingRequest.query.all()
        assert len(all_pending) == 1, "Somente uma pendência deve existir para payload idêntico"


def test_new_pending_when_work_changes(test_client):
    base = sample_work()
    first_payload_example = {
        "author_email": "autor2@mailinator.com",
        "author_name": "Autor 2",
        "orcid_id": "0009-0000-5294-7019",
        "work_data": base
    }
    first_response = test_client.post('/works', json=first_payload_example)
    assert first_response.status_code == 202
    request_id_obtained_by_first_response = first_response.get_json()['request_id']

    modified = sample_work()
    modified['title']['title']['value'] = 'Título Alterado'
    second_payload_example = {
        "author_email": "autor2@mailinator.com",
        "author_name": "Autor 2",
        "orcid_id": "0009-0000-5294-7019",
        "work_data": modified
    }
    second_response = test_client.post('/works', json=second_payload_example)
    assert second_response.status_code == 202
    request_id_obtained_by_second_response = second_response.get_json()['request_id']
    assert request_id_obtained_by_first_response != request_id_obtained_by_second_response, "Uma nova pendência deve ser criada quando o trabalho muda"

    with app.app_context():
        pending_for_author = PendingRequest.query.filter_by(author_email='autor2@mailinator.com').all()
        assert len(pending_for_author) == 2
