import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def restore_activities():
    yield
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert isinstance(payload["Chess Club"]["participants"], list)


def test_signup_for_activity():
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    response = client.post(
        f"/activities/{quote(activity)}/signup?email={quote(email)}"
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in activities[activity]["participants"]


def test_signup_duplicate_returns_400():
    activity = "Chess Club"
    email = activities[activity]["participants"][0]
    response = client.post(
        f"/activities/{quote(activity)}/signup?email={quote(email)}"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities[activity]["participants"].count(email) == 1


def test_unregister_participant():
    activity = "Chess Club"
    email = activities[activity]["participants"][0]
    response = client.delete(
        f"/activities/{quote(activity)}/signup?email={quote(email)}"
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity}"}
    assert email not in activities[activity]["participants"]
