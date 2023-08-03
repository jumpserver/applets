import sys

from app import AppletApplication


def main():
    base64_str = sys.argv[1]
    with AppletApplication(kwargs_str=base64_str) as app:
        app.start()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        raise e
