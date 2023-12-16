from yaml import dump


def build_page(date, data):
    front_matter = {
        "layout": "viz",
        "data": data
    }

    return "---\n" + dump(front_matter) + "\n---\n\n"