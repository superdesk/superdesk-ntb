import ntb


def get_mediatopics(article):
    return [
        s for s in article.get("subject", []) if s.get("scheme") == ntb.MEDIATOPICS_CV
    ]
