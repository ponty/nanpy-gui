from mainwnd import BoardWrapper

# FORMAT = '%(asctime)-6s: %(name)s - %(levelname)s - %(message)s'
# logging.basicConfig(level=logging.DEBUG, format=FORMAT)


def main():
    BoardWrapper().configure_traits()


if __name__ == '__main__':
    main()
