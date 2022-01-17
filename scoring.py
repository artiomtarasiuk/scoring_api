import hashlib
import json

from storage import Storage


def get_key(
    phone,
    birthday=None,
    first_name=None,
    last_name=None,
) -> str:
    key_parts = [
        first_name or "",
        last_name or "",
        phone or "",
        birthday.strftime("%Y%m%d") if birthday is not None else "",
    ]
    return (
        "uid:"
        + hashlib.md5("".join([str(v) for v in key_parts]).encode("utf-8")).hexdigest()
    )


def get_score(
    store: Storage,
    phone,
    email,
    birthday=None,
    gender=None,
    first_name=None,
    last_name=None,
):
    key = get_key(phone, birthday, first_name, last_name)
    # try get from cache,
    # fallback to heavy calculation in case of cache miss
    score = store.cache_get(key) or 0
    if score:
        return float(score)
    if phone:
        score += 1.5
    if email:
        score += 1.5
    if birthday and gender:
        score += 1.5
    if first_name and last_name:
        score += 0.5
    # cache for 60 minutes
    store.cache_set(key, score, 60 * 60)
    return float(score)


def get_interests(store: Storage, cid):
    r = store.get("i:%s" % cid)
    return json.loads(r) if r else []
