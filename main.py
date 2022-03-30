import utils.scrape as scrape

def main():
    candidates = scrape.get_candidates()
    scrape.process_candidates(candidates)


if __name__ == "__main__":
    main()