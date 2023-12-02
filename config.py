from configparser import ConfigParser


def config(filename="database.ini", chapter="postgresql"):
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(chapter):
        params = parser.items(chapter)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} is not found in the {1} file.'.format(chapter, filename))
    return db
