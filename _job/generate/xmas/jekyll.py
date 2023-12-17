from yaml import dump


def build_page(date, data, layout):
    front_matter = {
        "layout": layout,
        "data": data
    }

    return "---\n" + dump(front_matter) + "\n---\n\n"