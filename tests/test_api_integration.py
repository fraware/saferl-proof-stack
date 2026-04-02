from pathlib import Path
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from proofstack.api import app

client = TestClient(app)


def test_bundle_rejects_unknown_algorithm(tmp_path: Path):
    spec_file = tmp_path / "spec.yaml"
    spec_file.write_text(
        "environment: cartpole\ninvariants: ['x']\nguard: ['y']\nlemmas: []\n",
        encoding="utf-8",
    )
    with patch("proofstack.api.check_fireworks_key", return_value="key"):
        response = client.post(
            "/bundle",
            json={"spec_file": str(spec_file), "algorithm": "invalid"},
        )
    assert response.status_code == 422


def test_bundle_and_download_artifact(tmp_path: Path):
    spec_file = tmp_path / "spec.yaml"
    spec_file.write_text(
        "environment: cartpole\ninvariants: ['x']\nguard: ['y']\nlemmas: []\n",
        encoding="utf-8",
    )

    mock_bundle = Mock(path=str(tmp_path / "bundle"))
    bundle_dir = Path(mock_bundle.path)
    bundle_dir.mkdir()
    artifact = bundle_dir / "guard.c"
    artifact.write_text("int main(void){return 0;}", encoding="utf-8")

    with patch("proofstack.api.check_fireworks_key", return_value="key"), patch(
        "proofstack.api.ProofPipeline.run", return_value=mock_bundle
    ):
        response = client.post("/bundle", json={"spec_file": str(spec_file)})
        assert response.status_code == 200
        bundle_id = response.json()["bundle_id"]

        dl = client.get(f"/bundle/{bundle_id}", params={"artifact": "guard.c"})
        assert dl.status_code == 200
