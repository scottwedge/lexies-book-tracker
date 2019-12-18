# -*- encoding: utf-8

import sys

sys.path.append("src")

from lexies_library_log import app


if __name__ == '__main__':
    app.run(port=7000, debug=True)
