"""GitHub REST API and OAuth device flow, using only the standard library."""

import json
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.github.com"
DEVICE_CODE_URL = "https://github.com/login/device/code"
TOKEN_URL = "https://github.com/login/oauth/access_token"
SCOPE = "repo"


class GitHubError(Exception):
    pass


def _request(method, url, token=None, data=None, form=False):
    headers = {
        "Accept": "application/json",
        "User-Agent": "Gitta",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    body = None
    if data is not None:
        if form:
            body = urllib.parse.urlencode(data).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            body = json.dumps(data).encode()
            headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        try:
            parsed = json.loads(detail)
            msg = parsed.get("message", detail)
            for err in parsed.get("errors", []):
                if isinstance(err, dict) and err.get("message"):
                    msg += f" ({err['message']})"
        except ValueError:
            msg = detail
        raise GitHubError(f"GitHub svarade {exc.code}: {msg}") from exc
    except urllib.error.URLError as exc:
        raise GitHubError(f"Kunde inte nå GitHub (är du online?): {exc.reason}") from exc


def device_start(client_id):
    """Begin device flow. Returns dict with user_code, verification_uri, ..."""
    info = _request("POST", DEVICE_CODE_URL,
                    data={"client_id": client_id, "scope": SCOPE}, form=True)
    if "device_code" not in info:
        raise GitHubError(
            "GitHub godkände inte Client ID. Kontrollera att 'Enable Device "
            f"Flow' är ikryssat på OAuth-appen. ({info.get('error_description', info)})")
    return info


def device_poll(client_id, info, cancel):
    """Wait until the user approves. Returns the access token."""
    interval = int(info.get("interval", 5))
    deadline = time.time() + int(info.get("expires_in", 900))
    while time.time() < deadline:
        if cancel.wait(interval):
            raise GitHubError("Inloggningen avbröts.")
        res = _request("POST", TOKEN_URL, form=True, data={
            "client_id": client_id,
            "device_code": info["device_code"],
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        })
        if "access_token" in res:
            return res["access_token"]
        err = res.get("error")
        if err == "authorization_pending":
            continue
        if err == "slow_down":
            interval += 5
            continue
        if err == "expired_token":
            break
        if err == "access_denied":
            raise GitHubError("Du nekade åtkomst på GitHub.")
        raise GitHubError(res.get("error_description", str(res)))
    raise GitHubError("Koden gick ut. Starta inloggningen igen.")


def get_user(token):
    return _request("GET", f"{API}/user", token)


def list_repos(token):
    repos, page = [], 1
    while True:
        chunk = _request(
            "GET",
            f"{API}/user/repos?per_page=100&sort=updated&page={page}"
            "&affiliation=owner,collaborator,organization_member",
            token)
        repos.extend(chunk)
        if len(chunk) < 100:
            return repos
        page += 1


def get_readme(token, full_name):
    """Raw README text of a repository, or None if it has none."""
    req = urllib.request.Request(
        f"{API}/repos/{full_name}/readme",
        headers={"Accept": "application/vnd.github.raw+json", "User-Agent": "Gitta",
                 "Authorization": f"Bearer {token}",
                 "X-GitHub-Api-Version": "2022-11-28"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise GitHubError(f"GitHub svarade {exc.code} när README skulle hämtas.") from exc
    except urllib.error.URLError as exc:
        raise GitHubError(f"Kunde inte nå GitHub (är du online?): {exc.reason}") from exc


def create_repo(token, name, description, private):
    return _request("POST", f"{API}/user/repos", token, {
        "name": name,
        "description": description,
        "private": private,
        "auto_init": False,
    })
