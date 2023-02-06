
def get_rewrite_sequence(article) -> int:
    return int(article.get("rewrite_sequence") or 0)


def get_ntb_id(article) -> str:
    return "NTB{}".format(article["family_id"])


def get_doc_id(article) -> str:
    return "{ntb_id}_{version:02}".format(
        ntb_id=get_ntb_id(article),
        version=get_rewrite_sequence(article),
    )
